"""Flag matches whose ball data contradicts the recorded result (see report, Section 2)."""
import pandas as pd, numpy as np
b = pd.read_pickle('b1.pkl'); m = pd.read_csv('data/matches.csv').set_index('match_id')
i1 = b[b.innings == 1].groupby('match_id').tail(1).set_index('match_id')
i2 = b[b.innings == 2].groupby('match_id').tail(1).set_index('match_id')
d = pd.DataFrame({'t1': i1.score_after, 't2': i2.score_after, 'need2': i2.need_a, 'bat2': i2.batting_team_id}).join(m[['win_team_id', 'result', 'revised_target']])
d = d[d.t2.notna()]
d['chaser_won'] = (d.win_team_id == d.bat2)
so = set(b[b.innings >= 3].match_id)
d = d[~d.index.isin(so) & d.win_team_id.notna()]
byruns = d.result.str.contains('run', case=False, na=False)
d['margin'] = d.result.str.extract(r'by (\d+) run', flags=2)[0].astype(float)
d['dl'] = d.revised_target.notna() | d.result.str.contains('D/?L', case=False, na=False)
flagC = (~d.chaser_won) & (d.need2 <= 0)
flagB = d.chaser_won & (d.need2 > 15)
flagA = (~d.dl) & byruns & d.margin.notna() & (((d.t1 - d.t2) - d.margin).abs() > 12)
bad = d[flagA | flagB | flagC].index
pd.Series(bad).to_csv('bad_matches.csv', index=False)
print('flagged matches:', len(bad))
