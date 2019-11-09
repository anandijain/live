import os
import sys

import pandas as pd
import bs4
import requests as r
import live.scrape.pregame.nfl_macros as m
import live.scrape.pregame.openers_2 as of
from lxml import html
import requests


def main(start='199909120was', stop='201909160nyj'):
	data_root = '.' + m.data
	df = pd.read_csv('nfl_boxes.csv')
	df2 = df['urls'].tolist()
	last = '/boxscores/' + start + '.htm'
	index = df2.index(last)
	urls = df2[index:]

	# fn = 'pbp_w_poss.csv'
	# file = open(fn, 'w')

	# columns = m.nfl_p_cols
	# for i, j in enumerate(columns):
	# 	file.write(str(j))
	# 	if i == len(columns) -1:
	# 		file.write('\n')
	# 	else:
	# 		file.write(',')

	# file.close()

	for url in urls:
		p = of.page(m.url + url)
		fn_data = path_info_from_page(p, url)
		print(fn_data)
		if fn_data is None:
			return

		year, game_id = fn_data
		folder = 'pbp'
		path = data_root + folder

		try:
			int_year = int(year)
		except ValueError:
			print('skipping playoff game')
			continue
		try:
			os.makedirs(path)
		except FileExistsError:
			print('file: {} exists'.format(game_id))
			pass

		gen_stats(path, page=p, game_id=game_id)
		# pbp(path, page=p, game_id=game_id)





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





	fn = 'nfl_history.csv'
	file = open(fn, 'a')

	teams = team_names(path, page, game_id)
	meta = metas(path, page, game_id)
	teams_stat = team_stats(path, page, game_id)
	bet = bet_info(path, page, game_id)
	coach = coaches(path, page, game_id)
	# player = get_players(path, page, game_id)
	a_qs_none = [0, 0, 0, 0, 0]
	h_qs_none = [0, 0, 0, 0, 0]
	bet_none = [0, 0]
	teams_stats_none = [0, 0, 0, 0, 0, 0, 0, 
						0, 0, 0, 0, 0, 0, 0,
						0, 0, 0, 0, 0, 0, 0,
						0, 0, 0]

	for i, j in enumerate(meta):
		file.write(str(j))
		file.write(',')

	for i, j in enumerate(coach):
		file.write(str(j))
		file.write(',')

	for i, j in enumerate(teams):
		file.write(str(j))
		file.write(',')

	for i, j in enumerate(a_qs):  # for past games
		file.write(str(j))
		file.write(',')

	# for i, j in enumerate(a_qs_none):  # for future games
	# 	file.write(str(j))
	# 	file.write(',')

	for i, j in enumerate(h_qs): # for past games
		file.write(str(j))
		file.write(',')

	# for i, j in enumerate(h_qs_none): # for future games
	# 	file.write(str(j))
	# 	file.write(',')

	for i, j in enumerate(teams_stat): # for past games
		file.write(str(j))
		file.write(',')

	# for i, j in enumerate(teams_stats_none): # for future games
	# 	file.write(str(j))
	# 	file.write(',')

	for i, j in enumerate(bet): # for past games
		file.write(str(j))
		if i == len(bet) -1:
			file.write('\n')
		else:
			file.write(',')

	# for i, j in enumerate(bet_none): # for future games
	# 	file.write(str(j))
	# 	if i == len(bet_none) -1:
	# 		file.write('\n')
	# 	else:
	# 		file.write(',')


	# for i, j in enumerate(player):
	# 	file.write(str(j))
	# 	if i == len(player) -1:
	# 		file.write('\n')
	# 	else:
	# 		file.write(',')

	print(fn)
	file.close()



def comments(page):
	comments = page.findAll(text=lambda text:isinstance(text, bs4.Comment))
	return comments

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
				print(links)
				newlinks.append(links)

		if i << 1990:
			for elt in weeks_short:
				url2 = url +  str(i) + '/' + str(elt) + '.htm'
				page = of.page(url2)
				links = page.find_all('td', {'class' : 'right gamelink'})
				print(links)
				newlinks.append(links)


		for x in range(len(newlinks)):
			for i in range(len(newlinks[x])):
				real = newlinks[x][i].a['href']
				print(real)
				newlinks2.append(real)

	df = pd.read_csv('2019_boxes.csv')
	df['urls'] = newlinks2
		


	file.close()
	return newlinks2



