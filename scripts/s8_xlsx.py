import pandas as pd, numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
out,sens=pd.read_pickle('res_robust.pkl')
ab=pd.read_csv('all_bat.csv').sort_values('rank'); aw=pd.read_csv('all_bowl.csv').sort_values('rank')
fb=pd.read_csv('final_bat.csv').head(10); fw=pd.read_csv('final_bowl.csv').head(10)
F='Arial'; NAVY='0B1F4B'; PINK='E5007D'
hf=Font(name=F,bold=True,color='FFFFFF',size=10); hfill=PatternFill('solid',fgColor=NAVY)
inp=Font(name=F,color='0000FF',size=10); blk=Font(name=F,size=10); grn=Font(name=F,color='008000',size=10)
bold=Font(name=F,bold=True,size=10); title=Font(name=F,bold=True,size=14,color=NAVY); note=Font(name=F,italic=True,size=9,color='555555')
thin=Side(style='thin',color='C8CCD8'); bd=Border(left=thin,right=thin,top=thin,bottom=thin)
yel=PatternFill('solid',fgColor='FFFF00'); band=PatternFill('solid',fgColor='F3F4F8')
def hdr(ws,row,cols,start=1):
    for i,c in enumerate(cols):
        x=ws.cell(row,start+i,c); x.font=hf; x.fill=hfill; x.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True); x.border=bd
    ws.row_dimensions[row].height=30
def put(ws,r,c,v,font=blk,fmt=None,al='center'):
    x=ws.cell(r,c,v); x.font=font; x.border=bd; x.alignment=Alignment(horizontal=al)
    if fmt: x.number_format=fmt
    return x
wb=Workbook()

# ---------------- All sheets with live score
def all_sheet(name,df,role):
    ws=wb.create_sheet(name)
    ws['A1']=f'All eligible {role} - pressure scoring model'; ws['A1'].font=title
    ws['A2']='Score = weighted sum of four standardised components. Blue = inputs from the Python model; black = formulas. Change the weights (yellow) and ranks recompute.'; ws['A2'].font=note
    for i,(lab,w) in enumerate([('Weight: pressure value (net runs above expected)',0.35),('Weight: win probability added',0.30),('Weight: own-baseline delta',0.20),('Weight: consistency',0.15)]):
        ws.cell(3+i,1,lab).font=blk; c=ws.cell(3+i,2,w); c.font=inp; c.fill=yel; c.number_format='0.00'; c.border=bd
    ws.cell(7,1,'Weights total').font=bold; c=ws.cell(7,2,'=SUM(B3:B6)'); c.font=bold; c.number_format='0.00'
    cols=['Rank','Player','HP balls','HP matches','Net/100 (HP)','Net/100 (ordinary)','Delta (HP - ordinary)','WPA/100 (HP)','Consistency','z Net (shrunk)','z WPA (shrunk)','z Delta (shrunk)','z Consistency','Score']
    hdr(ws,9,cols); n=len(df); r0=10; r1=r0+n-1
    for i,(_,r) in enumerate(df.iterrows()):
        R=r0+i
        put(ws,R,1,f'=RANK(N{R},$N${r0}:$N${r1})',blk,'0')
        put(ws,R,2,r['name'],inp,al='left')
        put(ws,R,3,int(r.n_hp),inp,'#,##0'); put(ws,R,4,int(r.elig_m),inp,'0')
        put(ws,R,5,float(r.net_hp),inp,'0.0'); put(ws,R,6,float(r.net_np),inp,'0.0')
        put(ws,R,7,f'=E{R}-F{R}',blk,'0.0'); put(ws,R,8,float(r.wpa_hp),inp,'0.00'); put(ws,R,9,float(r.cons),inp,'0.00')
        for j,k in enumerate(['z_net_s','z_wpa_s','z_delta_s','z_cons']): put(ws,R,10+j,float(r[k]),inp,'0.00')
        put(ws,R,14,f'=$B$3*J{R}+$B$4*K{R}+$B$5*L{R}+$B$6*M{R}',bold,'0.00')
    ws.cell(r1+2,1,'HP = high pressure (leverage index at or above the 75th percentile). Net/100 = runs above expected per 100 balls, wickets included. WPA = win probability added (probability points).').font=note
    for c,w in zip(range(1,15),[7,26,10,11,12,13,14,12,12,12,12,12,13,10]): ws.column_dimensions[L(c)].width=w
    ws.column_dimensions['A'].width=48 if False else 7
    ws.freeze_panes='C10'
    return r0,r1
