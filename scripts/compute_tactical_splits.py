import pandas as pd, numpy as np

# Load b3 data with opposition quality
b = pd.read_pickle('b3.pkl')
thr = b.LI.quantile(0.75)
b['hp'] = b.LI >= thr

r_opp = pd.read_pickle('res_main_opp.pkl')
bat_top = r_opp['bat'].head(15)
bowl_top = r_opp['bowl'].head(15)

# 1. Batter Pace vs Spin
hp_bat = b[b.hp & b.faced & b.striker_id.isin(bat_top.index)].copy()
g_bat = hp_bat.groupby(['striker_id', 'striker_name', 'pace_or_spin'])
split_bat = g_bat.agg(
    balls=('bat_runs', 'size'),
    runs=('bat_runs', 'sum'),
    outs=('out_striker', 'sum'),
    fours=('is_four', 'sum'),
    sixes=('is_six', 'sum'),
    net_v=('v_bat', 'sum')
).reset_index()

split_bat['SR'] = (split_bat.runs / split_bat.balls * 100).round(1)
split_bat['avg'] = (split_bat.runs / split_bat.outs.clip(lower=1)).round(1)
split_bat['net_100'] = (split_bat.net_v / split_bat.balls * 100).round(2)
split_bat.to_csv('batter_pace_spin_splits.csv', index=False)
print("Saved batter_pace_spin_splits.csv")

# 2. Bowler Phase (PP, MID, DEATH)
hp_bowl = b[b.hp & b.bowler_id.isin(bowl_top.index)].copy()
g_bowl = hp_bowl.groupby(['bowler_id', 'bowler_name', 'phase'])
dots = hp_bowl[hp_bowl.legal & (hp_bowl.chg_runs == 0)].groupby(['bowler_id', 'phase']).size()

split_bowl = g_bowl.agg(
    balls=('bat_runs', 'size'),
    legal=('legal', 'sum'),
    runs=('chg_runs', 'sum'),
    wkts=('wkt_bowler', 'sum'),
    net_v=('v_bowl', 'sum')
).reset_index()

split_bowl['dots'] = split_bowl.set_index(['bowler_id', 'phase']).index.map(dots).fillna(0).values
split_bowl['econ'] = (split_bowl.runs / split_bowl.legal.clip(lower=1) * 6).round(2)
split_bowl['dot_pct'] = (split_bowl.dots / split_bowl.legal.clip(lower=1) * 100).round(1)
split_bowl['net_100'] = (split_bowl.net_v / split_bowl.legal.clip(lower=1) * 100).round(2)
split_bowl.to_csv('bowler_phase_splits.csv', index=False)
print("Saved bowler_phase_splits.csv")

