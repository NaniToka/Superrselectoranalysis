import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
b=pd.read_pickle('b2.pkl'); b=b[b.innings.isin([1,2])&b.LI.notna()]
res=pd.read_pickle('res_main.pkl'); out,sens=pd.read_pickle('res_robust.pkl')
PINK='#E5007D'; NAVY='#0B1F4B'; GREY='#9AA3B5'
# 1 leverage by over + calibration
fig,ax=plt.subplots(1,2,figsize=(9,3.2))
for inn,c,l in [(1,GREY,'1st innings'),(2,PINK,'2nd innings (chase)')]:
    s=b[b.innings==inn].groupby('overid').LI.mean(); ax[0].plot(s.index,s.values,marker='o',ms=3,color=c,label=l)
ax[0].axhline(1,color='k',lw=.5,ls='--'); ax[0].set_xlabel('Over'); ax[0].set_ylabel('Mean leverage index (1 = average ball)'); ax[0].legend(frameon=False); ax[0].set_title('Leverage rises sharply late in chases')
cal=pd.read_csv('wp_calibration.csv')
for inn,c,l in [(1,GREY,'1st innings'),(2,PINK,'2nd innings')]:
    d=cal[cal.innings==inn]; ax[1].plot(d.pred,d.obs,marker='o',ms=3,color=c,label=l)
ax[1].plot([0,1],[0,1],'k--',lw=.5); ax[1].set_xlabel('Predicted win probability'); ax[1].set_ylabel('Observed win rate'); ax[1].set_title('Win-probability model calibration'); ax[1].legend(frameon=False)
plt.tight_layout(); plt.savefig('c1.png',dpi=200); plt.close()
# 2 scatter
fig,ax=plt.subplots(1,2,figsize=(9,3.8))
for a,role,t in [(ax[0],'bat','Batters'),(ax[1],'bowl','Bowlers')]:
    r=res[role]; top=r.head(10)
    a.scatter(r.net_np,r.net_hp,s=np.sqrt(r.n_hp)*1.5,color=GREY,alpha=.5)
    a.scatter(top.net_np,top.net_hp,s=np.sqrt(top.n_hp)*1.5,color=PINK)
    for _,x in top.iterrows(): a.annotate(x['name'].split()[-1],(x.net_np,x.net_hp),fontsize=6.5,xytext=(3,3),textcoords='offset points')
    lim=[min(r.net_np.min(),r.net_hp.min())-5,max(r.net_np.max(),r.net_hp.max())+5]; a.plot(lim,lim,'k--',lw=.5)
    a.set_xlabel('Ordinary situations: runs above expected / 100 balls'); a.set_ylabel('High pressure: runs above expected / 100 balls'); a.set_title(t+' (pink = final top 10)')
plt.tight_layout(); plt.savefig('c2.png',dpi=200); plt.close()
# 3 stability
fig,ax=plt.subplots(1,2,figsize=(9,3.4))
for a,role,t in [(ax[0],'bat','Batters'),(ax[1],'bowl','Bowlers')]:
    o=out[role].head(10).iloc[::-1]
    a.barh(o.name,o.p_top10,color=NAVY,label='Top 10'); a.barh(o.name,o.p_top5,color=PINK,label='Top 5')
    a.set_xlim(0,1); a.set_xlabel('Share of 300 bootstrap resamples (matches)'); a.set_title(t+': ranking stability'); a.legend(frameon=False,loc='lower right')
plt.tight_layout(); plt.savefig('c3.png',dpi=200); plt.close()
print('ok')
