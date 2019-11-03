import os
import sys

import pandas as pd
import bs4
import requests as r
import nfl_macros as m
import openers_2 as of
from lxml import html
import requests
import nfl_helpers as h
import numpy as np
import nfl_pbp as p



# first function we need is one that grabs new game_ids for upcoming games and appends them to a csv containing that years prior games

def generate_urls():
	url = 'https://www.pro-football-reference.com/years/'
	weeks = ['week_1', 'week_2', 'week_3', 'week_4', 'week_5', 'week_6', 'week_7', 'week_8', 'week_9', 'week_10', 'week_11', 'week_12', 'week_13', 'week_14', 'week_15', 'week_16', 'week_17', 'weeek_18', 'week_19', 'week_20', 'week_21']
	weeks_short = ['week_1', 'week_2', 'week_3', 'week_4', 'week_5', 'week_6', 'week_7', 'week_8', 'week_9', 'week_10', 'week_11', 'week_12', 'week_13', 'week_14', 'week_15', 'week_16', 'week_17', 'weeek_18', 'week_19', 'week_20']
	urls = []
	newlinks = []
	newlinks2 = []
	for i in range(2019, 2020):
		if i >= 1990:
			for elt in weeks:
				url2 = url +  str(i) + '/' + str(elt) + '.htm'
				page = of.page(url2)
				links = page.find_all('td', {'class' : 'right gamelink'})
				# print(links)
				newlinks.append(links)

		for x in range(len(newlinks)):
			for i in range(len(newlinks[x])):
				real = newlinks[x][i].a['href']
				# print(real)
				newlinks2.append(real)
				# print(newlinks2)
	return newlinks2

# I don't know if this will be necessary, but we may need to erase the game_ids for games that are happening after the target day (for nfl after that given week)

def remove_unwanted_urls(boxes):
	# boxes = generate_urls()
	newboxes = []
	for x in range(len(boxes)):
		y1 = boxes[x][11]
		y2 = boxes[x][12]
		y3 = boxes[x][13]
		y4 = boxes[x][14]
		m1 = boxes[x][15]
		m2 = boxes[x][16]
		d1 = boxes[x][17]
		d2 = boxes[x][18]
		date = int(str(y1) + str(y2) + str(y3) + str(y4) + str(m1) + str(m2) + str(d1) + str(d2))
		# print(date)
		if date > 20191104: # change this number for the date that you want to target
			continue
		if date < 20191024:
			continue
		else:
			newboxes.append(boxes[x])

	# df = pd.DataFrame()
	# df['urls'] = newboxes
	# df.write_csv(fn='2019_boxes.csv')

	return newboxes

# second function needs to take in these ids and gather all the data we need for the games (this will gather game data for every game of that season up until that point! This will require multiple functions)

def scraper_main(start='201910240min', stop='201911040nyg'):
	data_root = '.' + m.data
	boxes = generate_urls()
	print(boxes)
	newboxes = remove_unwanted_urls(boxes)
	print(newboxes)
	df = pd.DataFrame()
	df['urls'] = newboxes
	df.write_csv(fn='2019_boxes.csv')
	df = open_csv('2019_boxes.csv')
	# print(df)
	df2 = df['urls'].tolist()
	last = '/boxscores/' + start + '.htm'
	index = df2.index(last)
	urls = df2[index:]

	write_header()

	for url in urls:
		# print(url)
		p = of.page(m.url + str(url))
		# print(p)
		fn_data = path_info_from_page(p, url)
		print(fn_data)
		if fn_data is None:
			return

		year, game_id = fn_data
		folder = 'pbp'
		path = data_root + folder

		# try:
		# 	int_year = int(year)
		# except ValueError:
		# 	print('skipping playoff game')
		# 	continue
		# try:
		# 	os.makedirs(path)
		# except FileExistsError:
		# 	print('file: {} exists'.format(game_id))
		# 	pass

		try:
			write_past_interior(path, page=p, game_id=game_id)
		except IndexError:
			write_future_interior(path, page=p, game_id=game_id)

	df2 = open_csv(fn='nfl_2019.csv')
	remove_crap(df2)
	df4 = open_csv(fn='nfl_history2.csv')
	turn_date_to_int(df2)
	df = pd.concat([df4,df2])
	df.write_csv(fn='nfl_history2.csv')
	df = open_csv(fn='nfl_history2.csv')
	# remove_crap(df)
	fix_total(df)
	turn_date_to_int(df)
	# print(df['Date'])
	assign_season(df)
	win(df)
	df.write_csv(fn=fn='nfl_history2.csv')
	df = fix_basic_train(df)
	df = fix_two_number_cols(df)
	df = set_cols_for_analysis(df)
	season_chunk = chunk_by_season(df)
	h_chunk = chunk_by_h(season_chunk)
	a_chunk = chunk_by_a(season_chunk)
	a_chunk = gen_a(a_chunk)
	h_chunk = gen_h(h_chunk)
	df2 = get_stats(a_chunk, h_chunk)
	df2 = home_away_stats(df2)
	print(df2)
	df2 = erase_cols(df2)
	print(df2)
	df2 = add_elos(df2)
	df2 = erase_rows(df2)
	print(df2)
	print(df2['a_team'])
	print(df2['h_team'])
	df3 = get_ml()
	# df3.write_csv(fn='nfl_week9_expanded.csv')
	fix_advanced_train(df3)
	df = open_csv(fn='nfl_history2.csv')
	df = df[df.Date <= 20191028]
	df.write_csv(fn='nfl_history2.csv')
	# dict1 = get_dict_of_df()
	# print(type(df3))
	# print(df3)
	# df4 = add_mls_to_main(df3)
	




def path_info_from_page(page, url):
	try:
		# week = page.strong.text.split(', ')
		year = url.split('/')
		year = year[2]
		y1 = year[0]
		y2 = year[1]
		y3 = year[2]
		y4 = year[3]
		year = int(str(y1) + str(y2) + str(y3) + str(y4))
		game_id = url.split('/')
		game_id = game_id[2]
	except IndexError:
		return None
	return year, game_id
		

