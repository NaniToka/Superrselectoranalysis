import pandas as pd, numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier as HGC, HistGradientBoostingRegressor as HGR
from sklearn.model_selection import GroupKFold

b = pd.read_pickle('b1.pkl')
bad = set(pd.read_csv('bad_matches.csv').iloc[:,0])
b = b[~b.match_id.isin(bad)].reset_index(drop=True)
reg = b.innings.isin([1, 2])
K = 5
rng = np.random.RandomState(7)
mids = b.match_id.unique()
fold_of = dict(zip(mids, rng.randint(0, K, len(mids))))
b['fold'] = b.match_id.map(fold_of)

# ------------------------------------------------------------------ WIN PROBABILITY
so_matches = set(b[b.innings >= 3].match_id)
b['bat_won'] = (b.batting_team_id == b.win_team_id).astype(float)
b.loc[b.win_team_id.isna() | b.match_id.isin(so_matches), 'bat_won'] = np.nan


def wp_feats(inn, bl, wk, sc, tgt, ipl, maxb):
    d = pd.DataFrame({'bl': bl, 'wk': wk, 'sc': sc, 'ipl': ipl, 'maxb': maxb})
    if inn == 1:
        pass
    else:
        need = tgt - sc
        d['need'] = need
        d['rrr'] = np.where(bl > 0, need / np.maximum(bl, 1) * 6, np.where(need > 0, 99, 0)).clip(None, 60)
        d['tgt'] = tgt
        d['nb'] = need / np.maximum(maxb, 1)
    return d


def state_after(df, inn):
    return wp_feats(inn, df.balls_left_a.values, df.wk_after.values, df.score_after.values, df.target.values, df.is_ipl.values, df.max_balls.values)


def state_before(df, inn):
    return wp_feats(inn, df.balls_left_b.values, df.wk_before.values, df.score_before.values, df.target.values, df.is_ipl.values, df.max_balls.values)


wp_models = {}
for inn in (1, 2):
    d = b[(b.innings == inn) & b.bat_won.notna() & (b.target.notna() if inn == 2 else True)]
    Xa = state_after(d, inn)
    # add initial states (before first ball)
    first = d[d.legal_before == 0].drop_duplicates('match_id')
    Xi = state_before(first, inn)
    X = pd.concat([Xa, Xi]).reset_index(drop=True)
    y = np.r_[d.bat_won.values, first.bat_won.values]
    f = np.r_[d.fold.values, first.fold.values]
    for k in range(K):
        mdl = HGC(max_iter=100, learning_rate=0.06, max_leaf_nodes=16, min_samples_leaf=(500 if inn == 1 else 150), l2_regularization=2.0, random_state=k)
        mdl.fit(X[f != k], y[f != k])
        wp_models[(inn, k)] = mdl
    print('WP model', inn, 'trained on', len(X))


from sklearn.isotonic import IsotonicRegression
cals = {}


def wp_predict(inn, X, folds):
    out = np.zeros(len(X))
    for k in range(K):
        idx = folds == k
        if idx.any():
            out[idx] = wp_models[(inn, k)].predict_proba(X[idx])[:, 1]
    if inn in cals:
        out = np.clip(cals[inn].predict(out), 0.005, 0.995)
    return out


def apply_terminal(inn, wp, need, wk, bl):
    if inn == 2:
        wp = np.where(need <= 0, 1.0, np.where((wk >= 10) | (bl <= 0), 0.0, wp))
    return wp


b['wp_b'] = np.nan
b['wp_a'] = np.nan
for inn in (1, 2):
    idx = (b.innings == inn)
    d = b[idx]
    fo = d.fold.values
    wb = wp_predict(inn, state_before(d, inn), fo)
    wa = wp_predict(inn, state_after(d, inn), fo)
    wb = apply_terminal(inn, wb, d.need_b.values, d.wk_before.values, d.balls_left_b.values)
    wa = apply_terminal(inn, wa, d.need_a.values, d.wk_after.values, d.balls_left_a.values)
    b.loc[idx, 'wp_b'] = wb
    b.loc[idx, 'wp_a'] = wa
# isotonic recalibration on out-of-fold predictions, then recompute
for inn in (1, 2):
    d = b[(b.innings == inn) & b.bat_won.notna() & (b.target.notna() if inn == 2 else True)]
    cals[inn] = IsotonicRegression(out_of_bounds='clip').fit(d.wp_b, d.bat_won)
    idx = (b.innings == inn)
    dd = b[idx]; fo = dd.fold.values
    wb = wp_predict(inn, state_before(dd, inn), fo); wa = wp_predict(inn, state_after(dd, inn), fo)
    wb = apply_terminal(inn, wb, dd.need_b.values, dd.wk_before.values, dd.balls_left_b.values)
    wa = apply_terminal(inn, wa, dd.need_a.values, dd.wk_after.values, dd.balls_left_a.values)
    b.loc[idx, 'wp_b'] = wb; b.loc[idx, 'wp_a'] = wa
# WP calibration check (out-of-fold)
lab = b[reg & b.bat_won.notna()]
lab = lab.assign(bin=pd.cut(lab.wp_b, [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0], include_lowest=True))
cal = lab.groupby(['innings', 'bin'], observed=True).agg(pred=('wp_b', 'mean'), obs=('bat_won', 'mean'), n=('wp_b', 'size')).reset_index()
cal.to_csv('wp_calibration.csv', index=False)
from sklearn.metrics import roc_auc_score, brier_score_loss
for inn in (1, 2):
    l = lab[lab.innings == inn]
    print('inn', inn, 'AUC', round(roc_auc_score(l.bat_won, l.wp_b), 3), 'Brier', round(brier_score_loss(l.bat_won, l.wp_b), 3))

