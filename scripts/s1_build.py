import pandas as pd, numpy as np
U = 'data/'
b = pd.read_csv(U + 'ball_by_ball.csv')
m = pd.read_csv(U + 'matches.csv')
c = pd.read_csv(U + 'competitions.csv')

b['et'] = b.extras_type.fillna('none')
# --- ball legality / run accounting (extras1_runs is a type code, NOT runs) ---
b['is_wide'] = b.et.eq('wide')
b['is_nb'] = b.et.isin(['Overstep', 'other'])          # 'other' behaves as an extra delivery (not a legal ball)
b['legal'] = ~(b.is_wide | b.is_nb)
b['faced'] = ~b.is_wide                                  # balls faced by batter (no-balls count as faced)
b['pen'] = np.where(b.et.eq('Penalty'), 5, 0)
b['bat_runs'] = np.where(b.is_wide, 0, b.runs)
b['chg_runs'] = b.runs + b.is_wide.astype(int) + b.is_nb.astype(int)   # charged to bowler
b['team_runs'] = b.chg_runs + b.pen
# wickets
b['wkt_any'] = b.is_wicket & ~b.dismissal_type.eq('Retire Out')
b['wkt_bowler'] = b.is_wicket & ~b.dismissal_type.isin(['RunOut', 'Retire Out', 'Obstracting the field', 'Obstructing the field'])
b['out_striker'] = b.wkt_any & (b.dismissed_player_id.fillna(b.striker_id) == b.striker_id)

b = b.sort_values(['match_id', 'innings', 'innings_ball_num']).reset_index(drop=True)
g = b.groupby(['match_id', 'innings'])
b['legal_before'] = g.legal.cumsum() - b.legal.astype(int)
b['legal_after'] = g.legal.cumsum()
b['score_before'] = g.team_runs.cumsum() - b.team_runs
b['score_after'] = g.team_runs.cumsum()
b['wk_before'] = g.wkt_any.cumsum() - b.wkt_any.astype(int)
b['wk_after'] = g.wkt_any.cumsum()

# match info
mi = m.set_index('match_id')
b = b.join(mi[['comp_id', 'match_date', 'stage', 'knock_out', 'win_team_id', 'first_inn_revised_overs',
               'second_inn_revised_overs', 'revised_target']], on='match_id')
b = b.join(c.set_index('comp_id')[['match_format', 'season']].rename(columns={'season': 'comp_season'}), on='comp_id')
b['is_ipl'] = (b.match_format == 'T20').astype(int)
b['year'] = pd.to_datetime(b.match_date).dt.year

# innings length
reg = b.innings.isin([1, 2])
b['max_balls'] = 120
b.loc[(b.innings == 1) & b.first_inn_revised_overs.notna(), 'max_balls'] = b.first_inn_revised_overs
b.loc[(b.innings == 2) & b.second_inn_revised_overs.notna(), 'max_balls'] = b.second_inn_revised_overs
b.loc[b.innings >= 3, 'max_balls'] = 6

# first-innings totals -> target
tot1 = b[b.innings == 1].groupby('match_id').score_after.max()
inn1_last = b[b.innings == 1].groupby('match_id').tail(1).set_index('match_id')
inn1_ok = ((inn1_last.legal_after >= inn1_last.max_balls) | (inn1_last.wk_after >= 10))
b['target'] = b.match_id.map(tot1) + 1
b.loc[(b.innings == 2) & ~b.match_id.map(inn1_ok).fillna(False).astype(bool) & b.revised_target.isna(), 'target'] = np.nan
b.loc[(b.innings == 2) & b.revised_target.notna(), 'target'] = b.revised_target
print('inn2 rows with unknown target:', ((b.innings==2)&b.target.isna()).sum())
b.loc[b.innings != 2, 'target'] = np.nan

b['balls_left_b'] = (b.max_balls - b.legal_before).clip(lower=0)
b['balls_left_a'] = (b.max_balls - b.legal_after).clip(lower=0)
for s in ['b', 'a']:
    sc = b['score_before'] if s == 'b' else b['score_after']
    wk = b['wk_before'] if s == 'b' else b['wk_after']
    bl = b['balls_left_' + s]
    b['need_' + s] = b.target - sc
    b['rrr_' + s] = np.where(bl > 0, b['need_' + s] / bl * 6, np.where(b['need_' + s] > 0, 99, 0))
    b['crr_' + s] = np.where((b.max_balls - bl) > 0, sc / (b.max_balls - bl) * 6, 0)

# phase
b['phase'] = np.select([b.overid <= 6, b.overid <= 15], ['PP', 'MID'], 'DEATH')
b['phase_n'] = np.select([b.overid <= 6, b.overid <= 15], [0, 1], 2)
b.to_pickle('b1.pkl')
print(b.shape, b.legal.mean(), b.year.value_counts().sort_index().to_dict())
print('ids per name:', b.groupby('striker_id').striker_name.nunique().max(), b.groupby('bowler_id').bowler_name.nunique().max())
print(b.groupby('is_ipl').match_id.nunique())
