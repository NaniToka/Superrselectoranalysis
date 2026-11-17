import pandas as pd, numpy as np
U='data/'
m=pd.read_csv(U+'competition_team_player_mapping.csv'); c=pd.read_csv(U+'competitions.csv')
ipl_ids=c[c.comp_name.str.startswith('IPL')].comp_id.tolist()
t20i=c[c.match_format=='T20I'].comp_id.tolist()
# nationality: most frequent T20I team of the player
nat=m[m.comp_id.isin(t20i)].groupby(['player_id','team_name']).size().reset_index(name='n').sort_values('n',ascending=False).drop_duplicates('player_id').set_index('player_id').team_name
ipl26=m[m.comp_id==3298].drop_duplicates('player_id').set_index('player_id').team_name
ipl_any=m[m.comp_id.isin(ipl_ids)].groupby('player_id').comp_id.nunique()
MANUAL={'Sunil Narine':'West Indies','Krunal Pandya':'India','Mohit Sharma':'India','Mohsin Khan':'India','Rajat Patidar':'India','Shashank Singh':'India','Rahul Tewatia':'India','Ajinkya Rahane':'India','Ayush Badoni':'India','Nehal Wadhera':'India','Devdutt Padikkal':'India','Nitish Rana':'India','Faf du Plessis':'South Africa','Digvesh Rathi':'India','T Natarajan':'India','Sandeep Sharma':'India','Rahul Chahar':'India','Harpreet Brar':'India','Jaydev Unadkat':'India','Vaibhav Arora':'India','Suyash Sharma':'India'}
rows=[]
for role in ['bat','bowl']:
    a=pd.read_csv(f'all_{role}.csv').sort_values('rank')
    for _,r in a.iterrows():
        pid=int(r.pid); n=nat.get(pid,'Unknown'); t=ipl26.get(pid)
        if n=='Unknown': n=MANUAL.get(r['name'],'Unknown')
        if n=='Pakistan': st='Not IPL-eligible in practice (Pakistan)'
        elif t is None and ipl_any.get(pid,0)==0: st='No IPL squad listing 2022-26 (ball data from T20Is) - auction entry uncertain'
        elif t is None: st='Not in an IPL 2026 squad - could reach the auction pool'
        else: st=f'Under IPL 2026 contract with {t} - retention/release decision due (reported deadline 17 Nov)'
        if r['name']=='Dinesh Karthik': st='Believed retired from IPL - verify before using'
        rows.append(dict(role=role,rank=int(r['rank']),pid=pid,name=r['name'],score=r.score,nationality=n,ipl2026=t if t else '',seasons_ipl=int(ipl_any.get(pid,0)),overseas='No' if n=='India' else ('Unknown' if n=='Unknown' else 'Yes'),status=st))
d=pd.DataFrame(rows); d.to_csv('availability.csv',index=False)
for role in ['bat','bowl']:
    print(d[(d.role==role)&(d['rank']<=25)][['rank','name','nationality','ipl2026','overseas','status']].to_string())