def team_names(path, page=of.page(m.url + '/boxscores/201901200kan.htm'), game_id='201901200kan'):
	names = page.find_all('div', {'class' : 'scorebox'})
	names = names[0].find_all('strong')
	h_team = names[0].text
	h_team = h_team[1:]
	h_team = h_team[:-1]

	a_team = names[2].text
	a_team = a_team[1:]
	a_team = a_team[:-1]

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

	return (meta_data)

def bet_info(path, page=of.page(m.url + '/boxscores/199101200buf.htm'), game_id='199101200buf'):
	y1 = game_id[0]
	y2 = game_id[1]
	y3 = game_id[2]
	y4 = game_id[3]
	year = int(str(y1) + str(y2) + str(y3) + str(y4))
	cs = comments(page)

	# if int(year) == 2010:
	# info = cs[16]
	# else:
	info = cs[15]

	info = bs4_parse(info)
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

	return(bet_info)





def team_stats(path, page=of.page(m.url + '/boxscores/201901200kan.htm'), game_id='201901200kan'):
	y1 = game_id[0]
	y2 = game_id[1]
	y3 = game_id[2]
	y4 = game_id[3]
	year = int(str(y1) + str(y2) + str(y3) + str(y4))
	cs = comments(page)

	# if int(year) >= 1999:
	teams_stats = cs[21]

	# if int(year) >= 2019:
	# teams_stats = cs[21]

	# if int(year) >= 1994 & int(year) <= 1998:
	# teams_stats = cs[20]

	# if int(year) <= 1994:
	# teams_stats = cs[19]

	# if int(year) == 2010:
	# teams_stats = cs[25]

	team_stats = bs4_parse(teams_stats)
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



	return (team_stats_h, team_stats_a)

def coaches(path, page=of.page(m.url + '/boxscores/201901200kan.htm'), game_id='201901200kan'):
	coaches = page.find_all('div', {'class' : 'datapoint'})
	coaches2 = []
	for coach in coaches:
		c = coach.find_all('a')
		d = c[0]['href']
		coaches2.append(d)

	return coaches2


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



def bs4_parse(text):
	return bs4.BeautifulSoup(text, 'html.parser')

def write_header():
	fn = 'nfl_history.csv'
	file = open(fn, 'w')

	columns = m.nfl_ref_lineup
	for i, j in enumerate(columns):
		file.write(str(j))
		if i == len(columns) -1:
			file.write('\n')
		else:
			file.write(',')

	file.close()


def pbp(path, page, game_id):
	y1 = game_id[0]
	y2 = game_id[1]
	y3 = game_id[2]
	y4 = game_id[3]
	# y = game_id[0:3]
	year = int(str(y1) + str(y2) + str(y3) + str(y4))
	cs = comments(page)



	# if int(year) >= 1994 & int(year) <= 1999:
	for x in range(len(cs)):
		if len(cs[x]) > 80000:
			pbp_c = cs[x]


			pbp_raw = bs4.BeautifulSoup(pbp_c, 'html.parser')
			pbp = pbp_raw.find('table', {'id': 'pbp'})
			tbody = pbp.tbody
			rows = tbody.find_all('tr')



			fn = 'pbp_w_poss.csv'
			file = open(fn, 'a+')

			# num_cols = len(m.nfl_p_cols)
			# columns = m.nfl_p_cols
			# for i, j in enumerate(columns):
			# 	file.write(str(j))
			# 	if i == len(columns) -1:
			# 		file.write('\n')
			# 	else:
			# 		file.write(',')



			bets = bet_info(path, page, game_id)

			# for i, col in enumerate(m.nfl_p_cols):
			# 	file.write(str(col))
			# 	if i == num_cols - 1:
			# 		file.write('\n')
			# 	else:
			# 		file.write(',')

			teams = team_names(path, page, game_id)
			for row in rows:
				row_len = len(row)
				link = row.find_all('a')
				if len(row) != 1 and len(row) != 21:
					try:
						link = link[2]['href']
						link = link.replace('.htm', '')
						link = (m.url + link + '/gamelog/')
						# print(link)
						page = requests.get(link)
						page = html.fromstring(page.content)
						playerlog = page.xpath('//*[@id="stats"]/tbody//tr/td[9]/a/@href')
						# print(playerlog)
						team_name = page.xpath('//*[@id="stats"]/tbody//tr/td[6]/a/text()')
						# print(team_name)
						game_id2 = '/boxscores/' + game_id
						file.write(str(game_id + ','))
						possesion = []
						for x in range(len(playerlog)):
							# print(playerlog[x])
							# print(game_id2)
							if game_id2 == playerlog[x]:
								poss = team_name[x]
								print('helloworld')
								print(poss)
								# file.write(str(poss + ','))
								possesion.append(poss)
						print(possesion[0])
						file.write(str(possesion[0] + ','))
					except IndexError:
						file.write(str(game_id + ','))
						file.write('N/A' + ',')
				else:
					pass
					
				try:
					for j, item in enumerate(row):
						yup = item.text
						yup = yup.replace(',','')
						file.write(yup)
						if len(row) != 1 and len(row) != 21:
							file.write(',')
						else:
							file.write('\n')
				except AttributeError:
					pass
				if len(row) != 1 and len(row) != 21:
					for i, j in enumerate(teams):
						file.write(str(j))
						file.write(',')

					for i, j in enumerate(bets):
						file.write(str(j))
						if i == len(bets) - 1:
							file.write('\n')
						else:
							file.write(',')
				else:
					pass
					# print(fn)
			file.close()


