# ---- executed inside s8_xlsx.py before saving
av=pd.read_csv('availability.csv')
wa=wb.create_sheet('Auction Actionability',1)
wa['A1']='Auction actionability (PROVISIONAL - retention lists due 17 Nov 2026 per reports)'; wa['A1'].font=title
wa['A2']='Nationality = most frequent T20I side in the data pack (a few from my own knowledge where the player has no T20I record). IPL 2026 team = squad listing in the data pack. Retention outcomes are NOT known yet; verify after the lists are published.'; wa['A2'].font=note
wa['A3']='Surya signal: reports (12 Nov) say MI treat him as not for sale/trade, but one report speculates an exit - not official.'; wa['A3'].font=note
def act_block(r0,label,role,n=25):
    wa.cell(r0,1,label).font=Font(name=F,bold=True,size=11,color=PINK)
    hdr(wa,r0+1,['Model rank','Player','Score','Nationality','Overseas?','IPL 2026 team','Excluded from IPL (Pakistan)?','Actionable rank','Status'])
    d=av[(av.role==role)&(av['rank']<=n)].sort_values('rank')
    first=r0+2
    for i,(_,r) in enumerate(d.iterrows()):
        R=first+i
        put(wa,R,1,int(r['rank']),inp,'0'); put(wa,R,2,r['name'],inp,al='left'); put(wa,R,3,float(r.score),inp,'0.00')
        put(wa,R,4,r.nationality,inp); put(wa,R,5,r.overseas,inp); put(wa,R,6,r.ipl2026 if isinstance(r.ipl2026,str) else '',inp,al='left')
        put(wa,R,7,f'=IF(D{R}="Pakistan","Yes","No")',blk)
        put(wa,R,8,f'=IF(G{R}="Yes","-",COUNTIF($G${first}:G{R},"No"))',blk,'0')
        put(wa,R,9,r.status,inp,al='left')
    return first, first+len(d)-1
a0,a1=act_block(5,'Batters - top 25 by model score','bat')
c0,c1=act_block(a1+3,'Bowlers - top 25 by model score','bowl')
for c,w in zip('ABCDEFGHI',[10,24,8,14,10,28,16,13,95]): wa.column_dimensions[c].width=w
wa.cell(c1+2,1,'Actionable rank counts down the list skipping players who cannot realistically be bought (Pakistan). It does not account for retentions, which are unknown until the lists are published.').font=note
# shortlist
wsl=wb.create_sheet('Auction Shortlist',2)
wsl['A1']='Suggested actionable lists and RR target pool (PROVISIONAL)'; wsl['A1'].font=title
wsl['A2']='Option B: remove players who cannot play in the IPL (Pakistan) and anyone believed retired; the next-ranked players move up. Option A (current submission) keeps the pure performance ranking.'; wsl['A2'].font=note
out2,_=pd.read_pickle('res_robust.pkl')
def alt(r0,label,role):
    wsl.cell(r0,1,label).font=Font(name=F,bold=True,size=11,color=PINK)
    hdr(wsl,r0+1,['Option B rank','Player','Model rank','Nationality','IPL 2026 team','Bootstrap top-10 share','Note'])
    d=av[(av.role==role)&(~av.nationality.eq('Pakistan'))&(~av.status.str.startswith('Believed retired'))].sort_values('rank').head(10)
    for i,(_,r) in enumerate(d.iterrows()):
        R=r0+2+i; o=out2[role].p_top10.get(r.pid,np.nan)
        put(wsl,R,1,i+1,blk,'0'); put(wsl,R,2,r['name'],inp,al='left'); put(wsl,R,3,int(r['rank']),inp,'0'); put(wsl,R,4,r.nationality,inp)
        put(wsl,R,5,r.ipl2026 if isinstance(r.ipl2026,str) else '',inp,al='left'); put(wsl,R,6,float(o) if o==o else None,inp,'0%')
        note=''
        if r['rank']>10: note='Moves into the top 10 when Pakistan / retired players are removed'
        if r.ipl2026=='Rajasthan Royals': note=(note+'; ' if note else '')+'Already an RR player in 2026 squad'
        put(wsl,R,7,note,inp,al='left')
alt(4,'Batters - Option B (availability-adjusted top 10)','bat')
alt(17,'Bowlers - Option B (availability-adjusted top 10)','bowl')
wsl.cell(30,1,'Auction target pool: high-scoring players NOT in an IPL 2026 squad (could reach the 16 Dec auction pool if registered)').font=Font(name=F,bold=True,size=11,color=PINK)
hdr(wsl,31,['Role','Player','Model rank','Nationality','Overseas?','Score','Why'])
pool=av[(av['rank']<=40)&(av.status.str.startswith('Not in an IPL 2026 squad'))].sort_values('score',ascending=False).head(12)
for i,(_,r) in enumerate(pool.iterrows()):
    R=32+i; put(wsl,R,1,'Batter' if r.role=='bat' else 'Bowler',inp); put(wsl,R,2,r['name'],inp,al='left'); put(wsl,R,3,int(r['rank']),inp,'0')
    put(wsl,R,4,r.nationality,inp); put(wsl,R,5,r.overseas,inp); put(wsl,R,6,float(r.score),inp,'0.00'); put(wsl,R,7,'Strong pressure score and no 2026 IPL squad listing; confirm registration and price',inp,al='left')
wsl.cell(46,1,'Players with a 2026 contract may still be released on 17 Nov; re-check this sheet against the official lists. Ranks 11-40 have wider uncertainty (see Stability).').font=note
for c,w in zip('ABCDEFG',[16,24,11,14,28,18,70]): wsl.column_dimensions[c].width=w
