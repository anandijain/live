import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import live

def open_csv(fn='nfl_one_train.csv'):
	pkg_path = live.__path__[0] + '/' + '../data/'
	full_name = pkg_path + fn
	df = pd.read_csv(full_name)
return df

def gradient_boosting():
	win_model = GradientBoostingClassifier()
	return win_model

def standardize_data(x):
	df = StandardScaler().fit_transform(x)
	return df

def train_model(df = open_csv()):
	all_columns = ['a_elo_pre', 'h_elo_pre', 'Home_team_gen_avg_rush_yards', 'Away_team_gen_avg_rush_yards', 'Away_team_gen_avg_penalties', 'Home_team_gen_avg_penalties', 'Away_team_gen_avg_turnovers', 'Home_team_gen_avg_turnovers', 'Away_team_gen_avg_pass_yards', 'Home_team_gen_avg_pass_yards', 'Home_team_gen_avg_time_of_possesion', 'Away_team_gen_avg_time_of_possesion', 'Home_team_gen_avg_score', 'Away_team_gen_avg_score', 'Away_team_gen_avg_points_allowed', 'Home_team_gen_avg_points_allowed', 'h_win']
	train_columns = ['a_elo_pre', 'h_elo_pre', 'Home_team_gen_avg_rush_yards', 'Away_team_gen_avg_rush_yards', 'Away_team_gen_avg_penalties', 'Home_team_gen_avg_penalties', 'Away_team_gen_avg_turnovers', 'Home_team_gen_avg_turnovers', 'Away_team_gen_avg_pass_yards', 'Home_team_gen_avg_pass_yards', 'Home_team_gen_avg_time_of_possesion', 'Away_team_gen_avg_time_of_possesion', 'Home_team_gen_avg_score', 'Away_team_gen_avg_score', 'Away_team_gen_avg_points_allowed', 'Home_team_gen_avg_points_allowed']
	x = df[train_columns]
	y = df[['h_win']]
	x = standardize_data(x)
	win_model = gradient_boosting()
	win_model.fit(x, y)
	return win_model