wb.remove(wb.active)
ws0=wb.create_sheet('Final Rankings')
b0,b1=all_sheet('All Batters',ab,'batters'); w0,w1=all_sheet('All Bowlers',aw,'bowlers')
# fix long weight labels visibility: widen col A on these sheets not possible (rank col) -> put labels spanning by merging? use wrap
for s in ['All Batters','All Bowlers']:
    ws=wb[s]
    for r in range(3,8): ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=1)
    ws.column_dimensions['A'].width=46
# ---------------- Final Rankings (formula-driven)
ws=ws0; ws['A1']='SupeRR Selector Season 2 - Round 1: most reliable players under pressure'; ws['A1'].font=title
ws['A2']='Rankings pull live from the All Batters / All Bowlers sheets (green = cross-sheet links). Source data: IPL + T20I ball-by-ball, 2022-2026.'; ws['A2'].font=note
def final_block(r_start,label,sheet,r0,r1,extra_name):
    ws.cell(r_start,1,label).font=Font(name=F,bold=True,size=11,color=PINK)
    hdr(ws,r_start+1,['Rank','Player','HP balls','Net/100 (HP)','Delta vs own baseline','WPA/100','Consistency','Score'])
    for k in range(1,11):
        R=r_start+1+k; put(ws,R,1,k,blk,'0')
        rng=lambda col:f"'{sheet}'!${col}${r0}:${col}${r1}"
        m=f"MATCH($A{R},{rng('A')},0)"
        put(ws,R,2,f"=INDEX({rng('B')},{m})",grn,al='left')
        for c,col,fmt in [(3,'C','#,##0'),(4,'E','0.0'),(5,'G','0.0'),(6,'H','0.00'),(7,'I','0.00'),(8,'N','0.00')]:
            put(ws,R,c,f"=INDEX({rng(col)},{m})",grn,fmt)
final_block(4,'Top 10 batters under pressure','All Batters',b0,b1,'')
final_block(18,'Top 10 bowlers under pressure','All Bowlers',w0,w1,'')
ws['A31']='Reading guide: HP = high-pressure deliveries (top quarter by leverage). Ranks 4 to 10 are close - see the Stability sheet before treating the order as firm.'; ws['A31'].font=note
for c,w in zip('ABCDEFGH',[7,28,11,13,17,11,13,10]): ws.column_dimensions[c].width=w

# ---------------- Top 10 Detail (traditional stats with formulas)
wd=wb.create_sheet('Top10 Detail'); wd['A1']='Traditional stats in high-pressure deliveries (top 10 lists)'; wd['A1'].font=title
wd['A2']='Counts are from the Python model (blue); rates are formulas (black). Batter outs = dismissals of the striker. Bowler runs exclude byes and leg byes; wickets exclude run-outs.'; wd['A2'].font=note
wd['A4']='Batters'; wd['A4'].font=Font(name=F,bold=True,size=11,color=PINK)
hdr(wd,5,['Rank','Batter','HP balls','HP runs','Outs','Fours','Sixes','SR','Average','Boundary %','Ordinary SR','SR gap'])
for i,(_,r) in enumerate(fb.iterrows()):
    R=6+i; put(wd,R,1,int(r['rank']),inp,'0'); put(wd,R,2,r['name'],inp,al='left')
    for c,k in [(3,'balls'),(4,'runs'),(5,'outs'),(6,'fours'),(7,'sixes')]: put(wd,R,c,int(r[k]),inp,'#,##0')
    put(wd,R,8,f'=D{R}/C{R}*100',blk,'0.0'); put(wd,R,9,f'=D{R}/MAX(1,E{R})',blk,'0.0'); put(wd,R,10,f'=(F{R}+G{R})/C{R}',blk,'0.0%')
    put(wd,R,11,float(r.SR_ord),inp,'0.0'); put(wd,R,12,f'=H{R}-K{R}',blk,'0.0')
