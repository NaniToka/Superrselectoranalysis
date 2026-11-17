import os
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

print("--- Building Clean Verified Master Methodology Report PDF ---")

# 1. Load verified data
exp_df = pd.read_csv('expected_dashboard_values.csv')
bat_top = exp_df[exp_df['role'] == 'bat'].sort_values('rank')
bowl_top = exp_df[exp_df['role'] == 'bowl'].sort_values('rank')

tac_df = pd.read_csv('tactical_splits_verified.csv')

# Load original model for comparison tag
r_orig, _ = pd.read_pickle('res_main.pkl')

# Colors
NAVY = HexColor('#041126')
PINK = HexColor('#E5007D')
GREY_BG = HexColor('#F8FAFC')
BORDER_CLR = HexColor('#E2E8F0')
TEXT_MUTED = HexColor('#64748B')
WHITE = HexColor('#FFFFFF')
LIGHT_GREY = HexColor('#F1F5F9')

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'DocTitle', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=NAVY
)
h1_style = ParagraphStyle(
    'H1', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=NAVY, spaceAfter=4, spaceBefore=6
)
h2_style = ParagraphStyle(
    'H2', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=PINK, spaceAfter=2, spaceBefore=4
)
body_style = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontName='Helvetica', fontSize=7.2, leading=9.5, textColor=HexColor('#1E293B')
)
note_style = ParagraphStyle(
    'Note', parent=styles['Normal'],
    fontName='Helvetica-Oblique', fontSize=6.5, leading=8.5, textColor=TEXT_MUTED
)

def make_table(data, widths, fs=6.8, alignments=None, grey_rows=None):
    if grey_rows is None:
        grey_rows = []
    formatted = []
    for r_idx, row in enumerate(data):
        fmt_row = []
        for c_idx, cell in enumerate(row):
            align = alignments[c_idx] if alignments else 'CENTER'
            f_size = fs if r_idx > 0 else fs + 0.2
            weight = 'Helvetica-Bold' if (r_idx == 0 or c_idx == 1) else 'Helvetica'
            clr = WHITE if r_idx == 0 else (TEXT_MUTED if r_idx in grey_rows else HexColor('#0F172A'))
            fmt_row.append(Paragraph(
                f"<para align='{align.lower()}'><font face='{weight}' size='{f_size}' color='{clr.hexval()}'>{cell}</font></para>",
                body_style
            ))
        formatted.append(fmt_row)
    
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_CLR),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]
    for r_idx in range(1, len(data)):
        if r_idx in grey_rows:
            t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), LIGHT_GREY))
        elif r_idx % 2 == 1:
            t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), GREY_BG))
            
    return Table(formatted, colWidths=widths, style=TableStyle(t_style))

doc_elements = []

# =========================================================================
# PAGE 1: EXECUTIVE BRIEF & OFFICIAL TOP 10 RANKINGS
# =========================================================================
header_data = [
    [
        Paragraph("<b>RAJASTHAN ROYALS &bull; SUPERR SELECTOR SEASON 2</b><br/><font size='7' color='#64748B'>Round 1 Submission &bull; Verified 4-Pillar Opposition-Adjusted Model &bull; Evaluated on 197,100 Deliveries</font>", title_style),
        Paragraph("<para align='right'><font size='7.5' color='#E5007D'><b>SELECTION METHODOLOGY REPORT</b></font><br/><font size='6.5' color='#64748B'>Target: Round 2 (Mumbai) &bull; Round 3 (Goa)</font></para>", body_style)
    ]
]
t_head = Table(header_data, colWidths=[12.5*cm, 5.3*cm])
t_head.setStyle(TableStyle([
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('TOPPADDING', (0,0), (-1,-1), 0),
    ('LEFTPADDING', (0,0), (-1,-1), 0),
    ('RIGHTPADDING', (0,0), (-1,-1), 0),
]))
doc_elements.append(t_head)
doc_elements.append(HRFlowable(width="100%", thickness=1.5, color=PINK, spaceAfter=5, spaceBefore=3))

