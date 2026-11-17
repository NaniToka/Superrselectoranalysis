import pandas as pd, numpy as np

b = pd.read_pickle('b2.pkl')
b = b[b.innings.isin([1, 2]) & b.LI.notna()].copy()
W_BAT = dict(net=0.35, wpa=0.30, delta=0.20, cons=0.15)
W_BOWL = dict(net=0.35, wpa=0.30, delta=0.20, cons=0.15)
MIN_HP = 150
MIN_HP_MATCHES = 8


def prep(df, thr_q=0.75, lam_scale=1.0, innings=None, league=None):
    d = df
    if innings is not None:
        d = d[d.innings == innings]
    if league is not None:
        d = d[d.is_ipl == league]
    thr = df.LI.quantile(thr_q)           # threshold always from full-sample LI distribution
    d = d.assign(hp=(d.LI >= thr))
    out = {}
    for role, pid, name, vcol, wcol, rowmask in [
        ('bat', 'striker_id', 'striker_name', 'v_bat', 'wpa_batter', d.faced),
        ('bowl', 'bowler_id', 'bowler_name', 'v_bowl', 'wpa_bowler', d.legal | ~d.legal)]:
        x = d[rowmask].copy()
        if lam_scale != 1.0:
            # recompute value with scaled wicket cost
            if role == 'bat':
                x['v'] = (x.bat_runs - x.E_bat_runs) - lam_scale * x.lam * (x.out_striker.astype(float) - x.P_out_bat)
            else:
                x['v'] = (x.E_chg_runs - x.chg_runs) + lam_scale * x.lam * (x.wkt_bowler.astype(float) - x.P_wkt_bowl)
        else:
            x['v'] = x[vcol]
        x['w'] = x[wcol]
        x['pid'] = x[pid]
        x['hpf'] = x.hp.astype(int)
        x['v_hp'] = x.v * x.hpf
        x['w_hp'] = x.w * x.hpf
        x['v_np'] = x.v * (1 - x.hpf)
        x['n_hp'] = x.hpf
        x['n_np'] = 1 - x.hpf
        x['v2_hp'] = x.v ** 2 * x.hpf
        x['v2_np'] = x.v ** 2 * (1 - x.hpf)
        x['w2_hp'] = x.w ** 2 * x.hpf
        pm = x.groupby(['pid', 'match_id']).agg(n_hp=('n_hp', 'sum'), n_np=('n_np', 'sum'), v_hp=('v_hp', 'sum'), w_hp=('w_hp', 'sum'),
                                                  v_np=('v_np', 'sum'), v2_hp=('v2_hp', 'sum'), v2_np=('v2_np', 'sum'), w2_hp=('w2_hp', 'sum')).reset_index()
        pm['hit'] = ((pm.n_hp >= 6) & (pm.v_hp > 0)).astype(int)
        pm['elig_m'] = (pm.n_hp >= 6).astype(int)
        names = x.groupby('pid')[name].agg(lambda s: s.iloc[0])
        out[role] = (pm, names)
    return out


def eb_shrink(mean, n, s2):
    """Empirical-Bayes shrinkage of per-player means toward the (n-weighted) grand mean."""
    mu = np.average(mean, weights=n)
    noise = np.average(s2 / n, weights=n)
    tau2 = max(np.var(mean) - noise, 1e-9)
    wgt = tau2 / (tau2 + s2 / n)
    return mu + wgt * (mean - mu), wgt


def score(pm, names, weights, mult=None, min_hp=MIN_HP, min_m=MIN_HP_MATCHES, return_all=False):
    if mult is not None:
        pm = pm.assign(k=pm.match_id.map(mult).fillna(0))
        for c in ['n_hp', 'n_np', 'v_hp', 'w_hp', 'v_np', 'v2_hp', 'v2_np', 'w2_hp', 'hit', 'elig_m']:
            pm[c] = pm[c] * pm.k
    a = pm.groupby('pid')[['n_hp', 'n_np', 'v_hp', 'w_hp', 'v_np', 'v2_hp', 'v2_np', 'w2_hp', 'hit', 'elig_m']].sum()
    a = a[(a.n_hp >= min_hp) & (a.elig_m >= min_m) & (a.n_np >= 100)].copy()
    a['net_hp'] = a.v_hp / a.n_hp * 100
    a['net_np'] = a.v_np / a.n_np * 100
    a['wpa_hp'] = a.w_hp / a.n_hp * 100
    a['delta'] = a.net_hp - a.net_np
    # per-ball variances (x100 scale)
    s2_hp = (a.v2_hp / a.n_hp - (a.v_hp / a.n_hp) ** 2) * 1e4
    s2_np = (a.v2_np / a.n_np - (a.v_np / a.n_np) ** 2) * 1e4
    s2_w = (a.w2_hp / a.n_hp - (a.w_hp / a.n_hp) ** 2) * 1e4
    a['net_s'], a['w_net'] = eb_shrink(a.net_hp.values, a.n_hp.values, s2_hp.mean())
    a['wpa_s'], _ = eb_shrink(a.wpa_hp.values, a.n_hp.values, s2_w.mean())
    nd = 1.0 / (1.0 / a.n_hp + 1.0 / a.n_np)  # effective n for difference
    a['delta_s'], _ = eb_shrink(a.delta.values, nd.values, (s2_hp.mean() + s2_np.mean()) / 2)
    k = 8.0
    a['cons'] = (a.hit + k * 0.5) / (a.elig_m + k)
    raw = {'net_s': 'net_hp', 'wpa_s': 'wpa_hp', 'delta_s': 'delta', 'cons': 'cons'}
    for c, r in raw.items():   # standardise by the RAW spread so shrinkage genuinely down-weights noisy components
        a['z_' + c] = (a[c] - a[c].mean()) / a[r].std(ddof=0)
    a['score'] = (weights['net'] * a.z_net_s + weights['wpa'] * a.z_wpa_s + weights['delta'] * a.z_delta_s + weights['cons'] * a.z_cons)
    a['name'] = names.reindex(a.index)
    a = a.sort_values('score', ascending=False)
    a['rank'] = np.arange(1, len(a) + 1)
    return a


if __name__ == '__main__':
    P = prep(b)
    res = {}
    for role, W in [('bat', W_BAT), ('bowl', W_BOWL)]:
        pm, names = P[role]
        a = score(pm, names, W)
        res[role] = a
        print(role, 'eligible', len(a))
        print(a[['name', 'n_hp', 'elig_m', 'net_hp', 'net_np', 'delta', 'wpa_hp', 'cons', 'net_s', 'wpa_s', 'delta_s', 'score']].head(15).round(2).to_string())
    pd.to_pickle(res, 'res_main.pkl')