wd['A18']='Bowlers'; wd['A18'].font=Font(name=F,bold=True,size=11,color=PINK)
hdr(wd,19,['Rank','Bowler','HP legal balls','HP runs','Wickets','Economy','Bowling SR','Dot ball %','Ordinary economy','Economy gap'])
for i,(_,r) in enumerate(fw.iterrows()):
    R=20+i; put(wd,R,1,int(r['rank']),inp,'0'); put(wd,R,2,r['name'],inp,al='left')
    for c,k in [(3,'balls'),(4,'runs'),(5,'wkts')]: put(wd,R,c,int(r[k]),inp,'#,##0')
    put(wd,R,6,f'=D{R}/C{R}*6',blk,'0.00'); put(wd,R,7,f'=C{R}/MAX(1,E{R})',blk,'0.0'); put(wd,R,8,float(r['dot%'])/100,inp,'0.0%')
    put(wd,R,9,float(r.econ_ord),inp,'0.00'); put(wd,R,10,f'=F{R}-I{R}',blk,'0.00')
wd['A31']='Economy gap below zero means the bowler is cheaper under pressure than in ordinary situations. Raw economy is not context-adjusted; the model score is.'; wd['A31'].font=note
for c,w in zip('ABCDEFGHIJKL',[7,26,13,10,9,10,11,11,15,12,12,10]): wd.column_dimensions[c].width=w

# ---------------- Stability
wt=wb.create_sheet('Stability'); wt['A1']='Ranking stability (top 10 finalists)'; wt['A1'].font=title
wt['A2']='Static results from 300 match-level bootstrap resamples, 7 alternative model specifications and 100 weight perturbations (+/-30%).'; wt['A2'].font=note
def nvar(role,pid):
    return sum(1 for k,s in sens[role].items() if k not in('weights_pm30','weights_top10_freq') and pid in s.index and s[pid]<=10)
def stab(r0,label,role,fdf):
    wt.cell(r0,1,label).font=Font(name=F,bold=True,size=11,color=PINK)
    hdr(wt,r0+1,['Rank','Player','Bootstrap: share in top 10','Bootstrap: share in top 5','Median rank (resamples)','Rank 10th pct','Rank 90th pct','Variants in top 10 (of 7)','Weight tests in top 10','Sample size flag'])
    for i,(_,r) in enumerate(fdf.iterrows()):
        R=r0+2+i; o=out[role].loc[r.pid]
        put(wt,R,1,int(r['rank']),inp,'0'); put(wt,R,2,r['name'],inp,al='left')
        put(wt,R,3,float(o.p_top10),inp,'0%'); put(wt,R,4,float(o.p_top5),inp,'0%')
        put(wt,R,5,float(o.median_rank),inp,'0.0'); put(wt,R,6,float(o.rank_lo),inp,'0.0'); put(wt,R,7,float(o.rank_hi),inp,'0.0')
        put(wt,R,8,nvar(role,r.pid),inp,'0'); put(wt,R,9,float(sens[role]['weights_top10_freq'].get(r.pid,0)),inp,'0%')
        put(wt,R,10,f'=IF(B{R}="","",IF(C{R}<0.5,"Unstable","Moderate+"))' if False else f'=IF(C{R}>=0.75,"Stable",IF(C{R}>=0.4,"Moderate","Unstable"))',blk)
stab(4,'Batters','bat',fb); stab(18,'Bowlers','bowl',fw)
wt['J5']='Stability flag (bootstrap top-10 share)'; wt['J5'].alignment=Alignment(wrap_text=True,horizontal='center')
wt['J19']='Stability flag (bootstrap top-10 share)'; wt['J19'].alignment=Alignment(wrap_text=True,horizontal='center')
wt['A31']='Flag rule: Stable >= 75% of resamples in top 10; Moderate 40% to 75%; Unstable below 40%. Variants: thresholds P67/P85, chase-only, IPL-only, T20I-only, wicket value x0.5 and x1.5. Some bowlers are absent from a variant when they fail its eligibility rule.'; wt['A31'].font=note
for c,w in zip('ABCDEFGHIJ',[7,26,15,15,14,11,11,15,14,16]): wt.column_dimensions[c].width=w

