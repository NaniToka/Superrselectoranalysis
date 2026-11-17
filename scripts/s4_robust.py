import pandas as pd, numpy as np
from s3_score import *

rng = np.random.RandomState(11)
base = pd.read_pickle('res_main.pkl')
P = prep(b)
match_ids = b.match_id.unique()
B = 300
out = {}
for role, W in [('bat', W_BAT), ('bowl', W_BOWL)]:
    pm, names = P[role]
    ids = base[role].index
    ranks = {p: [] for p in base[role].index}
    top10 = pd.Series(0, index=ids, dtype=float)
    top5 = pd.Series(0, index=ids, dtype=float)
    rk = pd.DataFrame(index=ids, columns=range(B), dtype=float)
    for i in range(B):
        samp = rng.choice(match_ids, len(match_ids), replace=True)
        mult = pd.Series(samp).value_counts()
        a = score(pm, names, W, mult=mult, min_hp=MIN_HP, min_m=MIN_HP_MATCHES)
        r = a['rank'].reindex(ids)
        rk[i] = r
        top10 += (r <= 10).fillna(False).astype(float)
        top5 += (r <= 5).fillna(False).astype(float)
    summ = pd.DataFrame({'name': base[role].name, 'base_rank': base[role]['rank'], 'base_score': base[role].score,
                         'p_top10': top10 / B, 'p_top5': top5 / B,
                         'median_rank': rk.median(axis=1), 'rank_lo': rk.quantile(.1, axis=1), 'rank_hi': rk.quantile(.9, axis=1)})
    out[role] = summ.sort_values('base_rank')
    print(role); print(out[role].head(16).round(2).to_string())

# ---------- sensitivity variants
variants = {
    'thr_P67': dict(thr_q=0.67), 'thr_P85': dict(thr_q=0.85), 'chase_only': dict(innings=2), 'lam_x0.5': dict(lam_scale=0.5),
    'lam_x1.5': dict(lam_scale=1.5), 'IPL_only': dict(league=1), 'T20I_only': dict(league=0)}
sens = {}
for role in ['bat', 'bowl']:
    sens[role] = {}
    for vn, kw in variants.items():
        kw = dict(kw)
        Pv = prep(b, **kw)
        mh = MIN_HP if vn not in ('IPL_only', 'T20I_only', 'chase_only') else 80
        mm = MIN_HP_MATCHES if vn not in ('IPL_only', 'T20I_only', 'chase_only') else 5
        pm, names = Pv[role]
        a = score(pm, names, W_BAT, min_hp=mh, min_m=mm)
        sens[role][vn] = a['rank']
    # weight perturbations
    wr = []
    for i in range(100):
        w = np.array([W_BAT['net'], W_BAT['wpa'], W_BAT['delta'], W_BAT['cons']]) * rng.uniform(0.7, 1.3, 4)
        w = w / w.sum()
        a = score(P[role][0], P[role][1], dict(net=w[0], wpa=w[1], delta=w[2], cons=w[3]))
        wr.append(a['rank'].reindex(base[role].index))
    sens[role]['weights_pm30'] = pd.concat(wr, axis=1).median(axis=1)
    sens[role]['weights_top10_freq'] = (pd.concat(wr, axis=1) <= 10).mean(axis=1)
pd.to_pickle((out, sens), 'res_robust.pkl')
for role in ['bat', 'bowl']:
    t = pd.DataFrame(sens[role]).reindex(base[role].index[:14])
    t.insert(0, 'name', base[role].name[:14]); t.insert(1, 'base', base[role]['rank'][:14])
    print(role); print(t.round(1).to_string())
