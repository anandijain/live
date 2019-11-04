
data = '/data/'

url = 'https://www.pro-football-reference.com'


bs_url = 'https://www.pro-football-reference.com/years/'


nfl_ref_lineup = ['Game_id', 'Date', 'Year', 'Start_time', 'Venue', 'Attendance', 'h_coach', 'a_coach', 'h_team', 'a_team', 'a_1stq', 'a_2ndq', 'a_3rdq', 'a_4thq', 'a_5thq', 'h_1stq', 'h_2ndq', 'h_3rdq', 'h_4thq', 'h_5thq', 'h_first_downs', 'h_rush_yds_tds', 'h_comp_att_yd_td_int', 'h_sacked_yards', 'h_net_pass_yards', 'h_total_yards', 'h_fumbles_lost', 'h_turnovers', 'h_penalty_yards', 'h_third_down_conv', 'h_fourth_down_conv', 'h_top', 'a_first_downs', 'a_rush_yds_tds', 'a_comp_att_yd_td_int', 'a_sacked_yards', 'a_net_pass_yards', 'a_total_yards', 'a_fumbles_lost', 'a_turnovers', 'a_penalty_yards', 'a_third_down_conv', 'a_fourth_down_conv', 'a_top', 'spread', 'over_under']

nfl_metas = ['Coach', 'Coach_h', 'Date', 'Start_time', 'Stadium', 'Attendance', 'time_of_game']

nfl_p_cols = ['Game_id', 'Possesion', 'Quarter', 'Time', 'Down', 'ToGo', 'Location', 'Detail', 'h_team_score', 'a_team_score', 'EPB', 'EPA', 'h_team', 'a_team', 'pg_spread', 'pgover_under']

midgame_stat_cols = ['a_team', 'h_team', 'a_team_C/ATT', 'a_team_pass_yards', 'a_team_avg_pass_yards', 'a_team_pass_tds', 'a_team_pass_ints', 'a_team_sacked', 'a_team_none', 'a_team_QB_rating', 'h_team_C/ATT', 'h_team_pass_yards', 'h_team_avg_pass_yards', 'h_team_pass_tds', 'h_team_pass_ints', 'h_team_sacked', 'h_team_none', 'h_team_QB_rating', 'a_team_carries', 'a_team_rush_yards', 'a_team_avg_rush', 'a_team_rush_tds', 'a_team_long_rush', 'h_team_carries', 'h_team_rush_yards', 'h_team_avg_rush_yards', 'h_team_rush_tds', 'h_team_long_rush', 'a_catches', 'a_recieving_yards', 'a_avg_recieving_yards', 'a_catching_tds', 'a_team_long_pass', 'a_team_total_targets', 'h_catches', 'h_recieving_yards', 'h_avg_recieving_yards', 'h_catching_tds', 'h_team_long_pass', 'h_team_total_targets', 'a_team_fumbles', 'a_team_fumbles_lost', 'a_team_fumbles_recovered', 'h_team_fumbles', 'h_team_fumbles_lost', 'h_team_fumbles_recovered', 'a_team_tackles', 'a_team_solo_tackles', 'a_team_sacks', 'a_team_tackles_for_loss', 'a_team_pd', 'a_team_QB_hits', 'a_team_defensive_tds', 'h_team_tackles', 'h_team_solo_tackles', 'h_team_sacks', 'h_team_tackles_for_loss', 'h_team_pd', 'h_team_QB_hits', 'h_team_defensive_tds', 'a_team_interceptions', 'a_team_yards_off_interceptions', 'a_team_touchdowns_off_interceptions', 'h_team_interceptions', 'h_team_yards_off_interception', 'h_team_touchdowns_interceptions', 'a_team_number_of_kick_returns', 'a_team_yards_on returns', 'a_team_avg_kick_return', 'a_team_long_return', 'a_team_return_touchdowns', 'h_team_number_of_kick_returns', 'h_team_yards_on returns', 'h_team_avg_kick_return', 'h_team_long_return', 'h_team_return_touchdowns', 'a_team_number_of_punt_returns', 'a_team_yards_on_punt_returns', 'a_team_avg_punt_return', 'a_team_long_punt_return', 'a_team_punt_return_tds', 'h_team_number_of_punt_returns', 'h_team_yards_on_punt_returns', 'h_team_avg_punt_return', 'h_team_long_punt_return', 'h_team_punt_return_tds', 'a_team_field_goals', 'a_team_field_goal_pctg', 'a_team_long_field_goal', 'a_team_extra_points', 'a_team_kicking_points', 'h_team_field_goals', 'h_team_field_goal_pctg', 'h_team_long_field_goal', 'h_team_extra_points', 'h_team_kicking_points', 'a_team_number_of_punts', 'a_team_total_punt_yards', 'a_team_avg_punt', 'a_team_touchbacks_off_punt', 'a_team_punts_within_20_yard_line', 'a_team_long_punt', 'h_team_number_of_punts', 'h_team_total_punt_yards', 'h_team_avg_punt', 'h_team_touchbacks_off_punt', 'h_team_punts_within_20_yard_line', 'h_team_long_punt']


midgame_turnover_cols = [ 'a_team', 'a_team_fumbles', 'a_team_fumbles_lost', 'a_team_fumbles_recovered', 'h_team', 'h_team_fumbles', 'h_team_fumbles_lost', 'h_team_fumbles_recovered', 'a_team_interceptions', 'a_team_yards_off_interceptions', 'a_team_touchdowns_off_interceptions', 'h_team', 'h_team_interceptions', 'h_team_yards_off_interception', 'h_team_touchdowns_interceptions']


players_cols = ['Game_id', 'Date', 'Year', 'Start_time', 'Venue', 'Attendance', 'a_team', 'h_team', 'a_1stq', 'a_2ndq', 'a_3rdq', 'a_4thq', 'a_5thq', 'h_1stq', 'h_2ndq', 'h_3rdq', 'h_4thq', 'h_5thq', 'spread', 'over_under', 'H_QB', 'H_player2', 'H_player3', 'H_player4', 'H_player5', 'H_player6', 'A_QB', 'A_player2', 'A_player3', 'A_player4', 'A_player5', 'A_player6']
