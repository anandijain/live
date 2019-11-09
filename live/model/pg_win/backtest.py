import pandas as pd
from live.modelling import train_model
import live

def open_csv(fn='nfl_one_train.csv'):
	pkg_path = live.__path__[0] + '/' + '../data/'
	full_name = pkg_path + fn
	df = pd.read_csv(full_name)
return df

def yo(odd):
    # to find the adjusted odds multiplier 
    # returns float
    if odd == 0:
        return 0
    if odd >= 100:
        return odd/100.
    elif odd < 100:
        return abs(100/odd)

def ev(prob, odd):
	ev = prob*yo(odd) - (1-prob)
	return ev
def back_test(df = open_csv()):
	num_rows = len(df)
	ts_row = num_rows*.66
	test_1 = num_rows *.83
	train_columns = ['a_elo_pre', 'h_elo_pre', 'Home_team_gen_avg_rush_yards', 'Away_team_gen_avg_rush_yards', 'Away_team_gen_avg_penalties', 'Home_team_gen_avg_penalties', 'Away_team_gen_avg_turnovers', 'Home_team_gen_avg_turnovers', 'Away_team_gen_avg_pass_yards', 'Home_team_gen_avg_pass_yards', 'Home_team_gen_avg_time_of_possesion', 'Away_team_gen_avg_time_of_possesion', 'Home_team_gen_avg_score', 'Away_team_gen_avg_score', 'Away_team_gen_avg_points_allowed', 'Home_team_gen_avg_points_allowed']

	train_set = df[:ts_row]
	test_df1 = df[ts_row:test_1]
	test_df2 = df[test_1:]
	test_dfs = [test_df1, test_df2]
	win_model = train_model(train_set)
	results = []
	for df in test_dfs:
		win_preds = win_model.predict_proba(df[train_columns])

		winners = list(df['h_win'])
		h_mls = list(df['h_ML'])
		a_mls = list(df['a_ML'])
		net = 0
		hnet = 0
		anet = 0
		for i in range(len(win_preds)):
			h_prob = win_preds[i][1]
			a_prob = win_preds[i][0]
			h_ml = h_mls[i]
			a_ml = a_mls[i]
			winner = winners[i]
			win_pred = win_preds[i]
			h_ev = ev(h_prob, h_ml)
			a_ev = ev(a_prob, a_ml)
			if h_ev > 0:
				if winner == 1:
					net += yo(h_ml)
					hnet+= yo(h_ml)
				if winner == 0:
					net -=1
					hnet -=1

			if a_ev > 0:
				if winner == 0:
					anet +=1
					net +=1
				if winner == 1:
					anet -=1
					net -=1
		results.append([net, hnet, anet])
	print('test1 net:', results[0][0])
	print('test1 hnet:', results[0][1])
	print('test1 anet:', results[0][2])
	print('test2 net:', results[1][0])
	print('test2 hnet:', results[1][1])
	print('test2 anet:', results[1][2])



