# ---------------- Notable names
wn=wb.create_sheet('Notable Names'); wn['A1']='Where well-known players rank under this model'; wn['A1'].font=title
wn['A2']='Lookups into the All Batters / All Bowlers sheets (live). "Not eligible" = fewer than 150 high-pressure balls, 8 high-pressure matches or 100 ordinary balls.'; wn['A2'].font=note
hdr(wn,4,['Player','Role','Rank','Score'])
names=[('Suryakumar Yadav','Batter'),('Tilak','Batter'),('Rinku','Batter'),('David Miller','Batter'),('Jos Buttler','Batter'),('Heinrich Klaasen','Batter'),
       ('Rashid Khan','Bowler'),('Arshdeep Singh','Bowler'),('Jasprit Bumrah','Bowler'),('Varun Chakravarthy','Bowler'),('Haris Rauf','Bowler'),('Wanindu Hasaranga','Bowler')]
allb=pd.concat([ab.assign(role='Batter'),aw.assign(role='Bowler')])
for i,(n,role) in enumerate(names):
    R=5+i; hit=allb[(allb.role==role)&allb.name.str.contains(n.split()[0] if n in ('Tilak','Rinku') else n.split()[-1])]
    full=hit.name.iloc[0] if len(hit) else n
    put(wn,R,1,full,inp,al='left'); put(wn,R,2,role,inp)
    sh,r0,r1=('All Batters',b0,b1) if role=='Batter' else ('All Bowlers',w0,w1)
    put(wn,R,3,f"=IFERROR(INDEX('{sh}'!$A${r0}:$A${r1},MATCH(A{R},'{sh}'!$B${r0}:$B${r1},0)),\"Not eligible\")",grn,'0')
    put(wn,R,4,f"=IFERROR(INDEX('{sh}'!$N${r0}:$N${r1},MATCH(A{R},'{sh}'!$B${r0}:$B${r1},0)),\"\")",grn,'0.00')
for c,w in zip('ABCD',[26,10,14,10]): wn.column_dimensions[c].width=w

# ---------------- Method & notes
wm=wb.create_sheet('Method & Notes'); wm['A1']='Method summary and caveats'; wm['A1'].font=title
lines=[('Pressure','Win-probability model (gradient boosting, out-of-fold, recalibrated) -> leverage index = expected absolute win-probability swing of the next ball. High pressure = leverage at or above the 75th percentile (>= 1.32; 49,276 of 197,100 analysed deliveries).'),
('Value','Per-ball value over expected (phase, wickets, balls left, target, league). Wicket value from the win-probability model: about 8.3 runs (powerplay), 6.0 (middle), 2.8 (death).'),
('Score','0.35 x pressure value + 0.30 x win probability added + 0.20 x delta vs own ordinary level + 0.15 x consistency, each empirical-Bayes shrunk and standardised.'),
('Eligibility','At least 150 high-pressure deliveries, 8 high-pressure matches (6+ balls each) and 100 ordinary deliveries: 100 batters and 102 bowlers qualify.'),
('Data fixes','extras1_runs is a type code; byes and leg-bye runs are unrecorded; 16 matches whose ball data contradicts the result and 570 second-innings balls with unknown target were dropped; super overs excluded.'),
('Limits','Ranks 4 to 10 are close (see Stability). No pitch, dew, boundary or opposition-strength data. About 17% of chases end before the last ball in the data. First-innings win probability is weaker (AUC 0.68 vs 0.89).'),
('Inputs','Blue cells are static outputs from the Python pipeline; changing weights on the All sheets recomputes scores and ranks, but the underlying z-scores come from the model and do not change.'),
('Rules','The competition data pack must not be shared or published; keep this workbook private. Make sure you can explain each choice yourself before submitting.')]
for i,(k,v) in enumerate(lines):
    R=3+i; a=wm.cell(R,1,k); a.font=bold; a.alignment=Alignment(vertical='top')
    c=wm.cell(R,2,v); c.font=blk; c.alignment=Alignment(wrap_text=True,vertical='top'); wm.row_dimensions[R].height=48
wm.column_dimensions['A'].width=14; wm.column_dimensions['B'].width=110
import os
s10_path = 'scripts/s10_add.py' if os.path.exists('scripts/s10_add.py') else 's10_add.py'
exec(open(s10_path).read())
wb.save('outputs/SupeRR_Round1_Rankings.xlsx')
