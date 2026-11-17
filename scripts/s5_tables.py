import pandas as pd, numpy as np
from s3_score import *
res = pd.read_pickle('res_main.pkl'); out, sens = pd.read_pickle('res_robust.pkl')
thr = b.LI.quantile(.75); b['hp'] = b.LI >= thr
print('LI P75 threshold', round(thr,3), 'HP share', b.hp.mean().round(3), 'n HP', b.hp.sum(), 'of', len(b))
# ---- validation: HP vs ordinary
bf = b[b.faced]
def stats(d):
    f = d[d.faced]; l = d
    return pd.Series({'deliveries': len(d), 'bat SR': f.bat_runs.sum()/len(f)*100, 'dismissal %/ball faced': f.out_striker.mean()*100,
        'boundary %': (f.is_four|f.is_six).mean()*100, 'dot %': (f.bat_runs==0).mean()*100,
        'bowler econ': l.chg_runs.sum()/l.legal.sum()*6, 'mean |dWP| per ball': l.wpa_bat.abs().mean()*100, 'mean LI': l.LI.mean()})
val = b.groupby('hp').apply(stats).T; val.columns=['Ordinary','High pressure']; print(val.round(2))
val.to_csv('val_hp.csv')
mix = b.groupby(['innings','phase']).hp.mean().unstack().round(3); print(mix); mix.to_csv('hp_mix.csv')
# ---- descriptive stats for eligible players
def desc_bat(pids):
    d = b[b.hp & b.faced & b.striker_id.isin(pids)].groupby('striker_id')
    t = d.agg(balls=('bat_runs','size'), runs=('bat_runs','sum'), outs=('out_striker','sum'), matches=('match_id','nunique'), fours=('is_four','sum'), sixes=('is_six','sum'))
    t['SR']=t.runs/t.balls*100; t['avg']=t.runs/t.outs.clip(lower=1); t['bdry%']=(t.fours+t.sixes)/t.balls*100
    nd = b[~b.hp & b.faced & b.striker_id.isin(pids)].groupby('striker_id').agg(r=('bat_runs','sum'), n=('bat_runs','size')); t['SR_ord']=nd.r/nd.n*100
    return t
def desc_bowl(pids):
    d = b[b.hp & b.bowler_id.isin(pids)].groupby('bowler_id')
    t = d.agg(balls=('legal','sum'), runs=('chg_runs','sum'), wkts=('wkt_bowler','sum'), matches=('match_id','nunique'))
    t['econ']=t.runs/t.balls*6; t['SR']=t.balls/t.wkts.clip(lower=1)
    dots = b[b.hp & b.legal & (b.chg_runs==0) & b.bowler_id.isin(pids)].groupby('bowler_id').size(); t['dot%']=dots/t.balls*100
    nd = b[~b.hp & b.bowler_id.isin(pids)].groupby('bowler_id').agg(r=('chg_runs','sum'), n=('legal','sum')); t['econ_ord']=nd.r/nd.n*6
    return t
fin = {}
for role, fn in [('bat', desc_bat), ('bowl', desc_bowl)]:
    a = res[role].head(15)
    t = fn(a.index).reindex(a.index)
    t.insert(0,'name',a.name); t.insert(1,'rank',a['rank'])
    t['score']=a.score; t['net_hp']=a.net_hp; t['net_np']=a.net_np; t['delta']=a.delta; t['wpa_hp']=a.wpa_hp; t['cons']=a.cons
    t['p_top10']=out[role].p_top10.reindex(a.index); t['p_top5']=out[role].p_top5.reindex(a.index)
    fin[role]=t; print(t.round(2).to_string()); t.to_csv(f'final_{role}.csv')
    res[role].to_csv(f'all_{role}.csv')
# ---- where do the old-report names rank
for role, names in [('bat',['Suryakumar','Tim David','Tilak','Rinku','Dinesh Karthik','Stubbs','Gill','Miller','Buttler','Klaasen']),('bowl',['Rashid','Arshdeep','Pathirana','Narine','Bumrah','Haris Rauf','Varun','Hasaranga','Hazlewood','Santner'])]:
    a = res[role]; print(role, [(n, int(a[a.name.str.contains(n)]['rank'].iloc[0]) if a.name.str.contains(n).any() else None) for n in names])