b['wpa_bat'] = b.wp_a - b.wp_b   # batting-team perspective

# ------------------------------------------------------------------ LEVERAGE INDEX
legal_reg = b[reg & b.legal]
outs = [0, 1, 2, 3, 4, 6, 'W']


def bucket(r):
    return np.where(r.wkt_any, 'W', np.where(r.bat_runs >= 6, '6', np.where(r.bat_runs >= 4, '4', r.bat_runs.astype(str))))


legal_reg = legal_reg.assign(o=bucket(legal_reg))
probs = legal_reg.groupby(['innings', 'overid']).o.value_counts(normalize=True).unstack(fill_value=0)
for o in ['0', '1', '2', '3', '4', '6', 'W']:
    if o not in probs.columns:
        probs[o] = 0
li = np.full(len(b), np.nan)
for inn in (1, 2):
    idx = np.where(b.innings.values == inn)[0]
    d = b.iloc[idx]
    fo = d.fold.values
    wb = d.wp_b.values
    pr = probs.loc[list(zip(d.innings, d.overid))][['0', '1', '2', '3', '4', '6', 'W']].values
    acc = np.zeros(len(d))
    for j, o in enumerate(['0', '1', '2', '3', '4', '6', 'W']):
        r = 0 if o == 'W' else int(o)
        wk = d.wk_before.values + (1 if o == 'W' else 0)
        sc = d.score_before.values + r
        bl = np.maximum(d.balls_left_b.values - 1, 0)
        X = wp_feats(inn, bl, wk, sc, d.target.values, d.is_ipl.values, d.max_balls.values)
        w = wp_predict(inn, X, fo)
        need = d.target.values - sc
        w = apply_terminal(inn, w, need, wk, bl)
        acc += pr[:, j] * np.abs(w - wb)
    li[idx] = acc
b['li_raw'] = li
b['LI'] = b.li_raw / np.nanmean(b.li_raw)

# ------------------------------------------------------------------ EXPECTED-VALUE MODELS
feat = ['innings', 'overid', 'wk_before', 'balls_left_b', 'score_before', 'crr_b', 'need_b', 'rrr_b', 'is_ipl']
b['rrr_b_c'] = b.rrr_b.clip(upper=60)
feat = ['innings', 'overid', 'wk_before', 'balls_left_b', 'score_before', 'crr_b', 'need_b', 'rrr_b_c', 'is_ipl']


def oof(df_mask, target, kind):
    d = b[df_mask]
    out = pd.Series(np.nan, index=b.index)
    for k in range(K):
        tr, te = d[d.fold != k], d[d.fold == k]
        if kind == 'reg':
            mdl = HGR(max_iter=150, learning_rate=0.06, max_leaf_nodes=24, min_samples_leaf=200, l2_regularization=1.0, random_state=k)
            mdl.fit(tr[feat], tr[target].astype(float))
            out.loc[te.index] = mdl.predict(te[feat])
        else:
            mdl = HGC(max_iter=150, learning_rate=0.06, max_leaf_nodes=24, min_samples_leaf=200, l2_regularization=1.0, random_state=k)
            mdl.fit(tr[feat], tr[target].astype(int))
            out.loc[te.index] = mdl.predict_proba(te[feat])[:, 1]
    return out


b['E_bat_runs'] = oof(reg & b.faced, 'bat_runs', 'reg')
b['P_out_bat'] = oof(reg & b.faced, 'out_striker', 'clf')
b['E_chg_runs'] = oof(reg, 'chg_runs', 'reg')
b['P_wkt_bowl'] = oof(reg, 'wkt_bowler', 'clf')
print('E-model sanity: mean pred vs obs  bat_runs', b.E_bat_runs.mean(), b[reg & b.faced].bat_runs.mean(),
      '| chg', b.E_chg_runs.mean(), b[reg].chg_runs.mean())

# ------------------------------------------------------------------ WICKET VALUE (runs) FROM WP MODEL, by phase
lam = {}
for ph in ['PP', 'MID', 'DEATH']:
    d = b[reg & (b.phase == ph) & b.wpa_bat.notna() & (b.innings == 2) & (b.wp_b.between(0.15, 0.85))]
    X = np.c_[d.team_runs.values, d.wkt_any.values.astype(float), np.ones(len(d))]
    coef = np.linalg.lstsq(X, d.wpa_bat.values, rcond=None)[0]
    lam[ph] = -coef[1] / coef[0]
    print(ph, 'WP per run', round(coef[0], 4), 'WP per wicket', round(coef[1], 4), '-> wicket = %.1f runs' % lam[ph])
b['lam'] = b.phase.map(lam)

# per-ball values (runs-above-expected incl. wicket cost)
b['v_bat'] = np.where(b.faced & reg, (b.bat_runs - b.E_bat_runs) - b.lam * (b.out_striker.astype(float) - b.P_out_bat), np.nan)
b['v_bowl'] = np.where(reg, (b.E_chg_runs - b.chg_runs) + b.lam * (b.wkt_bowler.astype(float) - b.P_wkt_bowl), np.nan)
b['wpa_batter'] = np.where(b.faced & reg, b.wpa_bat, np.nan)
b['wpa_bowler'] = np.where(reg, -b.wpa_bat, np.nan)
b.to_pickle('b2.pkl')

print(b[reg].LI.describe())
print(b[reg].LI.quantile([.5, .67, .75, .8, .9, .95]))
print(b[reg].groupby(['innings', 'phase']).LI.mean())
