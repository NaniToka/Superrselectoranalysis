import pandas as pd, numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier as HGC, HistGradientBoostingRegressor as HGR
b = pd.read_pickle('b2.pkl'); reg = b.innings.isin([1, 2])
K = 5; KPRIOR = 300.0   # pseudo-balls of shrinkage toward average quality (0)

def loo_rating(df, pid, vcol, mask):
    d = df[mask & df[vcol].notna()]
    tot = d.groupby(pid)[vcol].agg(['sum', 'count'])
    pm = d.groupby([pid, 'match_id'])[vcol].agg(['sum', 'count']).rename(columns={'sum': 's_m', 'count': 'n_m'})
    key = pd.MultiIndex.from_arrays([df[pid], df.match_id])
    j = pm.reindex(key)
    S = tot['sum'].reindex(df[pid]).values; N = tot['count'].reindex(df[pid]).values
    s_m = j.s_m.fillna(0).values; n_m = j.n_m.fillna(0).values
    return (S - s_m) / (N - n_m + KPRIOR) * 100      # runs above expected per 100 balls, excluding this match

# quality of the bowler faced (for batter models) and of the batter faced (for bowler models)
b['opp_bowl_q'] = loo_rating(b, 'bowler_id', 'v_bowl', reg)
b['opp_bat_q'] = loo_rating(b, 'striker_id', 'v_bat', reg & b.faced)
print(b[reg][['opp_bowl_q', 'opp_bat_q']].describe().round(2))
feat0 = ['innings', 'overid', 'wk_before', 'balls_left_b', 'score_before', 'crr_b', 'need_b', 'rrr_b_c', 'is_ipl']

def oof(mask, target, kind, feats):
    d = b[mask]; out = pd.Series(np.nan, index=b.index)
    for k in range(K):
        tr, te = d[d.fold != k], d[d.fold == k]
        M = HGR if kind == 'reg' else HGC
        mdl = M(max_iter=150, learning_rate=0.06, max_leaf_nodes=24, min_samples_leaf=200, l2_regularization=1.0, random_state=k)
        mdl.fit(tr[feats], tr[target].astype(float if kind == 'reg' else int))
        out.loc[te.index] = mdl.predict(te[feats]) if kind == 'reg' else mdl.predict_proba(te[feats])[:, 1]
    return out
fb = feat0 + ['opp_bowl_q']; fw = feat0 + ['opp_bat_q']
b['E_bat_runs'] = oof(reg & b.faced, 'bat_runs', 'reg', fb)
b['P_out_bat'] = oof(reg & b.faced, 'out_striker', 'clf', fb)
b['E_chg_runs'] = oof(reg, 'chg_runs', 'reg', fw)
b['P_wkt_bowl'] = oof(reg, 'wkt_bowler', 'clf', fw)
b['v_bat'] = np.where(b.faced & reg, (b.bat_runs - b.E_bat_runs) - b.lam * (b.out_striker.astype(float) - b.P_out_bat), np.nan)
b['v_bowl'] = np.where(reg, (b.E_chg_runs - b.chg_runs) + b.lam * (b.wkt_bowler.astype(float) - b.P_wkt_bowl), np.nan)
b.to_pickle('b3.pkl')
print('done; mean v_bat', b.v_bat.mean(), 'mean v_bowl', b.v_bowl.mean())