def gen_stats(path, page=of.page(m.url + '/boxscores/201901200kan.htm'), game_id='201901200kan'):
	url = '/boxscores/201901200kan.htm'
	fn_data = path_info_from_page(page, url)
	year = fn_data[0]

	stats = page.find_all('div', {'class' : 'linescore_wrap'})
	number_of_q = stats[0].find_all('thead')
	number_of_q = number_of_q[0].find_all('th')
	number_of_q = [link.string for link in number_of_q]
	number_of_q = [int(elem) for elem in number_of_q if elem.isdigit()]
	number_of_q = [elem - 1 for elem in number_of_q]
	stats = stats[0].find_all('tbody')
	stats = stats[0].find_all('td', {'class' : 'center'})
	a_qs = stats[:len(stats)//2]
	h_qs = stats[len(stats)//2:]

	del a_qs[0]
	del h_qs[0]

	a_qs = [link.string for link in a_qs]
	h_qs = [link.string for link in h_qs]

	a_qs = [int(elem) for elem in a_qs if elem.isdigit()]
	h_qs = [int(elem) for elem in h_qs if elem.isdigit()]

	a_1st = a_qs[number_of_q[0]]
	a_2nd = a_qs[number_of_q[1]]
	a_3rd = a_qs[number_of_q[2]]
	a_4th = a_qs[number_of_q[3]]
	if len(number_of_q) == 5:
		a_5th = a_qs[number_of_q[4]]
	if len(number_of_q) == 4:
		a_5th = 0

	h_1st = h_qs[number_of_q[0]]
	h_2nd = h_qs[number_of_q[1]]
	h_3rd = h_qs[number_of_q[2]]
	h_4th = h_qs[number_of_q[3]]
	if len(number_of_q) == 5:
		h_5th = h_qs[number_of_q[4]]
	if len(number_of_q) == 4:
		h_5th = 0


	a_qs = [a_1st, a_2nd, a_3rd, a_4th, a_5th]
	h_qs = [h_1st, h_2nd, h_3rd, h_4th, h_5th]

	return a_qs, h_qs

def team_names(path, page=of.page(m.url + '/boxscores/201901200kan.htm'), game_id='201901200kan'):
	names = page.find_all('div', {'class' : 'scorebox'})
	names = names[0].find_all('strong')
	h_team = names[0].text
	h_team = h_team[1:]
	h_team = h_team[:-1]

	if len(names[1]) == 3:
		a_team = names[1].text
		a_team = a_team[1:]
		a_team = a_team[:-1]
	if len(names[1]) == 1:
		a_team = names[2].text
		a_team = a_team[1:]
		a_team = a_team[:-1]
	# else:
	# 	a_team = names[2].text
	# 	a_team = a_team[1:]
	# 	a_team = a_team[:-1]

	return (h_team, a_team)

def metas(path, page=of.page(m.url + '/boxscores/199101200buf.htm'), game_id='199101200buf'):

	y1 = game_id[0]
	y2 = game_id[1]
	y3 = game_id[2]
	y4 = game_id[3]
	year = int(str(y1) + str(y2) + str(y3) + str(y4))
	meta_data = [game_id] + [None for i in range(4)]
	meta = page.find('div', {'class' : 'scorebox_meta'})
	meta_divs = meta.find_all('div')

	Date = meta_divs[0].text.split(':')
	Start_time = meta_divs[1].text.split(':')
	Start_time = Start_time[1] + ':' +  Start_time[2]
	Venue = meta_divs[2].text.split(':')

	try:
		if year >= 1992:
			Attendance = meta_divs[3].text.split(':')
			Attendance = Attendance[1]

		else:
			NA = 'NA'
			Attendance = NA
	except IndexError:
		NA = 'NA'
		Attendance = NA


	meta_data[1] = Date[0]
	meta_data[2] = Start_time
	meta_data[3] = Venue[1]
	meta_data[4] = Attendance
	meta_data[4] = meta_data[4].replace(',', '')

	return meta_data

def bet_info(path, page=of.page(m.url + '/boxscores/199101200buf.htm'), game_id='199101200buf'):
	y1 = game_id[0]
	y2 = game_id[1]
	y3 = game_id[2]
	y4 = game_id[3]
	year = int(str(y1) + str(y2) + str(y3) + str(y4))
	cs = p.comments(page)

	# if int(year) == 2010:
	# info = cs[16]
	# else:
	info = cs[15]

	info = p.bs4_parse(info)
	info = info.find_all('tr')

	if len(info) == 7:
		spread = info[5]
		over_under = info[6]

	if len(info) == 6:
		spread = info[4]
		over_under = info[5]

	if len(info) == 5:
		spread = info[3]
		over_under = info[4]

	if len(info) == 8:
		spread = info[6]
		over_under = info[7]

	if len(info) == 4:
		spread = info[2]
		over_under = info[3]

	if len(info) == 9:
		spread = info[7]
		over_under = info[8]

	if len(info) == 10:
		spread = info[8]
		over_under = info[9]

	teams = team_names(path, page, game_id)
	spread = spread.find_all('td', {'class' : 'center'})
	over_under = over_under.text
	spread3 = spread[0].text.split('>')
	spread3 = spread3[0].split('-')
	name = spread3[0][:-1]
	over_under = [int(elem) for elem in over_under if elem.isdigit()]
	try:
		spread4 = spread3[1]
		over_under = int(str(over_under[0]) + str(over_under[1]))
	except IndexError:
		spread4 = 'NA'
		over_under = 'NA'
	if name == teams[0]:
		spread4 = '-' + spread4
	if name == teams[1]:
		spread4 = '+' + spread4

	bet_info = [spread4, over_under]

	return bet_info

def team_stats(path, page=of.page(m.url + '/boxscores/201901200kan.htm'), game_id='201901200kan'):
	y1 = game_id[0]
	y2 = game_id[1]
	y3 = game_id[2]
	y4 = game_id[3]
	year = int(str(y1) + str(y2) + str(y3) + str(y4))
	cs = p.comments(page)
	teams_stats = cs[21]

	team_stats = p.bs4_parse(teams_stats)
	team_stats = team_stats.find_all('tr')

	first_downs = team_stats[1].find_all('td', {'class' : 'center'})
	a_first_ds = first_downs[0]
	h_first_ds = first_downs[1]
	h_first_ds = [int(elem) for elem in h_first_ds if elem.isdigit()]
	a_first_ds = [int(elem) for elem in a_first_ds if elem.isdigit()]
	h_first_ds = h_first_ds[0]
	a_first_ds = a_first_ds[0]

	ryt = team_stats[2].find_all('td', {'class' : 'center'})
	ryt = [link.string for link in ryt]
	a_ryt = ryt[0]
	h_ryt = ryt[1]


	cayti = team_stats[3].find_all('td', {'class' : 'center'})
	cayti = [link.string for link in cayti]
	a_cayti = cayti[0]
	h_cayti = cayti[1]


	sacked_yards = team_stats[4].find_all('td', {'class' : 'center'})
	sy = [link.string for link in sacked_yards]
	a_sy = sy[0]
	h_sy = sy[1]


	npy = team_stats[5].find_all('td', {'class' : 'center'})
	a_npy = npy[0]
	h_npy = npy[1]
	h_npy = [int(elem) for elem in h_npy if elem.isdigit()]
	a_npy = [int(elem) for elem in a_npy if elem.isdigit()]
	try:
		h_npy = h_npy[0]
		a_npy = a_npy[0]
	except IndexError:
		h_npy = 0
		a_npy = 0

	ty = team_stats[6].find_all('td', {'class' : 'center'})
	a_ty = ty[0]
	h_ty = ty[1]
	h_ty = [int(elem) for elem in h_ty if elem.isdigit()]
	a_ty = [int(elem) for elem in a_ty if elem.isdigit()]
	h_ty = h_ty[0]
	a_ty = a_ty[0]

	fl = team_stats[7].find_all('td', {'class' : 'center'})
	fl = [link.string for link in fl]
	a_fl = fl[0]
	h_fl = fl[1]

	turnovers = team_stats[8].find_all('td', {'class' : 'center'})
	a_t = turnovers[0]
	h_t = turnovers[1]
	h_t = [int(elem) for elem in h_t if elem.isdigit()]
	a_t = [int(elem) for elem in a_t if elem.isdigit()]
	h_t = h_t[0]
	a_t = a_t[0]

	py = team_stats[9].find_all('td', {'class' : 'center'})
	py = [link.string for link in py]
	a_py = py[0]
	h_py = py[1]


	try:
		tdc = team_stats[10].find_all('td', {'class' : 'center'})
		tdc = [link.string for link in tdc]
		a_tdc = tdc[0]
		h_tdc = tdc[1]
	except IndexError:
		a_tdc = 0
		h_tdc = 0

	try:
		fdc = team_stats[11].find_all('td', {'class' : 'center'})
		fdc = [link.string for link in fdc]
		a_fdc = fdc[0]
		h_fdc = fdc[1]
	except IndexError:
		a_fdc = 0
		h_fdc = 0

	try:
		top = team_stats[12].find_all('td', {'class' : 'center'})
		top = [link.string for link in top]
		a_top = top[0]
		h_top = top[1]
	except IndexError:
		a_top = 0
		h_top = 0

	team_stats_h = [h_first_ds, h_ryt, h_cayti, h_sy, h_npy, h_ty, h_fl, h_t, h_py, h_tdc, h_fdc, h_top]
	team_stats_a = [a_first_ds, a_ryt, a_cayti, a_sy, a_npy, a_ty, a_fl, a_t, a_py, a_tdc, a_fdc, a_top]



	return team_stats_h, team_stats_a

def coaches(path, page=of.page(m.url + '/boxscores/201901200kan.htm'), game_id='201901200kan'):
	coaches = page.find_all('div', {'class' : 'datapoint'})
	coaches2 = []
	for coach in coaches:
		c = coach.find_all('a')
		d = c[0]['href']
		coaches2.append(d)

	if len(coaches2) == 1:
		coaches2.append('N/A')

	return coaches2

def write_past_interior(path, page=of.page(m.url + '/boxscores/199101200buf.htm'), game_id='199101200buf'):
	team_stat = team_stats(path, page, game_id)
	bet = bet_info(path, page, game_id)
	meta = metas(path, page, game_id)
	names = team_names(path, page, game_id)
	coach = coaches(path, page, game_id)
	points = gen_stats(path, page, game_id)

	fn = 'nfl_2019.csv'
	file = open(fn, 'a')

	for i, j in enumerate(meta):
		file.write(str(j))
		file.write(',')

	for i, j in enumerate(coach):
		file.write(str(j))
		file.write(',')

	for i, j in enumerate(names):
		file.write(str(j))
		file.write(',')
	
	for i, j in enumerate(points):
		file.write(str(j))
		file.write(',')
	
	for i, j in enumerate(team_stat): 
		file.write(str(j))
		file.write(',')

	for i, j in enumerate(bet):
		file.write(str(j))
		if i == len(bet) -1:
			file.write('\n')
		else:
			file.write(',')

def write_future_interior(path, page=of.page(m.url + '/boxscores/199101200buf.htm'), game_id='199101200buf'):
	coach = coaches(path, page, game_id)
	meta = metas(path, page, game_id)
	names = team_names(path, page, game_id)
	a_qs_none = [0, 0, 0, 0, 0]
	h_qs_none = [0, 0, 0, 0, 0]
	bet_none = [0, 0]
	teams_stats_none = [0, 0, 0, 0, 0, 0, 0, 
						0, 0, 0, 0, 0, 0, 0,
						0, 0, 0, 0, 0, 0, 0,
						0, 0, 0]
	fn = 'nfl_2019.csv'
	file = open(fn, 'a')

	for i, j in enumerate(meta):
		file.write(str(j))
		file.write(',')

	for i, j in enumerate(coach):
		file.write(str(j))
		file.write(',')

	for i, j in enumerate(names):
		file.write(str(j))
		file.write(',')
	
	for i, j in enumerate(a_qs_none):
		file.write(str(j))
		file.write(',')

	for i, j in enumerate(h_qs_none):
		file.write(str(j))
		file.write(',')
	
	for i, j in enumerate(teams_stats_none): 
		file.write(str(j))
		file.write(',')

	for i, j in enumerate(bet_none):
		file.write(str(j))
		if i == len(bet_none) -1:
			file.write('\n')
		else:
			file.write(',')

def write_header():
	fn = 'nfl_2019.csv'
	file = open(fn, 'w')

	columns = m.nfl_ref_lineup
	for i, j in enumerate(columns):
		file.write(str(j))
		if i == len(columns) -1:
			file.write('\n')
		else:
			file.write(',')

	file.close()


# third function needs to clean up the data we have gathered by removing brackets apostrophes and so on

# fourth function needs to perform some operations such as calculating who won the game and gaining a real date column


def get_baseline():
	df = open_csv(fn='nfl_history2.csv')
	# remove_crap(df)
	fix_total(df)
	turn_date_to_int(df)
	print(df['Date'])
	assign_season(df)
	win(df)
	# get_rid_of_zeros(df)


def remove_crap(df):
	columns = ['a_1stq', 'a_5thq', 'h_1stq', 'h_5thq', 'h_first_downs', 'h_rush_yds_tds', 
			   'h_comp_att_yd_td_int', 'h_sacked_yards',
			   'h_fumbles_lost', 'h_penalty_yards', 'h_top', 'a_first_downs', 'a_rush_yds_tds', 
			   'a_comp_att_yd_td_int', 'a_sacked_yards', 
			   'a_fumbles_lost', 'a_penalty_yards', 'a_top']

	for elt in columns:
		print(elt)
		ex = df[elt]
		ex = ex.tolist()
		for x in range(len(ex)):
			ex[x] = ex[x].replace('[', '')
			ex[x] = ex[x].replace(']', '')
			# print(elt)
			ex[x] = ex[x].replace("'", "")
			ex[x] = ex[x].replace(':', '')
		df[elt] = ex

	# for x in range(len(df)):
	stq = df['a_1stq']
	stq = stq.tolist()
	for x in range(len(stq)):
		stq[x] = int(stq[x])
	hstq = df['h_1stq']
	hstq = hstq.tolist()
	for x in range(len(hstq)):
		hstq[x] = int(hstq[x])
	thq = df['a_5thq']
	thq = thq.tolist()
	for x in range(len(thq)):
		thq[x] = int(thq[x])
	hthq = df['h_5thq']
	hthq = hthq.tolist()
	for x in range(len(hthq)):
		hthq[x] = int(hthq[x])

	df['a_1stq'] = stq
	df['h_1stq'] = hstq
	df['a_5thq'] = thq
	df['h_5thq'] = hthq

def fix_total(df):
	# df = open_csv('nfl_2019.csv') 
	df['h_total'] = df['h_1stq'] + df['h_2ndq'] + df['h_3rdq'] + df['h_4thq'] + df['h_5thq']
	df['a_total'] = df['a_1stq'] + df['a_2ndq'] + df['a_3rdq'] + df['a_4thq'] + df['a_5thq']
	df.write_csv(fn='nfl_2019.csv')


	return df

def turn_date_to_int(df):
	# df = open_csv('nfl_2019.csv') 
	newlist = df['Game_id']
	newlist = newlist.tolist()
	dates = []
	for elt in newlist:
		y1 = int(elt[0])
		y2 = int(elt[1])
		y3 = int(elt[2])
		y4 = int(elt[3])
		m1 = int(elt[4])
		m2 = int(elt[5])
		d1 = int(elt[6])
		d2 = int(elt[7])
		date = int(str(y1) + str(y2) + str(y3) + str(y4) + str(m1) + str(m2) + str(d1) + str(d2))
		dates.append(date)
	print(len(dates))
	# df = df.dropna(how='all')
	# df = df.sort_values('Date', ascending=True, na_position='first')
	df['Date'] = dates
	print(df['Date'])
	df.write_csv(fn='nfl_2019.csv')
# df['Date'] = dates
	# print(df['Date'])
	# df.write_csv(fn='nfl_2019.csv')


	return df

def assign_season(df):
	# df = open_csv('nfl_2019.csv')
	newlist = df['Game_id']
	newlist = newlist.tolist()
	seasons = []
	for elt in newlist:
		try:
			y1 = int(elt[0])
			y2 = int(elt[1])
			y3 = int(elt[2])
			y4 = int(elt[3])
			m1 = int(elt[4])
			m2 = int(elt[5])
		except TypeError:
			continue
		month = int(str(m1) + str(m2))
		print(month)
		year = int(str(y1) + str(y2) + str(y3) + str(y4))
		if month >= 9:
			season = year 
		if month < 9:
			season = year - 1
		seasons.append(season)
	df['Season'] = seasons

	return df

def win(df):
	# df = open_csv('nfl_2019.csv')
	hwin = []
	awin = []
	tie = []
	hsc = df['h_total']
	hsc = hsc.tolist()
	asc = df['a_total']
	asc = asc.tolist()
	for x in range(len(hsc)):
		if int(hsc[x]) > int(asc[x]):
			hwin.append(1)
			awin.append(0)
			tie.append(0)
		if int(asc[x]) > int(hsc[x]):
			hwin.append(0)
			awin.append(1)
			tie.append(0)
		if int(hsc[x]) == int(asc[x]):
			hwin.append(0)
			awin.append(0)
			tie.append(1)

	df['h_win'] = hwin
	df['a_win'] = awin
	df['h_tie'] = tie
	df['a_tie'] = tie

	return df

# def get_rid_of_zeros(df):
# columns = ['a_1stq', 'a_2ndq', 'a_3rdq', 'a_4thq', 'a_5thq', 'h_1stq', 'h_2ndq',
# 		   'h_3rdq', 'h_4thq', 'h_5thq', 'h_first_downs', 'h_rush_yds_tds',
# 		   'h_comp_att_yd_td_int', 'h_sacked_yards', 'h_net_pass_yards',
# 		   'h_total_yards', 'h_fumbles_lost', 'h_turnovers', 'h_penalty_yards',
# 		   'h_third_down_conv', 'h_fourth_down_conv', 'h_top', 'a_first_downs',
# 		   'a_rush_yds_tds', 'a_comp_att_yd_td_int', 'a_sacked_yards', 'a_net_pass_yards',
# 		   'a_total_yards', 'a_fumbles_lost', 'a_turnovers', 'a_penalty_yards', 'a_third_down_conv',
# 		   'a_fourth_down_conv', 'a_top', 'spread', 'over_under']

# 	for x in range(len(df)):
# 		if df.iloc[x][columns] == 0:
# 			print('boo')
# 			df.iloc[x][columns] = 'N/A'




# fifth function needs to go over the dataframe containing this seasons data and we need to calculate averages here (this will include multiple functions)

def stats_main():
	df = open_csv('nfl_2019.csv')
	df = fix_two_number_cols(df)
	df = set_cols_for_analysis(df)
	h_chunk = chunk_by_h(df)
	a_chunk = chunk_by_a(df)
	a_chunk = gen_a(a_chunk)
	h_chunk = gen_h(h_chunk)
	df2 = get_stats(a_chunk, h_chunk)
	df2 = home_away_stats(df2)
	df2 = erase_rows(df2)
	df2 = erase_cols(df2)

def fix_two_number_cols(df):
	df[['h_penalties', 'h_p_yards']] = df.h_penalty_yards.str.split('-',expand=True,)
	df[['h_fumbles', 'h_f_lost']] = df.h_fumbles_lost.str.split('-',expand=True,)
	df[['h_rush_attempts', 'h_rush_yards', 'h_rush_tds', 'h_none']] = df.h_rush_yds_tds.str.split('-',expand=True,)
	df[['h_sacks', 'h_sack_yards']] = df.h_sacked_yards.str.split('-',expand=True,)
	# df[['h_fourth_down_conversion', 'h_fourth_down_attempts']] = df.h_fourth_down_conv.str.split('-',expand=True,)
	# df[['h_third_down_conversion', 'h_third_down_attempts']] = df.h_third_down_conv.str.split('-',expand=True,)
	df[['h_completions', 'h_pass_attempts', 'h_pass_yards', 'h_pass_td', 'h_interceptions']] = df.h_comp_att_yd_td_int.str.split('-',expand=True,)
	df[['a_penalties', 'a_p_yards']] = df.a_penalty_yards.str.split('-',expand=True,)
	df[['a_fumbles', 'a_f_lost']] = df.a_fumbles_lost.str.split('-',expand=True,)
	df[['a_rush_attempts', 'a_rush_yards', 'a_rush_tds', 'a_none']] = df.a_rush_yds_tds.str.split('-',expand=True,)
	df[['a_sacks', 'a_sack_yards']] = df.a_sacked_yards.str.split('-',expand=True,)
	# df[['a_fourth_down_conversion', 'a_fourth_down_attempts']] = df.a_fourth_down_conv.str.split('-',expand=True,)
	# df[['a_third_down_conversion', 'a_third_down_attempts']] = df.a_third_down_conv.str.split('-',expand=True,)
	df[['a_completions', 'a_pass_attempts', 'a_pass_yards', 'a_pass_td', 'a_interceptions', 'a_none2']] = df.a_comp_att_yd_td_int.str.split('-',expand=True,)

	return df


def set_cols_for_analysis(df):
	df['h_pass_attempts'] = df['h_pass_attempts'].fillna(0)
	df['h_pass_attempts'] = df['h_pass_attempts'].replace('','0')
	df['h_pass_attempts'] = df['h_pass_attempts'].astype(int)
	df['h_net_pass_yards'] = df['h_net_pass_yards'].fillna(0)
	df['h_net_pass_yards'] = df['h_net_pass_yards'].replace('','0')
	df['h_net_pass_yards'] = df['h_net_pass_yards'].astype(int)
	df['a_net_pass_yards'] = df['a_net_pass_yards'].fillna(0)
	df['a_net_pass_yards'] = df['a_net_pass_yards'].replace('','0')
	df['a_net_pass_yards'] = df['a_net_pass_yards'].astype(int)
	df['h_completions'] = df['h_completions'].fillna(0)
	df['h_completions'] = df['h_completions'].replace('','0')
	df['h_completions'] = df['h_completions'].astype(int)
	df['a_pass_attempts'] = df['a_pass_attempts'].fillna(0)
	df['a_pass_attempts'] = df['a_pass_attempts'].replace('','0')
	df['a_pass_attempts'] = df['a_pass_attempts'].astype(int)
	df['a_completions'] = df['a_completions'].fillna(0)
	df['a_completions'] = df['a_completions'].replace('','0')
	df['a_completions'] = df['a_completions'].astype(int)
	df['h_interceptions'] = df['h_interceptions'].fillna(0)
	df['h_interceptions'] = df['h_interceptions'].replace('','0')
	df['h_interceptions'] = df['h_interceptions'].astype(int)
	df['a_interceptions'] = df['a_interceptions'].fillna(0)
	df['a_interceptions'] = df['a_interceptions'].replace('','0')
	df['a_interceptions'] = df['a_interceptions'].astype(int)
	df['h_rush_attempts'] = df['h_rush_attempts'].fillna(0)
	df['h_rush_attempts'] = df['h_rush_attempts'].replace('','0')
	df['h_rush_attempts'] = df['h_rush_attempts'].astype(int)
	df['h_rush_yards'] = df['h_rush_yards'].fillna(0)
	df['h_rush_yards'] = df['h_rush_yards'].replace('','0')
	df['h_rush_yards'] = df['h_rush_yards'].astype(int)
	df['h_rush_tds'] = df['h_rush_tds'].fillna(0)
	df['h_rush_tds'] = df['h_rush_tds'].replace('','0')
	df['h_rush_tds'] = df['h_rush_tds'].astype(int)
	df['a_rush_attempts'] = df['a_rush_attempts'].fillna(0)
	df['a_rush_attempts'] = df['a_rush_attempts'].replace('','0')
	df['a_rush_attempts'] = df['a_rush_attempts'].astype(int)
	df['a_rush_yards'] = df['a_rush_yards'].fillna(0)
	df['a_rush_yards'] = df['a_rush_yards'].replace('','0')
	df['a_rush_yards'] = df['a_rush_yards'].astype(int)
	df['a_rush_tds'] = df['a_rush_tds'].fillna(0)
	df['a_rush_tds'] = df['a_rush_tds'].replace('','0')
	df['a_rush_tds'] = df['a_rush_tds'].astype(int)
	df['h_pass_completion_pct'] = df['h_completions'] / df['h_pass_attempts']
	df['a_pass_completion_pct'] = df['a_completions'] / df['a_pass_attempts']
	df['h_ints_per_attempts'] = df['h_interceptions'] / df['h_pass_attempts']
	df['a_ints_per_attempts'] = df['a_interceptions'] / df['a_pass_attempts']
	df['h_pass_yards_per_attempts'] = df['h_net_pass_yards'] / df['h_pass_attempts']
	df['a_pass_yards_per_attempts'] = df['a_net_pass_yards'] / df['a_pass_attempts']
	df['h_rush_yards_per_attempts'] = df['h_rush_yards'] / df['h_rush_attempts']
	df['a_rush_yards_per_attempts'] = df['a_rush_yards'] / df['a_rush_attempts']
	df['h_rush_tds_per_attempts'] = df['h_rush_tds'] / df['h_rush_attempts']
	df['a_rush_tds_per_attempts'] = df['a_rush_tds'] / df['a_rush_attempts']

	return df

def chunk_by_season(df):
	season_chunk = h.chunk(df, col='Season')
	season_chunk = pd.DataFrame.from_dict(season_chunk, orient='index')
	season_chunk = season_chunk.iloc[:, 0]

	return season_chunk

def chunk_by_h(season_chunk):
	h_chunked = h.chunk(season_chunk[2019], col='h_team')
	h_chunked = pd.DataFrame.from_dict(h_chunked, orient='index')
	h_chunked = h_chunked.iloc[:, 0]
	for i in range(len(h_chunked)):
		h_chunked[i] = h_chunked[i].sort_values('Date', ascending=True, na_position='first')

	return h_chunked

def chunk_by_a(season_chunk):
	a_chunked = h.chunk(season_chunk[2019], col='a_team')
	a_chunked = pd.DataFrame.from_dict(a_chunked, orient='index')
	a_chunked = a_chunked.iloc[:, 0]
	for i in range(len(a_chunked)):
		a_chunked[i] = a_chunked[i].sort_values('Date', ascending=True, na_position='first')

	return a_chunked

def gen_a(a_chunked):
	for i in range(len(a_chunked)):
		a_chunked[i]['gen_net_pass_yards'] = a_chunked[i]['a_net_pass_yards']
		a_chunked[i]['gen_rush_yards'] = a_chunked[i]['a_rush_yards']
		a_chunked[i]['gen_turnovers'] = a_chunked[i]['a_turnovers']
		a_chunked[i]['gen_top'] = a_chunked[i]['a_top']
		a_chunked[i]['gen_penalties'] = a_chunked[i]['a_penalties']
		a_chunked[i]['gen_team'] = a_chunked[i]['a_team']
		a_chunked[i]['gen_score'] = a_chunked[i]['a_total']
		a_chunked[i]['gen_score_allowed'] = a_chunked[i]['h_total']
		a_chunked[i]['gen_win'] = a_chunked[i]['a_win']
		a_chunked[i]['gen_fumbles'] = a_chunked[i]['a_fumbles']
		a_chunked[i]['gen_sacks'] = a_chunked[i]['a_sacks']
		a_chunked[i]['gen_sack_yards'] = a_chunked[i]['a_sack_yards']
		a_chunked[i]['gen_pass_td'] = a_chunked[i]['a_pass_td']
		a_chunked[i]['gen_interceptions'] = a_chunked[i]['a_interceptions']
		a_chunked[i]['gen_total_yards'] = a_chunked[i]['a_total_yards']
		a_chunked[i]['gen_first_downs'] = a_chunked[i]['a_first_downs']
		a_chunked[i]['gen_pass_comp_pct'] = a_chunked[i]['a_pass_completion_pct']
		a_chunked[i]['gen_ints_per_attempt'] = a_chunked[i]['a_ints_per_attempts']
		a_chunked[i]['gen_pass_yards_per_attempt'] = a_chunked[i]['a_pass_yards_per_attempts']
		a_chunked[i]['gen_op_penalty_yards'] = a_chunked[i]['h_p_yards']
		a_chunked[i]['gen_op_sacks'] = a_chunked[i]['h_sacks']
		a_chunked[i]['gen_op_sack_yards'] = a_chunked[i]['h_sack_yards']
		a_chunked[i]['gen_op_pass_td'] = a_chunked[i]['h_pass_td']
		a_chunked[i]['gen_op_total_yards'] = a_chunked[i]['h_total_yards']
		a_chunked[i]['gen_op_first_downs'] = a_chunked[i]['h_first_downs']
		a_chunked[i]['gen_op_top'] = a_chunked[i]['h_top']
		a_chunked[i]['gen_op_pass_yards_per_attempt'] = a_chunked[i]['h_pass_yards_per_attempts']
		a_chunked[i]['gen_op_rush_tds_per_attempt'] = a_chunked[i]['h_rush_tds_per_attempts']


	return a_chunked

def gen_h(h_chunked):
	for i in range(len(h_chunked)):
		h_chunked[i]['gen_net_pass_yards'] = h_chunked[i]['h_net_pass_yards']
		h_chunked[i]['gen_rush_yards'] = h_chunked[i]['h_rush_yards']
		h_chunked[i]['gen_turnovers'] = h_chunked[i]['h_turnovers']
		h_chunked[i]['gen_top'] = h_chunked[i]['h_top']
		h_chunked[i]['gen_penalties'] = h_chunked[i]['h_penalties']
		h_chunked[i]['gen_team'] = h_chunked[i]['h_team']
		h_chunked[i]['gen_score'] = h_chunked[i]['h_total']
		h_chunked[i]['gen_score_allowed'] = h_chunked[i]['a_total']
		h_chunked[i]['gen_win'] = h_chunked[i]['h_win']
		h_chunked[i]['gen_fumbles'] = h_chunked[i]['h_fumbles']
		h_chunked[i]['gen_sacks'] = h_chunked[i]['h_sacks']
		h_chunked[i]['gen_sack_yards'] = h_chunked[i]['h_sack_yards']
		h_chunked[i]['gen_pass_td'] = h_chunked[i]['h_pass_td']
		h_chunked[i]['gen_interceptions'] = h_chunked[i]['h_interceptions']
		h_chunked[i]['gen_total_yards'] = h_chunked[i]['h_total_yards']
		h_chunked[i]['gen_first_downs'] = h_chunked[i]['h_first_downs']
		h_chunked[i]['gen_pass_comp_pct'] = h_chunked[i]['h_pass_completion_pct']
		h_chunked[i]['gen_ints_per_attempt'] = h_chunked[i]['h_ints_per_attempts']
		h_chunked[i]['gen_pass_yards_per_attempt'] = h_chunked[i]['h_pass_yards_per_attempts']
		h_chunked[i]['gen_op_penalty_yards'] = h_chunked[i]['a_p_yards']
		h_chunked[i]['gen_op_sacks'] = h_chunked[i]['a_sacks']
		h_chunked[i]['gen_op_sack_yards'] = h_chunked[i]['a_sack_yards']
		h_chunked[i]['gen_op_pass_td'] = h_chunked[i]['a_pass_td']
		h_chunked[i]['gen_op_total_yards'] = h_chunked[i]['a_total_yards']
		h_chunked[i]['gen_op_first_downs'] = h_chunked[i]['a_first_downs']
		h_chunked[i]['gen_op_top'] = h_chunked[i]['a_top']
		h_chunked[i]['gen_op_pass_yards_per_attempt'] = h_chunked[i]['a_pass_yards_per_attempts']
		h_chunked[i]['gen_op_rush_tds_per_attempt'] = h_chunked[i]['a_rush_tds_per_attempts']


	return h_chunked

def get_stats(a_chunked, h_chunked):
	master2 = []
	for i in range(len(a_chunked)):
		teams = pd.concat([a_chunked[i], h_chunked[i]], sort=True)
		teams = teams.sort_values('Date', ascending=True, na_position='first')
		# print('gen_avg_penalties')
		teams['gen_avg_penalties'] = teams.gen_penalties.expanding(1).mean()
		listp = teams['gen_avg_penalties']
		listp = listp.tolist()
		Na = 0
		newlistp = [Na] + listp
		newlistp = newlistp[:-1]
		teams['gen_avg_penalties'] = newlistp
		# print('gen_avg_score')
		teams['gen_avg_score'] = teams.gen_score.expanding(1).mean()
		list1 = teams['gen_avg_score']
		list2 = list1.tolist()
		Na = 0
		newlist = [Na] + list2
		newlist = newlist[:-1]
		teams['gen_avg_score'] = newlist
		# print('gen_avg_allowed')
		teams['gen_avg_allowed'] = teams.gen_score_allowed.expanding(1).mean()
		list4 = teams['gen_avg_allowed']
		list4 = list4.tolist()
		Na = 0
		newlist3 = [Na] + list4
		newlist3 = newlist3[:-1]
		teams['gen_avg_allowed'] = newlist3
		# print('Gen_Games')
		teams['Gen_Games'] = np.arange(len(teams))
		# print('gen_rec')
		teams['gen_rec'] = teams.gen_win.cumsum()
		# print('gen_avg_pass_yards')
		teams['gen_avg_pass_yards'] = teams.gen_net_pass_yards.expanding(1).mean()
		list7 = teams['gen_avg_pass_yards']
		list7 = list7.tolist()
		Na = 0
		newlist4 = [Na] + list7
		newlist4 = newlist4[:-1]
		teams['gen_avg_pass_yards'] = newlist4
		# print('gen_avg_turnovers')
		teams['gen_avg_turnovers'] = teams.gen_turnovers.expanding(1).mean()
		list9 = teams['gen_avg_turnovers']
		list9 = list9.tolist()
		Na = 0
		newlist9 = [Na] + list9
		newlist9 = newlist9[:-1]
		teams['gen_avg_turnovers'] = newlist9
		# print('gen_avg_top')
		teams['gen_avg_top'] = teams.gen_top.expanding(1).mean()
		list11 = teams['gen_avg_top']
		list11 = list11.tolist()
		Na = 0
		newlist11 = [Na] + list11
		newlist11 = newlist11[:-1]
		teams['gen_avg_top'] = newlist11
		# print('gen_avg_rush_yards')
		teams['gen_avg_rush_yards'] = teams.gen_rush_yards.expanding(1).mean()
		list_rush_yards = teams['gen_avg_rush_yards']
		list_rush_yards = list_rush_yards.tolist()
		Na = 0
		newlist_rush_yards = [Na] + list_rush_yards
		newlist_rush_yards = newlist_rush_yards[:-1]
		teams['gen_avg_rush_yards'] = newlist_rush_yards
		teams['gen_avg_fumbles'] = teams.gen_fumbles.expanding(1).mean()
		listf = teams['gen_avg_fumbles']
		listf = listf.tolist()
		Na = 0
		newlistf = [Na] + listf
		newlistf = newlistf[:-1]
		teams['gen_avg_fumbles'] = newlistf
		teams['gen_avg_sacks'] = teams.gen_sacks.expanding(1).mean()
		lists = teams['gen_avg_sacks']
		lists = lists.tolist()
		Na = 0
		newlists = [Na] + lists
		newlists = newlists[:-1]
		teams['gen_avg_sacks'] = newlists
		teams['gen_avg_sack_yards'] = teams.gen_sack_yards.expanding(1).mean()
		listsy = teams['gen_avg_sack_yards']
		listsy = listsy.tolist()
		Na = 0
		newlistsy = [Na] + listsy
		newlistsy = newlistsy[:-1]
		teams['gen_avg_sack_yards'] = newlistsy
		teams['gen_avg_pass_tds'] = teams.gen_pass_td.expanding(1).mean()
		listptds = teams['gen_avg_pass_tds']
		listptds = listptds.tolist()
		Na = 0
		newlistptds = [Na] + listptds
		newlistptds = newlistptds[:-1]
		teams['gen_avg_pass_tds'] = newlistptds
		teams['gen_avg_interceptions'] = teams.gen_interceptions.expanding(1).mean()
		listint = teams['gen_avg_interceptions']
		listint = listint.tolist()
		Na = 0
		newlistint = [Na] + listint
		newlistint = newlistint[:-1]
		teams['gen_avg_interceptions'] = newlistint
		teams['gen_avg_total_yards'] = teams.gen_total_yards.expanding(1).mean()
		list8 = teams['gen_avg_total_yards']
		list8 = list8.tolist()
		Na = 0
		newlist8 = [Na] + list8
		newlist8 = newlist8[:-1]
		teams['gen_avg_total_yards'] = newlist8
		teams['gen_avg_turnovers'] = teams.gen_turnovers.expanding(1).mean()
		list9 = teams['gen_avg_turnovers']
		list9 = list9.tolist()
		Na = 0
		newlist9 = [Na] + list9
		newlist9 = newlist9[:-1]
		teams['gen_avg_turnovers'] = newlist9
		teams['gen_avg_first_downs'] = teams.gen_first_downs.expanding(1).mean()
		list10 = teams['gen_avg_first_downs']
		list10 = list10.tolist()
		Na = 0
		newlist10 = [Na] + list10
		newlist10 = newlist10[:-1]
		teams['gen_avg_first_downs'] = newlist10
		teams['gen_avg_pass_comp_pct'] = teams.gen_pass_comp_pct.expanding(1).mean()
		listppct = teams['gen_avg_pass_comp_pct']
		listppct = listppct.tolist()
		Na = 0
		newlistppct = [Na] + listppct
		newlistppct = newlistppct[:-1]
		teams['gen_avg_pass_comp_pct'] = newlistppct
		teams['gen_avg_ints_per_attempt'] = teams.gen_ints_per_attempt.expanding(1).mean()
		list_ints_per = teams['gen_avg_ints_per_attempt']
		list_ints_per = list_ints_per.tolist()
		Na = 0
		newlist_ints_per = [Na] + list_ints_per
		newlist_ints_per = newlist_ints_per[:-1]
		teams['gen_avg_ints_per_attempt'] = newlist_ints_per
		teams['gen_avg_pass_yards_per_attempt'] = teams.gen_pass_yards_per_attempt.expanding(1).mean()
		list_pass_yards_per = teams['gen_avg_pass_yards_per_attempt']
		list_pass_yards_per = list_pass_yards_per.tolist()
		Na = 0
		newlist_pass_yards_per = [Na] + list_pass_yards_per
		newlist_pass_yards_per = newlist_pass_yards_per[:-1]
		teams['gen_avg_pass_yards_per_attempt'] = newlist_pass_yards_per
		teams['gen_op_avg_penalty_yards'] = teams.gen_op_penalty_yards.expanding(1).mean()
		listpy = teams['gen_op_avg_penalty_yards']
		listpy = listpy.tolist()
		Na = 0
		newlistpy = [Na] + listpy
		newlistpy = newlistpy[:-1]
		teams['gen_op_avg_penalty_yards'] = newlistpy
		teams['gen_avg_sacks_allowed'] = teams.gen_op_sacks.expanding(1).mean()
		lists = teams['gen_avg_sacks_allowed']
		lists = lists.tolist()
		Na = 0
		newlists = [Na] + lists
		newlists = newlists[:-1]
		teams['gen_avg_sacks_allowed'] = newlists
		teams['gen_avg_sack_yards_allowed'] = teams.gen_op_sack_yards.expanding(1).mean()
		listsy = teams['gen_avg_sack_yards_allowed']
		listsy = listsy.tolist()
		Na = 0
		newlistsy = [Na] + listsy
		newlistsy = newlistsy[:-1]
		teams['gen_avg_sack_yards_allowed'] = newlistsy
		teams['gen_avg_pass_tds_allowed'] = teams.gen_op_pass_td.expanding(1).mean()
		listptds = teams['gen_avg_pass_tds_allowed']
		listptds = listptds.tolist()
		Na = 0
		newlistptds = [Na] + listptds
		newlistptds = newlistptds[:-1]
		teams['gen_avg_pass_tds_allowed'] = newlistptds
		teams['gen_avg_total_yards_allowed'] = teams.gen_op_total_yards.expanding(1).mean()
		list8 = teams['gen_avg_total_yards_allowed']
		list8 = list8.tolist()
		Na = 0
		newlist8 = [Na] + list8
		newlist8 = newlist8[:-1]
		teams['gen_avg_total_yards_allowed'] = newlist8
		teams['gen_avg_first_downs_allowed'] = teams.gen_op_first_downs.expanding(1).mean()
		list10 = teams['gen_avg_first_downs_allowed']
		list10 = list10.tolist()
		Na = 0
		newlist10 = [Na] + list10
		newlist10 = newlist10[:-1]
		teams['gen_avg_first_downs_allowed'] = newlist10
		teams['gen_avg_top_allowed'] = teams.gen_op_top.expanding(1).mean()
		list11 = teams['gen_avg_top_allowed']
		list11 = list11.tolist()
		Na = 0
		newlist11 = [Na] + list11
		newlist11 = newlist11[:-1]
		teams['gen_avg_top_allowed'] = newlist11
		teams['gen_avg_pass_yards_per_attempt_allowed'] = teams.gen_op_pass_yards_per_attempt.expanding(1).mean()
		list_pass_yards_per = teams['gen_avg_pass_yards_per_attempt_allowed']
		list_pass_yards_per = list_pass_yards_per.tolist()
		Na = 0
		newlist_pass_yards_per = [Na] + list_pass_yards_per
		newlist_pass_yards_per = newlist_pass_yards_per[:-1]
		teams['gen_avg_pass_yards_per_attempt_allowed'] = newlist_pass_yards_per
		teams['gen_avg_rush_tds_per_attempt_allowed'] = teams.gen_op_rush_tds_per_attempt.expanding(1).mean()
		list_rush_tds_per = teams['gen_avg_rush_tds_per_attempt_allowed']
		list_rush_tds_per = list_rush_tds_per.tolist()
		Na = 0
		newlist_rush_tds_per = [Na] + list_rush_tds_per
		newlist_rush_tds_per = newlist_rush_tds_per[:-1]
		teams['gen_avg_rush_tds_per_attempt_allowed'] = newlist_rush_tds_per
		print(teams['h_team'])
		print(teams['a_team'])
		master2.append(teams)

	big_csv = []
	for x in range(len(master2)):
		if x > 0:
			before = pd.DataFrame(master2[:x])
			print(master2[x]['Season'])
			before = pd.concat([b for b in before[0]])
		else:
			before = pd.DataFrame()
		if x < 1177:
			after = pd.DataFrame(master2[x:])
			after = pd.concat([a for a in after[0]])
		else:
			continue
		master3 = pd.concat([before, after], ignore_index=True)
		master4 = pd.merge(master2[x], master2[x], on=['Game_id'], how='inner')
		big_csv.append(master4)

	big_csv = pd.concat([b for b in big_csv], ignore_index=True)

	return big_csv

def home_away_stats(big_csv):
	big_csv1 = big_csv.drop_duplicates(subset='Game_id', keep='last')
	big_csv2 = big_csv.drop_duplicates(subset='Game_id', keep='first')
	big_csv1 = big_csv1.sort_values('Game_id', ascending=True, na_position='first')
	big_csv2 = big_csv2.sort_values('Game_id', ascending=True, na_position='first')

	genw = big_csv1['gen_team_x']
	genw = genw.tolist()
	genw2 = big_csv2['gen_team_x']
	genw2 = genw2.tolist()
	hw1 = big_csv1['h_team_x']
	hw1 = hw1.tolist()
	aw1 = big_csv1['a_team_x']
	aw1 = aw1.tolist()
	hw2 = big_csv2['h_team_x']
	hw2 = hw2.tolist()
	aw2 = big_csv2['a_team_x']
	aw2 = aw2.tolist()

	pen1 = big_csv1['gen_avg_penalties_x']
	pen1 = pen1.tolist()
	pen2 = big_csv2['gen_avg_penalties_x']
	pen2 = pen2.tolist()
	a_pen = []
	h_pen = []
	ry1 = big_csv1['gen_avg_rush_yards_x']
	ry1 = ry1.tolist()
	ry2 = big_csv2['gen_avg_rush_yards_x']
	ry2 = ry2.tolist()
	h_ry = []
	a_ry = []
	top1 = big_csv1['gen_avg_top_x']
	top1 = top1.tolist()
	top2 = big_csv2['gen_avg_top_x']
	top2 = top2.tolist()
	h_top = []
	a_top = []
	to1 = big_csv1['gen_avg_turnovers_x']
	to1 = to1.tolist()
	to2 = big_csv2['gen_avg_turnovers_x']
	to2 = to2.tolist()
	h_to = []
	a_to = []
	py1 = big_csv1['gen_avg_pass_yards_x']
	py1 = py1.tolist()
	py2 = big_csv2['gen_avg_pass_yards_x']
	py2 = py2.tolist()
	h_py = []
	a_py = []
	sc1 = big_csv1['gen_avg_score_x']
	sc1 = sc1.tolist()
	sc2 = big_csv2['gen_avg_score_x']
	sc2 = sc2.tolist()
	h_sc = []
	a_sc = []
	al1 = big_csv1['gen_avg_allowed_x']
	al1 = al1.tolist()
	al2 = big_csv2['gen_avg_allowed_x']
	al2 = al2.tolist()
	h_al = []
	a_al = []
	fum = big_csv1['gen_avg_fumbles_x']
	fum = fum.tolist()
	fum2 = big_csv2['gen_avg_fumbles_x']
	fum2 = fum2.tolist()
	h_fumbles = []
	a_fumbles = []
	sak = big_csv1['gen_avg_sacks_x']
	sak = sak.tolist()
	sak2 = big_csv2['gen_avg_sacks_x']
	sak2 = sak2.tolist()
	h_sacks = []
	a_sacks = []
	sak_y = big_csv1['gen_avg_sack_yards_x']
	sak_y = sak_y.tolist()
	sak_y2 = big_csv2['gen_avg_sack_yards_x']
	sak_y2 = sak_y2.tolist()
	h_sack_yards = []
	a_sack_yards = []
	ptd = big_csv1['gen_avg_pass_tds_x']
	ptd = ptd.tolist()
	ptd2 = big_csv2['gen_avg_pass_tds_x']
	ptd2 = ptd2.tolist()
	h_pass_tds = []
	a_pass_tds = []
	inte = big_csv1['gen_avg_interceptions_x']
	inte = inte.tolist()
	inte2 = big_csv2['gen_avg_interceptions_x']
	inte2 = inte2.tolist()
	h_interceptions = []
	a_interceptions = []
	tot_y = big_csv1['gen_avg_total_yards_x']
	tot_y = tot_y.tolist()
	tot_y2 = big_csv2['gen_avg_total_yards_x']
	tot_y2 = tot_y2.tolist()
	h_total_yds = []
	a_total_yds = []
	fd = big_csv1['gen_avg_first_downs_y']
	fd = fd.tolist()
	fd2 = big_csv2['gen_avg_first_downs_y']
	fd2 = fd2.tolist()
	h_fd = []
	a_fd = []
	pcp = big_csv1['gen_avg_pass_comp_pct_x']
	pcp = pcp.tolist()
	pcp2 = big_csv2['gen_avg_pass_comp_pct_x']
	pcp2 = pcp2.tolist()
	h_pass_comp_pct = []
	a_pass_comp_pct = []
	ipa = big_csv1['gen_avg_ints_per_attempt_x']
	ipa = ipa.tolist()
	ipa2 = big_csv2['gen_avg_ints_per_attempt_x']
	ipa2 = ipa2.tolist()
	h_int_pa = []
	a_int_pa = []
	pypa = big_csv1['gen_avg_pass_yards_per_attempt_x']
	pypa = pypa.tolist()
	pypa2 = big_csv2['gen_avg_pass_yards_per_attempt_x']
	pypa2 = pypa2.tolist()
	h_pass_yds_pa =[]
	a_pass_yds_pa =[]
	opy = big_csv1['gen_op_avg_penalty_yards_x']
	opy = opy.tolist()
	opy2 = big_csv2['gen_op_avg_penalty_yards_x']
	opy2 = opy2.tolist()
	h_op_penalty_yards =[]
	a_op_penalty_yards =[]
	skal = big_csv1['gen_avg_sacks_allowed_x']
	skal = skal.tolist()
	skal2 = big_csv2['gen_avg_sacks_allowed_x']
	skal2 = skal2.tolist()
	h_sacks_all = []
	a_sacks_all = []
	skyal = big_csv1['gen_avg_sack_yards_allowed_x']
	skyal = skyal.tolist()
	skyal2 = big_csv2['gen_avg_sack_yards_allowed_x']
	skyal2 = skyal2.tolist()
	h_sacks_y_all = []
	a_sacks_y_all = []
	ptdal = big_csv1['gen_avg_pass_tds_allowed_x']
	ptdal = ptdal.tolist()
	ptdal2 = big_csv2['gen_avg_pass_tds_allowed_x']
	ptdal2 = ptdal2.tolist()
	h_pass_tds_all = []
	a_pass_tds_all = []
	totyall = big_csv1['gen_avg_total_yards_allowed_x']
	totyall = totyall.tolist()
	totyall2 = big_csv2['gen_avg_total_yards_allowed_x']
	totyall2 = totyall2.tolist()
	h_tot_yds_all = []
	a_tot_yds_all = []
	fdall = big_csv1['gen_avg_first_downs_allowed_x']
	fdall = fdall.tolist()
	fdall2 = big_csv2['gen_avg_first_downs_allowed_x']
	fdall2 = fdall2.tolist()
	h_fd_all = []
	a_fd_all = []
	topal = big_csv1['gen_avg_top_allowed_x']
	topal = topal.tolist()
	topal2 = big_csv2['gen_avg_top_allowed_x']
	topal2 = topal2.tolist()
	h_top_all = []
	a_top_all = []
	pypaal = big_csv1['gen_avg_pass_yards_per_attempt_allowed_x']
	pypaal = pypaal.tolist()
	pypaal2 = big_csv2['gen_avg_pass_yards_per_attempt_allowed_x']
	pypaal2 = pypaal2.tolist()
	h_p_yds_pa_all = []
	a_p_yds_pa_all = []
	rtdpaal = big_csv1['gen_avg_rush_tds_per_attempt_allowed_x']
	rtdpaal = rtdpaal.tolist()
	rtdpaal2 = big_csv2['gen_avg_rush_tds_per_attempt_allowed_x']
	rtdpaal2 = rtdpaal2.tolist()
	h_r_tds_pa_all = []
	a_r_tds_pa_all = []



	for x in range(len(big_csv1)):
		if genw[x] == genw2[x]:
			genw2[x] = hw1[x]
		if str(genw[x]) == str(hw1[x]):
			h_pen.append(pen1[x])
			h_ry.append(ry1[x])
			h_top.append(top1[x])
			h_to.append(to1[x])
			h_py.append(py1[x])
			h_sc.append(sc1[x])
			h_al.append(al1[x])
			h_fumbles.append(fum[x])
			h_sacks.append(sak[x])
			h_sack_yards.append(sak_y[x])
			h_pass_tds.append(ptd[x])
			h_interceptions.append(inte[x])
			h_total_yds.append(tot_y[x])
			h_fd.append(fd[x])
			h_pass_comp_pct.append(pcp[x])
			h_int_pa.append(ipa[x])
			h_pass_yds_pa.append(pypa[x])
			h_op_penalty_yards.append(opy[x])
			h_sacks_all.append(skal[x])
			h_sacks_y_all.append(skyal[x])
			h_pass_tds_all.append(ptdal[x])
			h_tot_yds_all.append(totyall[x])
			h_fd_all.append(fdall[x])
			h_top_all.append(topal[x])
			h_p_yds_pa_all.append(pypaal[x])
			h_r_tds_pa_all.append(rtdpaal[x])
		else:
			a_pen.append(pen1[x])
			a_ry.append(ry1[x])
			a_top.append(top1[x])
			a_to.append(to1[x])
			a_py.append(py1[x])
			a_sc.append(sc1[x])
			a_al.append(al1[x])
			a_fumbles.append(fum[x])
			a_sacks.append(sak[x])
			a_sack_yards.append(sak_y[x])
			a_pass_tds.append(ptd[x])
			a_interceptions.append(inte[x])
			a_total_yds.append(tot_y[x])
			a_fd.append(fd[x])
			a_pass_comp_pct.append(pcp[x])
			a_int_pa.append(ipa[x])
			a_pass_yds_pa.append(pypa[x])
			a_op_penalty_yards.append(opy[x])
			a_sacks_all.append(skal[x])
			a_sacks_y_all.append(skyal[x])
			a_pass_tds_all.append(ptdal[x])
			a_tot_yds_all.append(totyall[x])
			a_fd_all.append(fdall[x])
			a_top_all.append(topal[x])
			a_p_yds_pa_all.append(pypaal[x])
			a_r_tds_pa_all.append(rtdpaal[x])
		if str(genw2[x]) == str(hw1[x]):
			h_pen.append(pen2[x])
			h_ry.append(ry2[x])
			h_top.append(top2[x])
			h_to.append(to2[x])
			h_py.append(py2[x])
			h_sc.append(sc2[x])
			h_al.append(al2[x])
			h_fumbles.append(fum2[x])
			h_sacks.append(sak2[x])
			h_sack_yards.append(sak_y2[x])
			h_pass_tds.append(ptd2[x])
			h_interceptions.append(inte2[x])
			h_total_yds.append(tot_y2[x])
			h_fd.append(fd2[x])
			h_pass_comp_pct.append(pcp2[x])
			h_int_pa.append(ipa2[x])
			h_pass_yds_pa.append(pypa2[x])
			h_op_penalty_yards.append(opy2[x])
			h_sacks_all.append(skal2[x])
			h_sacks_y_all.append(skyal2[x])
			h_pass_tds_all.append(ptdal2[x])
			h_tot_yds_all.append(totyall2[x])
			h_fd_all.append(fdall2[x])
			h_top_all.append(topal2[x])
			h_p_yds_pa_all.append(pypaal2[x])
			h_r_tds_pa_all.append(rtdpaal2[x])
		else:
			a_pen.append(pen2[x])
			a_ry.append(ry2[x])
			a_top.append(top2[x])
			a_to.append(to2[x])
			a_py.append(py2[x])
			a_sc.append(sc2[x])
			a_al.append(al2[x])
			a_fumbles.append(fum2[x])
			a_sacks.append(sak2[x])
			a_sack_yards.append(sak_y2[x])
			a_pass_tds.append(ptd2[x])
			a_interceptions.append(inte2[x])
			a_total_yds.append(tot_y2[x])
			a_fd.append(fd2[x])
			a_pass_comp_pct.append(pcp2[x])
			a_int_pa.append(ipa2[x])
			a_pass_yds_pa.append(pypa2[x])
			a_op_penalty_yards.append(opy2[x])
			a_sacks_all.append(skal2[x])
			a_sacks_y_all.append(skyal2[x])
			a_pass_tds_all.append(ptdal2[x])
			a_tot_yds_all.append(totyall2[x])
			a_fd_all.append(fdall2[x])
			a_top_all.append(topal2[x])
			a_p_yds_pa_all.append(pypaal2[x])
			a_r_tds_pa_all.append(rtdpaal2[x])


	big_csv1['Home_team_gen_avg_penalties'] = h_pen
	big_csv1['Home_team_gen_avg_rush_yards'] = h_ry
	big_csv1['Home_team_gen_avg_time_of_possesion'] = h_top
	big_csv1['Home_team_gen_avg_turnovers'] = h_to
	big_csv1['Home_team_gen_avg_sacks'] = h_sacks
	big_csv1['Home_team_gen_avg_sack_yards'] = h_sack_yards
	big_csv1['Home_team_gen_avg_pass_yards'] = h_py
	big_csv1['Home_team_gen_avg_score'] = h_sc
	big_csv1['Home_team_gen_avg_points_allowed'] = h_al
	big_csv1['Home_team_gen_avg_fumbles'] = h_fumbles
	big_csv1['Home_team_gen_avg_pass_tds'] = h_pass_tds
	big_csv1['Home_team_gen_avg_interceptions'] = h_interceptions
	big_csv1['Home_team_gen_avg_total_yards'] = h_total_yds
	big_csv1['Home_team_gen_avg_first_downs'] = h_fd
	big_csv1['Home_team_gen_avg_pass_completion_pct'] = h_pass_comp_pct
	big_csv1['Home_team_gen_avg_interceptions_per_attempt'] = h_int_pa
	big_csv1['Home_team_gen_avg_pass_yards_per_attempt'] = h_pass_yds_pa
	big_csv1['Home_team_gen_avg_op_penalty_yards'] = h_op_penalty_yards
	big_csv1['Home_team_gen_avg_sacks_allowed'] = h_sacks_all
	big_csv1['Home_team_gen_avg_sack_yards_allowed'] = h_sacks_y_all
	big_csv1['Home_team_gen_avg_pass_tds_allowed'] = h_pass_tds_all
	big_csv1['Home_team_gen_avg_total_yards_allowed'] = h_tot_yds_all
	big_csv1['Home_team_gen_avg_first_downs_allowed'] = h_fd_all
	big_csv1['Home_team_gen_avg_top_allowed'] = h_top_all
	big_csv1['Home_team_gen_avg_pass_yards_per_attempt_allowed'] = h_p_yds_pa_all
	big_csv1['Home_team_gen_avg_rush_tds_per_attempt_allowed'] = h_r_tds_pa_all

	big_csv1['Away_team_gen_avg_penalties'] = a_pen
	big_csv1['Away_team_gen_avg_rush_yards'] = a_ry
	big_csv1['Away_team_gen_avg_time_of_possesion'] = a_top
	big_csv1['Away_team_gen_avg_turnovers'] = a_to
	big_csv1['Away_team_gen_avg_sacks'] = a_sacks
	big_csv1['Away_team_gen_avg_sack_yards'] = a_sack_yards
	big_csv1['Away_team_gen_avg_pass_yards'] = a_py
	big_csv1['Away_team_gen_avg_score'] = a_sc
	big_csv1['Away_team_gen_avg_points_allowed'] = a_al
	big_csv1['Away_team_gen_avg_fumbles'] = a_fumbles
	big_csv1['Away_team_gen_avg_pass_tds'] = a_pass_tds
	big_csv1['Away_team_gen_avg_interceptions'] = a_interceptions
	big_csv1['Away_team_gen_avg_total_yards'] = a_total_yds
	big_csv1['Away_team_gen_avg_first_downs'] = a_fd
	big_csv1['Away_team_gen_avg_pass_completion_pct'] = a_pass_comp_pct
	big_csv1['Away_team_gen_avg_interceptions_per_attempt'] = a_int_pa
	big_csv1['Away_team_gen_avg_pass_yards_per_attempt'] = a_pass_yds_pa
	big_csv1['Away_team_gen_avg_op_penalty_yards'] = a_op_penalty_yards
	big_csv1['Away_team_gen_avg_sacks_allowed'] = a_sacks_all
	big_csv1['Away_team_gen_avg_sack_yards_allowed'] = a_sacks_y_all
	big_csv1['Away_team_gen_avg_pass_tds_allowed'] = a_pass_tds_all
	big_csv1['Away_team_gen_avg_total_yards_allowed'] = a_tot_yds_all
	big_csv1['Away_team_gen_avg_first_downs_allowed'] = a_fd_all
	big_csv1['Away_team_gen_avg_top_allowed'] = a_top_all
	big_csv1['Away_team_gen_avg_pass_yards_per_attempt_allowed'] = a_p_yds_pa_all
	big_csv1['Away_team_gen_avg_rush_tds_per_attempt_allowed'] = a_r_tds_pa_all


	

	return big_csv1


# sixth function needs to output the same dataframe with only the rows for the upcoming game

def erase_rows(df):
	# df2 = df[df.Date < 20191028]
	df = df[df.Date >= 20191028]

	# df2 = open_csv('nfl_history_with_stats.csv')
	
	# df2 = pd.concat([df, df2])
	# df2 = df2.sort_values('Date', ascending=True, na_position='first')

	# df3 = open_csv('week9_preds.csv') # whatever the most recent dataframe was for test purposes

	# cols = ['a_elo_pre', 'h_elo_pre', 'Home_team_gen_avg_rush_yards', 'Away_team_gen_avg_rush_yards',
	# 		'Away_team_gen_avg_penalties', 'Home_team_gen_avg_penalties', 'Away_team_gen_avg_turnovers',
	# 		'Home_team_gen_avg_turnovers', 'Away_team_gen_avg_pass_yards', 'Home_team_gen_avg_pass_yards',
	# 		'Home_team_gen_avg_time_of_possesion', 'Away_team_gen_avg_time_of_possesion', 'Home_team_gen_avg_score',
	# 		'Away_team_gen_avg_score', 'Away_team_gen_avg_points_allowed', 'Home_team_gen_avg_points_allowed',
	# 		'Date', 'h_win_1_score', 'h_win_0_score', 'a_team', 'h_team', 'h_ML_EV', 'a_ML_EV', 'h_ML_pick', 'a_ML_pick']


	df.write_csv(fn='nfl_2019_week9_expanded.csv')
	
	return df


# seventh function needs to erase the columns that we do not want while running through auto ml

def erase_cols(df):

	a_team = df['a_team_x']
	a_team = a_team.tolist()
	h_team = df['h_team_x']
	h_team = h_team.tolist()
	df['a_team'] = a_team
	df['h_team'] = h_team
	date = df['Date_x']
	date = date.tolist()
	df['Date'] = date
	season = df['Season_x']
	season = season.tolist()
	df['Season'] = season

	columns = ['a_team_x', 'h_team_x','gen_avg_penalties_x', 'gen_avg_score_x', 'gen_avg_allowed_x', 'Gen_Games_x', 'gen_rec_x',
			   'gen_avg_pass_yards_x', 'gen_avg_turnovers_x', 'gen_avg_top_x', 'gen_avg_rush_yards_x',
			   'Attendance_y', 'Date_y', 'Season_y', 'Start_time_y', 'Venue_y', 'Year_y', 'a_1stq_y',
			   'a_2ndq_y', 'a_3rdq_y', 'a_4thq_y', 'a_5thq_y', 'a_coach_y', 'a_comp_att_yd_td_int_y',
			   'a_completions_y', 'a_f_lost_y', 'a_first_downs_y',
			   'a_fumbles_y', 'a_fumbles_lost_y', 'a_interceptions_y',
			   'a_ints_per_attempts_y', 'a_net_pass_yards_y', 'a_p_yards_y', 'a_pass_attempts_y',
			   'a_pass_completion_pct_y', 'a_pass_td_y', 'a_pass_yards_y', 'a_pass_yards_per_attempts_y',
			   'a_penalties_y', 'a_penalty_yards_y', 'a_rush_attempts_y', 'a_rush_tds_y',
			   'a_rush_tds_per_attempts_y', 'a_rush_yards_y', 'a_rush_yards_per_attempts_y',
			   'a_rush_yds_tds_y', 'a_sack_yards_y', 'a_sacked_yards_y', 'a_sacks_y', 'a_team_y',
			   'a_tie_y', 'a_top_y', 'a_total_y', 'a_total_yards_y', 'a_turnovers_y', 'a_win_y',
			   'gen_net_pass_yards_y', 'gen_penalties_y', 'gen_rush_yards_y', 'gen_score_y',
			   'gen_score_allowed_y', 'gen_team_y', 'gen_top_y', 'gen_turnovers_y', 'gen_win_y',
			   'h_1stq_y', 'h_2ndq_y', 'h_3rdq_y', 'h_4thq_y', 'h_5thq_y', 'h_coach_y',
			   'h_comp_att_yd_td_int_y', 'h_completions_y', 'h_f_lost_y', 'h_first_downs_y',
			   'h_fumbles_y', 'h_fumbles_lost_y', 'h_interceptions_y', 'h_ints_per_attempts_y',
			   'h_net_pass_yards_y', 'h_p_yards_y', 'h_pass_attempts_y', 'h_pass_completion_pct_y',
			   'h_pass_td_y', 'h_pass_yards_y', 'h_pass_yards_per_attempts_y', 'h_penalties_y',
			   'h_penalty_yards_y', 'h_rush_attempts_y', 'h_rush_tds_y', 'h_rush_tds_per_attempts_y',
			   'h_rush_yards_y', 'h_rush_yards_per_attempts_y', 'h_rush_yds_tds_y', 'h_sack_yards_y',
			   'h_sacked_yards_y', 'h_sacks_y', 'h_team_y',
			   'h_tie_y', 'h_top_y', 'h_total_y', 'h_total_yards_y', 'h_turnovers_y', 'h_win_y',
			   'over_under_y', 'spread_y', 'gen_avg_penalties_y', 'gen_avg_score_y', 'gen_avg_allowed_y', 'Gen_Games_y',
			   'gen_rec_y', 'gen_avg_pass_yards_y', 'gen_avg_turnovers_y', 'gen_avg_top_y', 'gen_avg_rush_yards_y', 'Attendance_x',
			   'Date_x', 'Season_x', 'Start_time_x', 'Venue_x', 'Year_x', 'a_1stq_x', 'a_2ndq_x', 'a_3rdq_x', 'a_4thq_x',
			   'a_5thq_x', 'a_coach_x', 'a_comp_att_yd_td_int_x', 'a_completions_x', 'a_f_lost_x', 'a_first_downs_x',
			   'a_fumbles_x', 'h_none_x', 'h_none_y', 'a_none_x', 'a_none2_x', 'a_none_y', 'a_none2_y',
			   'a_fumbles_lost_x', 'a_interceptions_x', 'a_ints_per_attempts_x', 'a_net_pass_yards_x', 'a_p_yards_x', 'a_pass_attempts_x', 
			   'a_pass_completion_pct_x', 'a_pass_td_x', 'a_pass_yards_x', 'a_pass_yards_per_attempts_x', 'a_penalties_x', 'a_penalty_yards_x', 
			   'a_rush_attempts_x', 'a_rush_tds_x', 'a_rush_tds_per_attempts_x', 'a_rush_yards_x', 'a_rush_yards_per_attempts_x', 'a_rush_yds_tds_x', 
			   'a_sack_yards_x', 'a_sacked_yards_x', 'a_sacks_x', 'a_tie_x', 
			   'a_top_x', 'a_total_x', 'a_total_yards_x', 'a_turnovers_x', 'a_win_x', 'gen_net_pass_yards_x', 'gen_penalties_x', 
			   'gen_rush_yards_x', 'gen_score_x', 'gen_score_allowed_x', 'gen_team_x', 'gen_top_x', 'gen_turnovers_x', 'gen_win_x', 
			   'h_1stq_x', 'h_2ndq_x', 'h_3rdq_x', 'h_4thq_x', 'h_5thq_x', 'h_coach_x', 'h_comp_att_yd_td_int_x', 'h_completions_x', 
			   'h_f_lost_x', 'h_first_downs_x',
			   'h_fumbles_x', 'h_fumbles_lost_x', 'h_interceptions_x', 'h_ints_per_attempts_x', 'h_net_pass_yards_x', 'h_p_yards_x', 
			   'h_pass_attempts_x', 'h_pass_completion_pct_x', 'h_pass_td_x', 'h_pass_yards_x', 'h_pass_yards_per_attempts_x', 'h_penalties_x', 
			   'h_penalty_yards_x', 'h_rush_attempts_x', 'h_rush_tds_x', 'h_rush_tds_per_attempts_x', 'h_rush_yards_x', 
			   'h_rush_yards_per_attempts_x', 'h_rush_yds_tds_x', 'h_sack_yards_x', 'h_sacked_yards_x', 'h_sacks_x', 
			   'h_tie_x', 'h_top_x', 'h_total_x', 'gen_op_rush_tds_per_attempt_x','gen_avg_rush_tds_per_attempt_allowed_x', 'gen_op_rush_tds_per_attempt_y', 'gen_avg_rush_tds_per_attempt_allowed_y',
			   'h_total_yards_x', 'h_turnovers_x', 'h_win_x', 'over_under_x', 'spread_x', 
			   'gen_avg_first_downs_allowed_x', 'gen_avg_first_downs_allowed_y', 'gen_avg_first_downs_x',
			   'gen_avg_first_downs_y', 'gen_avg_fumbles_x', 'gen_avg_fumbles_y', 'gen_avg_interceptions_x',
			   'gen_avg_interceptions_y', 'gen_avg_ints_per_attempt_x', 'gen_avg_ints_per_attempt_y',
			   'gen_avg_pass_comp_pct_x', 'gen_avg_pass_comp_pct_y', 'gen_avg_pass_tds_allowed_x',
			   'gen_avg_pass_tds_allowed_y', 'gen_avg_pass_tds_x', 'gen_avg_pass_tds_y', 'gen_avg_pass_yards_per_attempt_allowed_x',
			   'gen_avg_pass_yards_per_attempt_allowed_y', 'gen_avg_pass_yards_per_attempt_x', 'gen_avg_pass_yards_per_attempt_y',
			   'gen_avg_sack_yards_allowed_x', 'gen_avg_sack_yards_allowed_y', 'gen_avg_sack_yards_x',
			   'gen_avg_sack_yards_y', 'gen_avg_sacks_allowed_x', 'gen_avg_sacks_allowed_y',
			   'gen_avg_sacks_x', 'gen_avg_sacks_y', 'gen_avg_top_allowed_x', 'gen_avg_top_allowed_y',
			   'gen_avg_total_yards_allowed_x', 'gen_avg_total_yards_allowed_y', 'gen_avg_total_yards_x',
			   'gen_avg_total_yards_y', 'gen_first_downs_x', 'gen_first_downs_y', 'gen_fumbles_x', 'gen_fumbles_y',
			   'gen_interceptions_x', 'gen_interceptions_y', 'gen_ints_per_attempt_x', 'gen_ints_per_attempt_y',
			   'gen_op_avg_penalty_yards_x', 'gen_op_avg_penalty_yards_y', 'gen_op_first_downs_x', 'gen_op_first_downs_y', 'gen_op_pass_td_x',
			   'gen_op_pass_td_y', 'gen_op_pass_yards_per_attempt_x', 'gen_op_pass_yards_per_attempt_y', 'gen_op_penalty_yards_x', 'gen_op_penalty_yards_y',
			   'gen_op_sack_yards_x', 'gen_op_sack_yards_y', 'gen_op_sacks_x', 'gen_op_sacks_y', 'gen_op_top_x', 'gen_op_top_y', 'gen_op_total_yards_x',	
			   'gen_op_total_yards_y', 'gen_pass_comp_pct_x', 'gen_pass_comp_pct_y', 'gen_pass_td_x', 'gen_pass_td_y', 'gen_pass_yards_per_attempt_x',	
			   'gen_pass_yards_per_attempt_y', 'gen_sack_yards_x', 'gen_sack_yards_y', 'gen_sacks_x', 'gen_sacks_y', 'gen_total_yards_x', 'gen_total_yards_y']
	for elt in columns:
		df = df.drop(elt, axis=1)


	

	return df


# eigth function needs to scrape the elos for each team and add the values to two new columns in the dataframe (h_elo_pre, a_elo_pre)

def add_elos(df):
	page = of.page('https://github.com/fivethirtyeight/data/tree/master/nfl-elo')
	div = page.find_all('div', {'class' : 'Box-body'})
	table = div[0].find_all('table')
	tbody = table[0].tbody
	a = tbody.find_all('a')
	link = a[1]['href']
	data = open_csv(link)

	newlist = data['date']
	newlist = newlist.tolist()
	dates = []
	for object1 in newlist:
		time = pd.to_datetime(object1, format='%Y/%m/%d')
		date = int(time.strftime('%Y%m%d'))
		dates.append(date)
	data['Date'] = dates
	

	subs = {
			'CHI':'Chicago Bears',
			'GB': 'Green Bay Packers',
			'PHI': 'Philadelphia Eagles',
			'WSH': 'Washington Redskins',
			'CAR': 'Carolina Panthers',
			'LAR': 'Los Angeles Rams',
			'NYJ': 'New York Jets',
			'BUF': 'Buffalo Bills',
			'MIN': 'Minnesota Vikings',
			'ATL': 'Atlanta Falcons',
			'CLE': 'Cleveland Browns',
			'TEN': 'Tennessee Titans',
			'MIA': 'Miami Dolphins',
			'BAL': 'Baltimore Ravens',
			'JAX': 'Jacksonville Jaguars',
			'KC': 'Kansas City Chiefs',
			'LAC': 'Los Angeles Chargers',
			'IND': 'Indianapolis Colts',
			'SEA': 'Seattle Seahawks',
			'CIN': 'Cincinnati Bengals',
			'TB': 'Tampa Bay Buccaneers',
			'SF': 'San Francisco 49ers',
			'ARI': 'Arizona Cardinals',
			'DET': 'Detroit Lions',
			'DAL': 'Dallas Cowboys',
			'NYG': 'New York Giants',
			'NE': 'New England Patriots',
			'PIT': 'Pittsburgh Steelers',
			'NO': 'New Orleans Saints',
			'HOU': 'Houston Texans',
			'OAK': 'Oakland Raiders',
			'DEN': 'Denver Broncos',

		}

	h_teams = data['team1'].map(subs)
	a_teams = data['team2'].map(subs)
	data['h_elo_pre'] = data['elo1_pre']
	data['a_elo_pre'] = data['elo2_pre']


	cols = ['date', 'season', 'neutral', 'playoff', 'team1', 'team2', 'elo_prob1', 'elo_prob2', 'elo1_post', 'elo2_post',
			'qbelo1_pre', 'qbelo2_pre', 'qb1', 'qb2', 'qb1_value_pre', 'qb2_value_pre', 'elo1_pre', 'elo2_pre',
			'qb1_adj', 'qb2_adj', 'qbelo_prob1', 'qbelo_prob2', 'qb1_game_value', 'qb2_game_value',
			'qb1_value_post', 'qb2_value_post', 'qbelo1_post', 'qbelo2_post', 'score1', 'score2']
	for elt in cols:
		data = data.drop(elt, axis=1)

	data['h_team'] = h_teams	
	data['a_team'] = a_teams	
	merged = pd.merge(df, data, on=['a_team', 'h_team', 'Date'], how='inner')
	print(merged)
	merged.write_csv(fn='nfl_2019_week9_expanded.csv')


	return merged




# ninth function needs to scrape the moneylines and add the values to two new columns in the dataframe(h_ML, a_ML)

def get_ml(link='https://www.bovada.lv/services/sports/event/v2/events/A/description/', sport='football/nfl'):
	full_link = link + sport
	# print(full_link)
	bov_json = r.get(full_link).json()
	bov_events = bov_json[0]['events']
	# print(bov_events)
	lines = [parse_event(e) for e in bov_events]
	# print(lines)
	ml_df = turn_into_df(lines)
	print(ml_df)
	df = add_mls_to_main(ml_df)

	return df





def parse_event(event):
	sport = event['sport']
	game_id = event['id']
	a_team, h_team = teams(event)
	display_groups = event['displayGroups'][0]
	markets = display_groups['markets']
	a_ml, h_ml = parse_markets(markets)

	data = [a_team, h_team, a_ml, h_ml]
	# print(data)

	return data
    
def parse_markets(markets):
	a_ml, h_ml = ["NaN" for _ in range(2)]
	for market in markets:
		desc = market['description']
		outcomes = market['outcomes']
		if desc == 'Moneyline':
			a_ml, h_ml = moneyline(outcomes)
	# print(a_ml)
	# print(h_ml)
	return a_ml, h_ml

def moneyline(outcomes):
	a_ml = 'NaN'
	h_ml = 'NaN'
	for outcome in outcomes:
		price = outcome['price']
		if outcome['type'] == 'A':
			a_ml = price['american']
		else:
			h_ml = price['american']

	return a_ml, h_ml

def teams(event):
    # returns away, home
	team_one = event['competitors'][0]
	team_two = event['competitors'][1]
	if team_one['home']:
		h_team = team_one['name']
		a_team = team_two['name']
	else:
		a_team = team_one['name']
		h_team = team_two['name']
	# print(h_team)
	# print(a_team)
	return a_team, h_team

def turn_into_df(data):
	df = pd.DataFrame()
	a_teams = []
	h_teams = []
	a_mls = []
	h_mls = []
	for x in range(len(data)):
		a_teams.append(data[x][0])
	for x in range(len(data)):
		h_teams.append(data[x][1])
	for x in range(len(data)):
		a_mls.append(data[x][2])
	for x in range(len(data)):
		h_mls.append(data[x][3])
	df['a_team'] = a_teams
	df['h_team'] = h_teams
	df['a_ML'] = a_mls
	df['h_ML'] = h_mls

	return df

def add_mls_to_main(df):
	df2 = open_csv(fn='nfl_2019_week9_expanded.csv')
	# print(df2)
	a_teams = df['a_team']
	h_teams = df['h_team']
	a_teams = a_teams.tolist()
	h_teams = h_teams.tolist()
	for x in range(len(a_teams)):
		if a_teams[x][-1] == ' ':
			a_teams[x] = a_teams[x][:-1:]
		if h_teams[x][-1] == ' ':
			h_teams[x] = h_teams[x][:-1:]
	df['a_team'] = a_teams
	df['h_team'] = h_teams
	merged = pd.merge(df, df2, on=['a_team', 'h_team'], how='inner')
	merged.write_csv(fn='nfl_2019_week9_expanded.csv')

	return merged

def get_dict_of_df():
	df = open_csv(fn='nfl_2019_week9_expanded.csv')
	dict1 = df.set_index('h_team').T.to_dict('list')
	print(dict1)

	return dict1




# tenth function needs to fix the train data and delete future game from dataframe

def fix_basic_train(df):
	# df = open_csv('nfl_history2.csv')
	# df = df[df.Date <= 20191028]

	cols = ['a_fourth_down_conv', 'a_third_down_conv', 'h_third_down_conv', 'h_fourth_down_conv']
	for elt in cols:
		df = df.drop(elt, axis=1)
	df.write_csv(fn='nfl_history2.csv')

	return df

def fix_advanced_train(df):
	df2 = open_csv(fn='nfl_history_with_stats.csv')
	
	df2 = pd.concat([df, df2])
	df2 = df2.sort_values('Date', ascending=True, na_position='first')

	# df3 = open_csv('week9_preds.csv') # whatever the most recent dataframe was for test purposes

	# cols = ['a_elo_pre', 'h_elo_pre', 'Home_team_gen_avg_rush_yards', 'Away_team_gen_avg_rush_yards',
	# 		'Away_team_gen_avg_penalties', 'Home_team_gen_avg_penalties', 'Away_team_gen_avg_turnovers',
	# 		'Home_team_gen_avg_turnovers', 'Away_team_gen_avg_pass_yards', 'Home_team_gen_avg_pass_yards',
	# 		'Home_team_gen_avg_time_of_possesion', 'Away_team_gen_avg_time_of_possesion', 'Home_team_gen_avg_score',
	# 		'Away_team_gen_avg_score', 'Away_team_gen_avg_points_allowed', 'Home_team_gen_avg_points_allowed',
	# 		'Date', 'h_win_1_score', 'h_win_0_score', 'a_team', 'h_team', 'h_ML_EV', 'a_ML_EV', 'h_ML_pick', 'a_ML_pick']


	df2.write_csv(fn='nfl_history_with_stats.csv')


def open_csv(fn = 'data.csv'):
	pkg_path = live.__path__[0] + '/' + '../data/'
	full_name = pkg_path + fn
	df = pd.read_csv(full_name)
	return df

def write_csv(fn = 'data.csv'):
	pkg_path = live.__path__[0] + '/' + '../data/'
	full_name = pkg_path + fn
	df.to_csv(full_name)