doc_elements.append(Paragraph("1. Executive Summary: The Continuous Leverage Framework", h1_style))
doc_elements.append(Paragraph(
    "This report documents the official submission for the Rajasthan Royals SupeRR Selector Season 2 (Round 1). "
    "Rather than defining high pressure through arbitrary binary phases (such as death overs or required run rate thresholds), "
    "we model pressure continuously using an out-of-fold calibrated <b>Win-Probability Leverage Index (LI)</b> across all 197,100 deliveries "
    "from the 2022&ndash;2026 IPL and T20 International tournament dataset (958 players total; extras1_runs is a type code; byes and leg-bye runs are unrecorded). "
    "Deliveries in the top quartile (<b>LI &ge; 1.32</b>; 49,276 deliveries) are designated as High Pressure, where average win-probability swing per ball "
    "surges to <b>3.73 percentage points</b> compared to <b>0.62 percentage points</b> in ordinary play (a 6.0&times; volatility increase). "
    "Players meeting qualification thresholds (&ge;150 HP deliveries, &ge;8 HP matches of 6+ balls each, and &ge;100 ordinary balls) are evaluated: "
    "<b>100 batters and 102 bowlers qualify</b>. Each candidate is ranked on a 4-pillar composite function: "
    "<b>Pressure Value (35%)</b>, <b>Win Probability Added (30%)</b>, <b>Delta vs Baseline (20%)</b>, and <b>Consistency (15%)</b>, "
    "with Empirical Bayes shrinkage and leave-one-match-out opponent quality adjustments applied. Rankings are stress-tested across 200 match-level bootstrap resamples for the adjusted model (300 for original).",
    body_style
))
doc_elements.append(Spacer(1, 3))

# Top 10 Batters Table
doc_elements.append(Paragraph("<b>Table 1: Official Top 10 Batters Under High Pressure (Opposition-Adjusted Model)</b>", h2_style))
bat_rows = [['#', 'Batter', 'HP Balls', 'HP Runs', 'Outs', 'HP SR', 'Net/100', 'Delta', 'WPA/100', 'Cons.', 'Adj Score', 'Orig', 'Boot %']]
for _, r in bat_top.iterrows():
    orig_rk = int(r.get('orig_rank', r['rank']))
    bat_rows.append([
        f"<b>{int(r['rank'])}</b>", r['player'], f"{int(r.hp_balls)}", str(r.get('hp_runs', '-')), str(r.get('outs', '-')),
        f"{float(r.sr):.1f}" if str(r.get('sr', '')).replace('.','').isdigit() else '-',
        f"{float(r.net_100):+.2f}", f"{float(r.delta):+.2f}", f"{float(r.wpa_100):+.3f}",
        f"{float(r.consistency)*100:.1f}%", f"<b>{float(r.score):.3f}</b>", f"{orig_rk}", f"{float(r.boot_top10):.1f}%"
    ])