def get_players(path, page=of.page(m.url + '/boxscores/201901200kan.htm'), game_id='201901200kan'):
	y1 = game_id[0]
	y2 = game_id[1]
	y3 = game_id[2]
	y4 = game_id[3]
	year = int(str(y1) + str(y2) + str(y3) + str(y4))
	cs = comments(page)

	# if int(year) >= 1980 & int(year) <= 1993:
	# 	oplayers = cs[20]
	# 	dplayers = cs[24]
	# 	o_special_t = cs[25]
	# 	d_special_t = cs[29]

	# if int(year) >= 1994 & int(year) <= 1998:
	# 	oplayers = cs[24]
	# 	dplayers = cs[25]
	# 	o_special_t = cs[29]
	# 	d_special_t = cs[30]

	# if int(year) >= 1999 & int(year) <= 2011:
	# 	oplayers = cs[25]
	# 	dplayers = cs[29]
	# 	o_special_t = cs[30]
	# 	d_special_t = cs[31]
	# 	h_starters = cs[32]
	# 	a_starters = cs[33]

	# if int(year) >= 2012:
	# 	h_players = cs[34]
	# 	a_players = cs[35]
	# 	h_players = p.bs4_parse(h_players)
	# 	a_players = p.bs4_parse(a_players)
	# 	h_player_pos = h_players.find_all('td', {'class' : 'left'})
	# 	a_player_pos = a_players.find_all('td', {'class' : 'left'})
	# 	h_positions = []
	# 	for x in range(len(h_player_pos)):
	# 		str_pos = str(h_player_pos[x])
	# 		position = str_pos.split('>')
	# 		position = position[1].split('<')
	# 		h_position = position[0]
	# 		h_positions.append(h_position)
	# 	a_positions = []
	# 	for x in range(len(a_player_pos)):
	# 		str_pos = str(a_player_pos[x])
	# 		position = str_pos.split('>')
	# 		position = position[1].split('<')
	# 		a_position = position[0]
	# 		a_positions.append(a_position)
	# 	h_players = h_players.find_all('a')
	# 	a_players = a_players.find_all('a')
	# 	h_players = str(h_players)
	# 	a_players = str(a_players)
	# 	h_player_pos = str(h_player_pos)
	# 	a_player_pos = str(a_player_pos)
	# 	h_players = h_players.split(',')
	# 	a_players = a_players.split(',')
	# 	h_player_pos = h_player_pos.split(',')
	# 	a_player_pos = a_player_pos.split(',')


	# 	h_players_r = []
	# 	for elt in h_players:
	# 		h = elt.split('.htm')
	# 		ma = h[0].split('/')
	# 		player_id = ma[-1]
	# 		h_players_r.append(player_id)

	# 	a_players_r = []
	# 	for elt in a_players:
	# 		h = elt.split('.htm')
	# 		ma = h[0].split('/')
	# 		player_id = ma[-1]
	# 		a_players_r.append(player_id)

	# 	h_player_pos_r = []
	# 	for elt in h_player_pos:
	# 		h = elt.split('>')
	# 		ma = h[1].split('<')
	# 		player_pos = ma[0]
	# 		h_player_pos_r.append(player_pos)

	# 	a_player_pos_r = []
	# 	for elt in a_player_pos:
	# 		h = elt.split('>')
	# 		ma = h[1].split('<')
	# 		player_pos = ma[0]
	# 		a_player_pos_r.append(player_pos)

	# 	for x in range(len(h_players_r)):
	# 		h_players_r[x] = [h_players_r[x] ,h_player_pos_r[x]]

	# 	for x in range(len(a_players_r)):
	# 		a_players_r[x] = [a_players_r[x] ,a_player_pos_r[x]]

	# 	players = [h_players_r, a_players_r]


	# oplayers = bs4_parse(oplayers)
	# dplayers = bs4_parse(dplayers)
	# o_special_t = bs4_parse(o_special_t)
	# d_special_t = bs4_parse(d_special_t)
	# oplayers = oplayers.find_all('a')
	# dplayers = dplayers.find_all('a')
	# o_special_t = o_special_t.find_all('a')
	# d_special_t = d_special_t.find_all('a')
	# oplayers = str(oplayers)
	# dplayers = str(dplayers)
	# o_special_t = str(o_special_t)
	# d_special_t = str(d_special_t)
	# oplayers = oplayers.split(',')
	# dplayers = dplayers.split(',')
	# o_special_t = o_special_t.split(',')
	# d_special_t = d_special_t.split(',')


	# oplayers_r = []
	# for elt in oplayers:
	# 	h = elt.split('.htm')
	# 	ma = h[0].split('/')
	# 	player_id = ma[-1]
	# 	oplayers_r.append(player_id)

	# dplayers_r = []
	# for elt in dplayers:
	# 	h = elt.split('.htm')
	# 	ma = h[0].split('/')
	# 	player_id = ma[-1]
	# 	dplayers_r.append(player_id)

	# o_special_t_r = []
	# for elt in o_special_t:
	# 	h = elt.split('.htm')
	# 	ma = h[0].split('/')
	# 	player_id = ma[-1]
	# 	o_special_t_r.append(player_id)

	# d_special_t_r = []
	# for elt in d_special_t:
	# 	h = elt.split('.htm')
	# 	ma = h[0].split('/')
	# 	player_id = ma[-1]
	# 	d_special_t_r.append(player_id)

	# if int(year) >= 2018:
	h_starters = cs[35]
	a_starters = cs[36]

	# if int(year) >= 1999:
	# h_starters = cs[32]
	# a_starters = cs[33]


	h_starters = bs4_parse(h_starters)
	a_starters = bs4_parse(a_starters)
	# print(a_starters)
	h_player_pos = h_starters.find_all('td', {'class' : 'left'})
	# print(h_player_pos)
	a_player_pos = a_starters.find_all('td', {'class' : 'left'})
	# print(h_player_pos)

	h_positions = []
	for x in range(len(h_player_pos)):
		str_pos = str(h_player_pos[x])
		position = str_pos.split('>')
		position = position[1].split('<')
		h_position = position[0]
		h_positions.append(h_position)

	a_positions = []
	for x in range(len(a_player_pos)):
		str_pos = str(a_player_pos[x])
		position = str_pos.split('>')
		position = position[1].split('<')
		a_position = position[0]
		a_positions.append(a_position)

	h_starters = h_starters.find_all('a')
	a_starters = a_starters.find_all('a')
	h_starters = str(h_starters)
	a_starters = str(a_starters)
	h_starters = h_starters.split(',')
	a_starters = a_starters.split(',')


	h_starters_r = []
	for elt in h_starters:
		h = elt.split('.htm')
		ma = h[0].split('/')
		player_id = ma[-1]
		h_starters_r.append(player_id)

	a_starters_r = []
	for elt in a_starters:
		h = elt.split('.htm')
		ma = h[0].split('/')
		player_id = ma[-1]
		a_starters_r.append(player_id)

	tups_h = []
	for x in range(len(h_starters_r)):
		name = h_starters_r[x]
		position = h_positions[x]
		tup = [name, position]
		tups_h.append(tup)
		# print(tups_h)

	tups_a = []
	for x in range(len(a_starters_r)):
		name = a_starters_r[x]
		position = a_positions[x]
		tup = [name, position]
		tups_a.append(tup)


	i = 0
	players = []
	# df = pd.DataFrame()
	for x in range(len(tups_h)):
		if tups_h[x][1] == 'QB':
			players.append(str(tups_h[x][0]))

	players.append(str(tups_h[1][0]))
	players.append(str(tups_h[2][0]))
	players.append(str(tups_h[3][0]))
	players.append(str(tups_h[4][0]))
	players.append(str(tups_h[5][0]))
			# df['h_QB'] = [str(tups_h[x][0])]
		# if tups_h[x][1] == 'RB':
		# 	df['h_RB'] = [str(tups_h[x][0])]
		# 	if len(df.iloc[0]) == 1:
		# 		df['h_RB'] = 'N/A'
		# if tups_h[x][1] == 'WR':
		# 	df['h_WR' + str(i)] = [str(tups_h[x][0])]
		# 	i += 1
		# 	if len(df.iloc[0]) == 3:
		# 		df['h_WR1'] = 'N/A'
		# 	if len(df.iloc[0]) ==4:
		# 		df['h_WR2'] = 'N/A'
		# if tups_h[x][1] == 'TE':
		# 	df['h_TE'] = [str(tups_h[x][0])]
		# 	if len(df.iloc[0]) == 5:
		# 		df['h_TE'] = 'N/A'
	i = 0
	for x in range(len(tups_a)):
		if tups_a[x][1] == 'QB':
			players.append(str(tups_a[x][0]))

	players.append(str(tups_a[1][0]))
	players.append(str(tups_a[2][0]))
	players.append(str(tups_a[3][0]))
	players.append(str(tups_a[4][0]))
	players.append(str(tups_a[5][0]))
			# df['a_QB'] = [str(tups_a[x][0])]
		# if tups_a[x][1] == 'RB':
		# 	df['a_RB'] = [str(tups_a[x][0])]
		# 	if len(df.iloc[0]) == 6:
		# 		df['a_RB'] = 'N/A'
		# if tups_a[x][1] == 'WR':
		# 	df['a_WR' + str(i)] = [str(tups_a[x][0])]
		# 	i += 1
		# 	if len(df.iloc[0]) == 8:
		# 		df['a_WR1'] = 'N/A'
		# 	if len(df.iloc[0]) ==9:
		# 		df['a_WR2'] = 'N/A'
		# if tups_a[x][1] == 'TE':
		# 	df['a_TE'] = [str(tups_a[x][0])]
		# 	if len(df.iloc[0]) == 10:
		# 		df['a_TE'] = 'N/A'


	# try:
	# 	players = df.iloc[0]
	# 	players2 = players.tolist()
	# except IndexError:
	# 	players2 = 'N/A'
	# 	pass



		# players = [h_starters_r, a_starters_r, oplayers_r, dplayers_r, o_special_t_r, d_special_t_r]

	# players = [oplayers_r, dplayers_r, o_special_t_r, d_special_t_r]

	return (players)




