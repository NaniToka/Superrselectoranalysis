import pandas as pd, numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
fb=pd.read_csv('final_bat.csv').head(10); fw=pd.read_csv('final_bowl.csv').head(10)
out,sens=pd.read_pickle('res_robust.pkl'); val=pd.read_csv('val_hp.csv',index_col=0); mix=pd.read_csv('hp_mix.csv',index_col=0)
vk=['bat','bowl']
def nvar(role,pid):
    n=0
    for k,s in sens[role].items():
        if k in ('weights_pm30','weights_top10_freq'): continue
        if pid in s.index and s[pid]<=10: n+=1
    return n
def wf(role,pid): return sens[role]['weights_top10_freq'].get(pid,np.nan)
S=getSampleStyleSheet()
B=ParagraphStyle('b',parent=S['BodyText'],fontSize=9,leading=12.2,spaceAfter=4)
H1=ParagraphStyle('h1',parent=S['Heading1'],fontSize=13,textColor=colors.HexColor('#0B1F4B'),spaceBefore=8,spaceAfter=4)
H2=ParagraphStyle('h2',parent=S['Heading2'],fontSize=10.5,textColor=colors.HexColor('#E5007D'),spaceBefore=5,spaceAfter=3)
T=ParagraphStyle('t',parent=S['Title'],fontSize=18,textColor=colors.HexColor('#0B1F4B'))
SM=ParagraphStyle('sm',parent=B,fontSize=7.8,leading=10,textColor=colors.HexColor('#444444'))
def tbl(data,widths,fs=7.5):
    t=Table(data,colWidths=widths,repeatRows=1)
    t.setStyle(TableStyle([('FONTSIZE',(0,0),(-1,-1),fs),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0B1F4B')),('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F4F8')]),('GRID',(0,0),(-1,-1),.25,colors.HexColor('#C8CCD8')),
        ('ALIGN',(2,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5)]))
    return t
P=lambda t,s=B: Paragraph(t,s)
st=[]
st+= [P('SupeRR Selector Season 2 - Round 1',T),P('<b>Most reliable players under pressure: methodology report</b><br/>Win-probability leverage, context-adjusted value over expected, and empirical-Bayes shrinkage',ParagraphStyle('c',parent=B,alignment=1)),Spacer(1,6)]
st+= [P('1. Summary',H1),
P('We define pressure as <b>how much the next delivery can move the match</b> (a leverage index built from a win-probability model), rather than a hand-picked list of over and run-rate rules. Every delivery in the 200,999-ball dataset (IPL and T20I, 2022 to 2026) gets a continuous leverage score; the top quarter are "high pressure". Each batter and bowler is then judged on how many <b>runs above expected</b> (wickets included) they add in high-pressure deliveries, on the <b>win probability they add</b>, on how that compares with <b>their own ordinary-situation level</b>, and on how <b>consistently</b> they do it match to match. Small samples are handled by empirical-Bayes shrinkage instead of a single cut-off. The ranking is then stress-tested with 300 match-level bootstrap resamples and seven alternative model specifications.'),
P('<b>Honest headline:</b> only a few picks are very stable (Suryakumar Yadav and Phil Salt among batters; Sunil Narine among bowlers). Positions 4 to 10 in both lists sit in a tight band, and Section 6 reports exactly how often each player survives resampling.')]
st+= [P('2. Data preparation and quality checks',H1),
P('Several properties of the supplied files shaped the analysis, and each was checked against the data:'),
P('- <b>Extras codes.</b> The column <i>extras1_runs</i> is a type code (6 = no extra, 2 = wide, 3 = leg bye, 4 = bye, 1 = no ball), not a run count. Runs charged to the bowler = bat runs + 1 for wides and no-balls; byes and leg byes are not charged to bowlers; wides are not balls faced by the batter. Deliveries with extras type "other" behave as extra deliveries (over completeness is 98.2 percent when they are excluded from the legal count).'),
P('- <b>Wickets.</b> Run-outs, retired-out and obstructing the field are not credited to bowlers; a batter is only charged with an out when he is the dismissed player.'),
P('- <b>Unrecorded runs.</b> Bye and leg-bye runs are not recorded in the run column, so reconstructed totals sit slightly below official scores. Reconstructed first-minus-second innings totals match the official "won by N runs" margin within 2 runs for 49 percent and within 5 runs for 82 percent of the 385 matches decided by runs (median difference 0). We therefore removed 16 matches whose ball data contradicts the recorded result (for example a chaser who reaches the target in the data but is recorded as losing) and 570 second-innings deliveries where the first innings was incomplete, so the target is unknown.'),
P('- <b>Rain-affected matches</b> use the revised target and revised overs. Super-over deliveries (38) are excluded.'),
P('Final analysis set: 197,100 deliveries from regular innings (first innings 103,726 deliveries, second innings 93,374).')]
st+= [P('3. Defining pressure',H1),
P('<b>Step 1 - Win-probability model.</b> Separate gradient-boosted models for the first and second innings predict the batting side winning from the state after every ball: balls left, wickets lost, score (first innings), runs needed, required rate and target (second innings), and league. Predictions are out-of-fold (5 folds grouped by match), then isotonic-recalibrated. Second-innings AUC is 0.89 (Brier 0.137); first-innings AUC is 0.68 because a first-innings score alone says little about the result. Calibration is shown in Figure 1.'),
P('<b>Step 2 - Leverage index (LI).</b> For every delivery we enumerate the possible outcomes of the next legal ball (dot, 1, 2, 3, 4, 6, wicket), weight them by their empirical probability for that innings and over, and compute the expected absolute change in win probability. Dividing by the dataset average gives LI = 1 for an average ball. This automatically captures required rate, wickets in hand, balls left and closeness of the contest in one number, and it gives dead rubbers an LI near zero (no need for an arbitrary RRR cap).'),
P('<b>Step 3 - High-pressure flag.</b> A delivery is high pressure when LI is at or above the 75th percentile (LI >= 1.32): 49,276 deliveries, 25 percent of the data. A continuous score avoids the binary rules in many pressure definitions that, for example, label every first-innings death over as pressure. Here only 25 percent of first-innings death balls qualify, against 39 percent of chase death balls and 30 percent of mid-chase balls, because those are the deliveries whose outcome really moves the result.'),
P('<b>Validation.</b> High-pressure deliveries move win probability about 6 times more than ordinary ones, and carry a higher dismissal rate and a lower dot-ball rate:',B)]
rows=[['Metric','Ordinary','High pressure']]
for k in ['deliveries','mean LI','mean |dWP| per ball','bat SR','dismissal %/ball faced','dot %','boundary %','bowler econ']:
    rows.append([k.replace('mean |dWP| per ball','mean win-prob swing per ball (pts)'),f"{val.loc[k,'Ordinary']:,.2f}" if k!='deliveries' else f"{val.loc[k,'Ordinary']:,.0f}",f"{val.loc[k,'High pressure']:,.2f}" if k!='deliveries' else f"{val.loc[k,'High pressure']:,.0f}"])
st+= [tbl(rows,[7*cm,3*cm,3*cm]),Spacer(1,3),P('Note: raw strike rates are barely different (141.8 vs 138.7), which is why raw pressure strike rate is a poor measure; batters are expected to score at a similar rate but their outs and boundaries matter far more. This is why we measure value over expected, not raw rates.',SM),
Image('c1.png',width=16.5*cm,height=5.9*cm),P('Figure 1. Left: mean leverage index by over. Right: out-of-fold calibration of the win-probability model.',SM)]
st+= [P('4. Performance measurement',H1),
P('<b>Context-adjusted expected values.</b> Gradient-boosted models (out-of-fold, no player identities) predict, for each delivery, expected bat runs, probability the striker is out, expected runs charged to the bowler and probability of a bowler wicket, from over, wickets, balls left, score or runs needed, required rate and league. Expected values therefore already reflect that death overs are expensive and chases are different from first innings, putting Narine (middle overs) and a death-over bowler on equal terms.'),
P('<b>Wicket value in runs</b> is estimated from the win-probability model (win-probability change per wicket divided by per run): about 8.3 runs in the powerplay, 6.0 in the middle overs and 2.8 in the death. Per-ball value is: batter = (runs - expected runs) - wicket value x (out - expected out); bowler = (expected runs conceded - runs conceded) + wicket value x (wicket - expected wicket).'),
P('<b>Four components per player</b> (high-pressure deliveries unless noted):'),
P('1. <b>Pressure value</b>: runs above expected per 100 balls, wickets included (weight 0.35).<br/>2. <b>Win probability added</b> per 100 balls (weight 0.30).<br/>3. <b>Own-baseline delta</b>: pressure value minus the same player\'s value in ordinary deliveries (weight 0.20), answering "compared with their usual level".<br/>4. <b>Consistency</b>: share of matches (at least 6 high-pressure balls) in which the player\'s net value was positive (weight 0.15).'),
P('<b>Standardisation.</b> Components 1 to 3 are shrunk with an empirical-Bayes estimator toward the pool mean (weight = tau-squared / (tau-squared + sigma-squared / n), with variances estimated from the data), then standardised using the raw spread so that shrinkage truly reduces a noisy component\'s influence. The own-baseline delta is almost pure noise for most players (its shrinkage weight is small), which is itself a finding: "clutch" is far better measured by high-pressure <i>level</i> relative to context than by the gap to a baseline. Consistency uses a Beta-style prior of 8 pseudo-matches at 50 percent.')]
st+= [P('5. Fair comparisons',H1),
P('- <b>Eligibility:</b> at least 150 high-pressure deliveries, at least 8 high-pressure matches, and at least 100 ordinary deliveries (100 batters and 102 bowlers qualify). Shrinkage, not the cut-off alone, controls small-sample luck.<br/>- <b>IPL and T20I:</b> pooled so players who appear in both are compared on one scale; the expected-value models include a league indicator, and rankings are re-run on IPL-only and T20I-only data (Section 6).<br/>- <b>Different contexts:</b> phase, innings, wickets and chase state are inside the expected values and the win-probability model, so a death-over specialist is not rewarded merely for his role.<br/>- <b>Names:</b> player IDs map one-to-one to names in the ball-by-ball file.')]
st+= [P('6. Results and evidence',H1),P('<b>Top 10 batters under pressure</b>',H2)]
rows=[['#','Batter','HP balls','HP runs','SR','Avg','Net/100','WPA/100','Cons.','Top10 boot.','Top10 var.']]
for _,r in fb.iterrows(): rows.append([int(r['rank']),r['name'],int(r.balls),int(r.runs),f"{r.SR:.0f}",f"{r.avg:.1f}",f"{r.net_hp:.1f}",f"{r.wpa_hp:.2f}",f"{r.cons:.2f}",f"{r.p_top10:.0%}",f"{nvar('bat',r.pid)}/7"])
st+= [tbl(rows,[.7*cm,3.6*cm,1.3*cm,1.3*cm,1*cm,1*cm,1.4*cm,1.5*cm,1.1*cm,1.6*cm,1.5*cm]),
P('HP = high pressure. Net/100 = runs above expected per 100 balls including wicket cost. WPA/100 = win probability added per 100 balls (points of probability). Top10 boot. = share of 300 match bootstrap resamples in which the player is top 10. Top10 var. = number of the 7 alternative specifications (thresholds, chase-only, IPL-only, T20I-only, wicket value x0.5 and x1.5) in which he is top 10.',SM),P('<b>Top 10 bowlers under pressure</b>',H2)]
rows=[['#','Bowler','HP balls','Wkts','Econ','Ord. econ','Dot %','Net/100','WPA/100','Top10 boot.','Top10 var.']]
for _,r in fw.iterrows(): rows.append([int(r['rank']),r['name'],int(r.balls),int(r.wkts),f"{r.econ:.2f}",f"{r.econ_ord:.2f}",f"{r.get('dot%'):.0f}",f"{r.net_hp:.1f}",f"{r.wpa_hp:.2f}",f"{r.p_top10:.0%}",f"{nvar('bowl',r.pid)}/7"])
st+= [tbl(rows,[.7*cm,3.6*cm,1.3*cm,1.1*cm,1.1*cm,1.5*cm,1.1*cm,1.4*cm,1.5*cm,1.6*cm,1.5*cm]),Spacer(1,4),
Image('c2.png',width=16.5*cm,height=7.0*cm),P('Figure 2. Pressure value against ordinary-situation value. Points above the dashed line perform better under pressure than usual; bubble size is the number of high-pressure deliveries.',SM)]
st+= [P('Reading the results',H2),
P('<b>Suryakumar Yadav</b> is top in the base ranking, rank 1 in 5 of the 7 variants and top 10 in all 7. He combines the biggest pressure sample (697 balls) with a high pressure value (+39 runs per 100 balls above expected) and a positive gap to his own baseline. <b>Phil Salt</b> posts a similar rate on a smaller sample. <b>Tim David</b> and <b>Abhishek Sharma</b> score at about the same level in pressure as in ordinary situations (negative delta): they are reliable, not extra-elevated. <b>Babar Azam</b>, <b>Fakhar Zaman</b> and <b>Vaibhav Sooryavanshi</b> rely on samples under 250 balls and are most exposed to resampling noise.'),
P('<b>Sunil Narine</b> is the clear leading bowler (6.51 economy against 6.99 in ordinary situations, 24 wickets in 389 high-pressure balls, top 10 in 96 percent of resamples). <b>Abrar Ahmed</b>, <b>Mitchell Santner</b>, <b>Jacob Duffy</b> and <b>Matheesha Pathirana</b> follow, with Duffy and Abrar resting on 160 to 180 pressure balls.'),
P('<b>Where well-known names sit:</b> Rashid Khan ranks 14th, Jasprit Bumrah 26th, Varun Chakravarthy 17th and Arshdeep Singh 71st among bowlers; Tilak Varma ranks 43rd and David Miller 94th among batters. Their values are mostly close to or below expectation once phase and match state are accounted for, e.g. Arshdeep concedes more than expected for the situations he bowls in. This is a statement about 2022 to 2026 IPL and T20I data under this definition, not about overall ability.'),
Image('c3.png',width=16.5*cm,height=6.4*cm),P('Figure 3. Bootstrap stability: share of 300 resamples of matches in which each finalist is in the top 10 (navy) and top 5 (pink).',SM)]
st+= [P('7. Reliability checks and limitations',H1),
P('<b>Checks run.</b> (a) Out-of-fold models everywhere, so no player is evaluated on a match the models saw. (b) 300 bootstrap resamples of matches, recomputing eligibility, shrinkage and ranks each time. (c) Seven alternative specifications: threshold at the 67th and 85th percentile, chase only, IPL only, T20I only, wicket value x0.5 and x1.5. (d) 100 random perturbations of the four weights by up to plus or minus 30 percent; nine of the ten batters and nine of the ten bowlers stay in the top 10 in at least 90 percent of perturbations.'),
P('<b>Where the model is less certain.</b><br/>- Ranks 4 to 10 are close; the bootstrap shows the ordering there is partly luck of the sample, so we recommend treating them as a tier rather than a strict order.<br/>- First-innings pressure is measured less precisely (win-probability AUC 0.68).<br/>- Bye and leg-bye runs are not in the data and some final balls of chases are missing (about 17 percent of second innings end before the last recorded ball), which slightly biases required rates and removes some finishing blows.<br/>- No pitch, dew, boundary size, opposition strength or batter-bowler matchup data are modelled. Different leagues and opponents (for example T20I versus associate sides) are only handled through a league indicator.<br/>- The per-player sample is 150 to 700 pressure balls; no method can fully separate skill from luck at that size. Shrinkage and the bootstrap make this explicit rather than hiding it.<br/>- The isotonic recalibration was fitted on the same out-of-fold predictions it corrects, so calibration plots slightly flatter the model.')]
st+= [P('8. Reproducibility',H1),P('Pipeline: (1) rebuild ball state and extras logic; (2) fit out-of-fold win-probability and expected-value models (histogram gradient boosting, 5 folds by match, seed fixed); (3) compute leverage and per-ball value; (4) aggregate by player and match, apply empirical-Bayes shrinkage and the weighted index; (5) bootstrap and sensitivity runs. All thresholds and weights are stated above. The data pack was used only for this competition.')]

av=pd.read_csv('availability.csv')
def short(r):
    if r.nationality=='Pakistan': return 'Not IPL-eligible in practice'
    if str(r.status).startswith('Believed'): return 'Believed retired - verify'
    if isinstance(r.ipl2026,str) and r.ipl2026: return 'Contracted 2026; decision due'
    if 'No IPL squad' in r.status: return 'No IPL listing 2022-26'
    return 'Not in 2026 squad'
st+=[PageBreak(),P('9. Auction actionability (provisional)',H1),
P('The ranking above is a pure performance ranking, as the brief asks. Because the end goal is the IPL 2027 auction (reported for 16 December, with retention lists reported due 17 November), we also flag who can realistically be bought. <b>Retention outcomes are not yet known</b>: the notes below use the 2026 squad listings in the data pack and press reports, and must be re-checked once official lists are out. Nationality is the player\'s most frequent T20I side in the data pack (a few from outside knowledge for players with no T20I record).')]
for role,lab in [('bat','Batters'),('bowl','Bowlers')]:
    d=av[(av.role==role)&(av['rank']<=10)].sort_values('rank')
    rows=[['#',lab[:-1],'Nationality','IPL 2026 team','Availability flag']]
    for _,r in d.iterrows(): rows.append([int(r['rank']),r['name'],r.nationality,r.ipl2026 if isinstance(r.ipl2026,str) and r.ipl2026 else '-',short(r)])
    st+=[tbl(rows,[.8*cm,4*cm,2.8*cm,5*cm,4.4*cm],7.5),Spacer(1,5)]
st+=[P('<b>Key flags.</b> Babar Azam, Fakhar Zaman (batters) and Abrar Ahmed (bowlers) are Pakistani and effectively cannot be bought for the IPL; they rank on pure performance only. Suryakumar Yadav is expected to stay at MI (reports describe him as not for sale or trade, though one report speculates an exit; nothing is official). Phil Salt and Tim David (RCB), Abhishek Sharma (SRH), Shubman Gill (GT), Sunil Narine (KKR) and Santner (MI) are all under 2026 contracts, so retention decides whether they ever reach the auction.'),
P('<b>Availability-adjusted alternative (Option B).</b> Removing Pakistani and retired players, the batter list becomes Yadav, Salt, David, Abhishek Sharma, Pooran, Gill, Sooryavanshi, Nissanka, Seifert, Chapman; the bowler list becomes Narine, Santner, Duffy, Pathirana, Taskin Ahmed, Ferguson, Hazlewood, Krunal Pandya, Axar Patel, Jofra Archer. Players added from outside the main list (Seifert, Chapman, Archer) have only 13 to 18 percent bootstrap top-10 probability, so Option B trades some statistical stability for relevance. The submitted ranking stays the pure performance list unless the author decides otherwise.'),
P('<b>RR target pool.</b> High scorers with no 2026 IPL squad listing include Mohit Sharma, Mujeeb Ur Rahman, Tim Southee, Sediqullah Atal, Glenn Maxwell, Andre Russell and Shai Hope. Whether each registers for the auction, and at what price, is unknown; these are leads to verify, not recommendations.')]
SimpleDocTemplate('outputs/SupeRR_Selector_Methodology_Report_v2.pdf',pagesize=A4,leftMargin=1.6*cm,rightMargin=1.6*cm,topMargin=1.5*cm,bottomMargin=1.5*cm,title='SupeRR Selector Season 2 Methodology Report').build(st)