doc_elements.append(make_table(bat_rows, [0.6*cm, 3.8*cm, 1.2*cm, 1.2*cm, 0.9*cm, 1.2*cm, 1.4*cm, 1.3*cm, 1.3*cm, 1.3*cm, 1.4*cm, 0.9*cm, 1.2*cm],
                               alignments=['CENTER', 'LEFT', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER']))
doc_elements.append(Spacer(1, 4))

# Top 10 Bowlers Table
doc_elements.append(Paragraph("<b>Table 2: Official Top 10 Bowlers Under High Pressure (Opposition-Adjusted Model)</b>", h2_style))
bowl_rows = [['#', 'Bowler', 'HP Balls', 'Legal', 'Wkts', 'Econ', 'Dot %', 'Net/100', 'Delta', 'WPA/100', 'Cons.', 'Adj Score', 'Orig', 'Boot %']]
for _, r in bowl_top.iterrows():
    orig_rk = int(r.get('orig_rank', r['rank']))
    bowl_rows.append([
        f"<b>{int(r['rank'])}</b>", r['player'], f"{int(r.hp_balls)}", str(r.get('legal_balls', r.hp_balls)), str(r.get('wkts', '-')),
        f"{float(r.econ):.2f}" if str(r.get('econ', '')).replace('.','').isdigit() else '-',
        f"{float(r.dot_pct):.1f}%" if str(r.get('dot_pct', '')).replace('.','').isdigit() else '-',
        f"{float(r.net_100):+.2f}", f"{float(r.delta):+.2f}", f"{float(r.wpa_100):+.3f}",
        f"{float(r.consistency)*100:.1f}%", f"<b>{float(r.score):.3f}</b>", f"{orig_rk}", f"{float(r.boot_top10):.1f}%"
    ])
doc_elements.append(make_table(bowl_rows, [0.6*cm, 3.8*cm, 1.2*cm, 1.1*cm, 0.9*cm, 1.2*cm, 1.1*cm, 1.4*cm, 1.3*cm, 1.3*cm, 1.3*cm, 1.4*cm, 0.9*cm, 1.2*cm],
                               alignments=['CENTER', 'LEFT', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER']))
doc_elements.append(Spacer(1, 4))

# Executive Callout
doc_elements.append(Paragraph(
    "<b>KEY STRATEGIC OBSERVATIONS FOR THE DUGOUT:</b><br/>"
    "&bull; <b>The Raw Strike Rate Illusion:</b> Batting SR under high pressure is virtually identical to ordinary overs (141.84 vs 138.72). Pressure does not change how fast batters score; what changes is a +5% jump in dismissal rate and a 6.0&times; surge in win-probability swing per ball.<br/>"
    "&bull; <b>In-House Asset (Vaibhav Sooryavanshi):</b> Ranked #8 globally under pressure (+75.76 Net/100, 231.1 SR, 1.209 WPA/100). He represents an exceptional in-house development asset for Rajasthan Royals.<br/>"
    "&bull; <b>Tier Dynamics:</b> Narine (93.0% boot), Salt (82.0%), and Surya (76.0%) form a stable core. Ranks 4 to 10 exhibit bootstrap survival rates of 20% to 60%, confirming they form a tactical cohort sensitive to matchup nuances.<br/>"
    "&bull; <b>Actionable Candidates (Option B):</b> Removing players unavailable for the IPL (Babar Azam, Fakhar Zaman, Abrar Ahmed) advances <b>Harry Brook</b> (#10 Bat) and <b>Mohit Sharma</b> (#9 Bowl) into actionable priority.",
    body_style
))

doc_elements.append(PageBreak())

# =========================================================================
# PAGE 2: DATA PREPARATION & STATE-SPACE LEVERAGE ENGINE
# =========================================================================
doc_elements.append(Paragraph("2. Data Preparation, Integrity Audits & Screenings", h1_style))
doc_elements.append(Paragraph(
    "The dataset spans 876 matches from 2022 to 2026 across the IPL and T20 Internationals (958 players total). "
    "Audits established key data engineering boundaries:<br/>"
    "&bull; <b>Extras Handling:</b> In the raw feed, <code>extras1_runs</code> is an integer categorical type code (6 = none, 2 = wide, 3 = leg-bye, 4 = bye, 1 = no-ball), NOT a run tally. "
    "Batters face legal balls + no-balls (wides excluded). Bowlers are debited for bat runs + 1 run for wides and no-balls; byes and leg-byes are excluded from bowler concession.<br/>"
    "&bull; <b>Dismissal Attribution:</b> Only bowler-dismissals (bowled, caught, lbw, stumped, hit wicket) are credited to the bowler. Run-outs and other indirect dismissals are excluded from bowler credit.<br/>"
    "&bull; <b>Screening:</b> 16 matches where scorecards contradicted official match margins and 570 second-innings deliveries with unrecorded targets were dropped. Super overs (38 balls) were removed.<br/>"
    "&bull; <b>Clean Base:</b> Exactly <b>197,100 deliveries</b> across 860 matches.",
    body_style
))
doc_elements.append(Spacer(1, 3))

doc_elements.append(Paragraph("3. Continuous Leverage Index (LI) Formulation", h1_style))
doc_elements.append(Paragraph(
    "Pressure is defined continuously through win-probability sensitivity:<br/>"
    "&bull; <b>Win-Probability Model:</b> Separate Histogram Gradient-Boosted Classifiers (HGB) predict batting-side victory from post-delivery match state (5 folds grouped by match, seed-fixed). "
    "Chase model features include balls remaining, wickets lost, runs required, and required run rate (AUC = 0.886, Brier = 0.137). Innings 1 model uses balls left, wickets, and score (AUC = 0.684). Both are recalibrated out-of-fold via Isotonic Regression.<br/>"
    "&bull; <b>Leverage Formulation:</b> For each ball, we evaluate possible outcomes $o \\in \\{0, 1, 2, 3, 4, 6, W\\}$ weighted by transition frequencies $p(o \\mid \\text{innings, over})$:<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;$$LI_{\\text{raw}} = \\sum_{o} p(o \\mid \\text{innings, over}) \\cdot \\left| \\mathcal{P}(s_{t+1} \\mid o) - \\mathcal{P}(s_t) \\right|, \\quad LI = \\frac{LI_{\\text{raw}}}{\\mathbb{E}[LI_{\\text{raw}}]}$$<br/>"
    "Deliveries sitting in the top quartile (<b>LI &ge; 1.32</b>, 75th percentile) are classified as <b>High Pressure</b> ($N = 49,276$).",
    body_style
))
doc_elements.append(Spacer(1, 3))

if os.path.exists('c1.png'):
    doc_elements.append(Image('c1.png', width=17.5*cm, height=5.2*cm))
    doc_elements.append(Paragraph("<b>Figure 1:</b> Left &mdash; Mean Leverage Index by over across innings. Right &mdash; Out-of-fold win probability calibration curves.", note_style))

doc_elements.append(PageBreak())

# =========================================================================
# PAGE 3: 4-PILLAR MODEL & CASE STUDY: JASPRIT BUMRAH
# =========================================================================
doc_elements.append(Paragraph("4. Context-Adjusted Value Over Expected & Dynamic Wicket Valuation", h1_style))
doc_elements.append(Paragraph(
    "Deliveries are valued against expected runs and expected dismissal probabilities conditional on match state:<br/>"
    "&bull; <b>Dynamic Wicket Valuation:</b> A wicket's value depends on remaining batting resources: "
    "<b>&lambda; = 8.3 runs</b> in Powerplay, <b>6.0 runs</b> in Middle overs, and <b>2.8 runs</b> at Death.<br/>"
    "&bull; <b>Net Runs Added:</b> Batter value is $v_{\\text{bat}} = (R_t - \\mathbb{E}[R_t]) - \\lambda_t (\\mathbb{I}_{\\text{out}} - \\mathbb{P}[\\text{out}])$. "
    "Bowler value is $v_{\\text{bowl}} = (\\mathbb{E}[R_t] - R_t) + \\lambda_t (\\mathbb{I}_{\\text{wkt}} - \\mathbb{P}[\\text{wkt}])$.<br/>"
    "&bull; <b>Empirical Bayes Shrinkage:</b> Raw metric averages are shrunk toward population priors to eliminate small-sample noise.<br/>"
    "&bull; <b>Opposition Quality Adjustment:</b> Leave-one-match-out opponent quality scaling normalizes for strength of bowling and batting attacks faced.",
    body_style
))
doc_elements.append(Spacer(1, 3))

doc_elements.append(Paragraph("5. Analysis of Jasprit Bumrah & Model Boundaries", h1_style))
bumrah_text = (
    "<b>OBSERVATIONS ON JASPRIT BUMRAH (Rank #24 Adjusted &bull; Rank #26 Original):</b><br/>"
    "In high-pressure deliveries (LI &ge; 1.32), Jasprit Bumrah has <b>506 deliveries</b>, with <b>42.2% dot balls</b>, "
    "a batter strike rate of <b>125.4</b>, and <b>20 wickets</b> against <b>27.8 expected</b>. "
    "His pressure value is <b>+15.73 Net/100</b>, while his ordinary-level gap (Delta) is <b>-11.19</b>.<br/>"
    "<i>Analytical Limitation:</i> While one possible hypothesis is that opposing batters adopt an unusually risk-averse approach against him (choosing not to attack and depressing per-ball wicket events), "
    "<b>the underlying cause (e.g. batter risk aversion vs. match situation vs. execution) is untested in the data pack.</b> "
    "Our model reports the empirical per-ball value without imposing speculative adjustments."
)
doc_elements.append(Table([[Paragraph(bumrah_text, body_style)]], colWidths=[17.8*cm], 
                          style=TableStyle([
                              ('BACKGROUND', (0,0), (-1,-1), GREY_BG),
                              ('BOX', (0,0), (-1,-1), 1.0, BORDER_CLR),
                              ('TOPPADDING', (0,0), (-1,-1), 4),
                              ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                              ('LEFTPADDING', (0,0), (-1,-1), 8),
                              ('RIGHTPADDING', (0,0), (-1,-1), 8),
                          ])))
doc_elements.append(Spacer(1, 4))

if os.path.exists('c2.png'):
    doc_elements.append(Image('c2.png', width=17.5*cm, height=5.5*cm))
    doc_elements.append(Paragraph("<b>Figure 2:</b> High-Pressure Net Value vs Ordinary Situation Baseline (Points above diagonal indicate players elevating under pressure).", note_style))

doc_elements.append(PageBreak())

# =========================================================================
# PAGE 4: TACTICAL MATCHUPS (PACE/SPIN & PHASE SPLITS)
# =========================================================================
doc_elements.append(Paragraph("6. Tactical Splits: Pace vs. Spin & Phase Deployments", h1_style))
doc_elements.append(Paragraph(
    "High-pressure execution was examined across bowling disciplines and innings phases using verified splits. "
    "Rows with fewer than 100 deliveries are flagged with wider standard errors:",
    body_style
))
doc_elements.append(Spacer(1, 2))

# Batter Pace/Spin Table from tactical_splits_verified.csv
doc_elements.append(Paragraph("<b>Table 3: Batter Pace vs. Spin Splits in High Pressure</b>", h2_style))
bat_sp = tac_df[tac_df['role'] == 'bat']
bat_sp_rows = [['Player', 'Split', 'HP Balls', 'Runs', 'SR', 'Net/100', 'Std. Error (&plusmn;)', 'Sample Flag']]
grey_bat_rows = []
for idx, (_, r) in enumerate(bat_sp.iterrows(), start=1):
    is_low = str(r['sample_flag']).startswith('LOW')
    if is_low:
        grey_bat_rows.append(idx)
    bat_sp_rows.append([
        r['player'], r['split'], str(r['hp_balls']), str(r['runs_scored_or_conceded']),
        f"{r['strike_rate_or_econ']:.1f}", f"{r['net100']:+.2f}", f"&plusmn;{r['std_err']:.1f}", r['sample_flag']
    ])

doc_elements.append(make_table(bat_sp_rows, [3.8*cm, 1.8*cm, 1.6*cm, 1.6*cm, 1.8*cm, 2.0*cm, 2.4*cm, 2.8*cm], fs=6.2,
                               alignments=['LEFT', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER'],
                               grey_rows=grey_bat_rows))
doc_elements.append(Spacer(1, 4))

doc_elements.append(Paragraph(
    "<b>Analytical Takeaways:</b><br/>"
    "&bull; <b>Phil Salt:</b> Demonstrates matched returns across pace (+36.93 Net/100, 173.7 SR, 224 balls) and spin (+36.69 Net/100, 179.1 SR, 115 balls).<br/>"
    "&bull; <b>Babar Azam:</b> High return against pace (+47.43 Net/100, 182.1 SR, 145 balls) compared to spin (-20.02 Net/100, 120.0 SR, 75 balls; note: spin sample is low).<br/>"
    "&bull; <b>Shubman Gill:</b> High execution against spin (+45.12 Net/100, 169.7 SR, 201 balls) vs. pace (-1.20 Net/100, 149.6 SR, 363 balls).",
    body_style
))

doc_elements.append(PageBreak())

# =========================================================================
# PAGE 5: BOWLER PHASE SPLITS & AUCTION ACTIONABILITY (OPTION B)
# =========================================================================
doc_elements.append(Paragraph("7. Bowler Phase Deployments & Auction Actionability (Option B)", h1_style))
doc_elements.append(Paragraph(
    "Phase-specific delivery data identifies where bowlers have historically produced high-pressure returns:",
    body_style
))
doc_elements.append(Spacer(1, 2))

# Bowler Phase Table from tactical_splits_verified.csv
doc_elements.append(Paragraph("<b>Table 4: Bowler Phase Splits in High Pressure (PP, Mid, Death)</b>", h2_style))
bowl_sp = tac_df[tac_df['role'] == 'bowl']
bowl_sp_rows = [['Bowler', 'Phase', 'HP Deliveries', 'Runs Conceded', 'Economy', 'Net/100', 'Std. Error (&plusmn;)', 'Sample Flag']]
grey_bowl_rows = []
for idx, (_, r) in enumerate(bowl_sp.iterrows(), start=1):
    is_low = str(r['sample_flag']).startswith('LOW')
    if is_low:
        grey_bowl_rows.append(idx)
    bowl_sp_rows.append([
        r['player'], r['split'], str(r['hp_balls']), str(r['runs_scored_or_conceded']),
        f"{r['strike_rate_or_econ']:.2f}", f"{r['net100']:+.2f}", f"&plusmn;{r['std_err']:.1f}", r['sample_flag']
    ])

doc_elements.append(make_table(bowl_sp_rows, [3.8*cm, 1.8*cm, 1.8*cm, 1.8*cm, 1.8*cm, 2.0*cm, 2.2*cm, 2.6*cm], fs=5.8,
                               alignments=['LEFT', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER'],
                               grey_rows=grey_bowl_rows))
doc_elements.append(Spacer(1, 4))

doc_elements.append(Paragraph(
    "<b>Actionable Selection Architecture (Option B):</b><br/>"
    "&bull; <b>Exclusions:</b> Babar Azam (#4 Bat), Fakhar Zaman (#9 Bat), and Abrar Ahmed (#2 Bowl) cannot participate in the IPL due to geopolitical restrictions.<br/>"
    "&bull; <b>Elevated Candidates:</b> Removing non-actionable entries elevates <b>Harry Brook</b> (#10 Bat) and <b>Tim Seifert</b> (#11 Bat) in the batting order, and advances <b>Mohit Sharma</b> (#9 Bowl) and <b>Krunal Pandya</b> (#10 Bowl) in the bowling order.<br/>"
    "&bull; <b>Tournament Road:</b> This submission targets Round 2 on-site in Mumbai, leading to Round 3 in Goa for the Round 2 winner.",
    body_style
))

# Build Document
doc = SimpleDocTemplate(
    'outputs/SupeRR_Selector_Methodology_Report_v2.pdf',
    pagesize=A4,
    leftMargin=1.5*cm,
    rightMargin=1.5*cm,
    topMargin=1.3*cm,
    bottomMargin=1.3*cm
)

doc.build(doc_elements)
print("--- PDF Report re-compiled successfully at outputs/SupeRR_Selector_Methodology_Report_v2.pdf! ---")