def get_table(page, table_id):  # given bs4 page and table id, finds table using bs4. returns tbody
	table = page.find('table', {'id': table_id})
	return table


def get_player_salaries(page=of.page(m.url + '/players/salary.htm')):
	table = page.find_all('table', {'id' : 'player_salaries'})
	table = table[0].prettify()
	df = pd.read_html(table)
	df = df[0]
	page.find_all('td', {'data-stat' : 'player'})
	players2 = []
	for player in players:
		l_of_p = player.find_all('a')
		hello = l_of_p[0]['href']
		players2.append(hello)

	df['Player'] = players2

	return df

def get_player_injuries(page=of.page(m.url + '/players/injuries.htm')):
	injuries = page.find_all('div', {'id' : 'all_injuries'})
	injuries = injuries[0].prettify()
	df = pd.read_html(injuries)
	df = df[0]
	players = page.find_all('th', {'class' : 'left'})
	players.remove(players[0])
	players.remove(players[0])
	players.remove(players[0])
	players2 = []
	for player in players:
		l_of_p = player.find_all('a')
		hello = l_of_p[0]['href']
		players2.append(hello)

	df['Player'] = players2


def get_coach_list(page=of.page(m.url + '/coaches/')):
	coach = page.find_all('table', {'id' : 'coaches'})
	coach = coach[0].prettify()
	df = pd.read_html(coach)
	df = df[0]
	coach_ids = page.find_all('td', {'class' : 'left'})
	coaches = []
	for coach_id in coach_ids:
		l_of_c = coach_id.find_all('a')
		hello = l_of_c[0]['href']
		coaches.append(hello)
	df['Coach'] = coaches


if __name__ == "__main__":
    main()
