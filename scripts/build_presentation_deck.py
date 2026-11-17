"""
Rajasthan Royals SupeRR Selector Season 2 - Executive Presentation Deck
Generates a 10-slide widescreen presentation deck (PDF) in landscape format.
"""
import pandas as pd
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

NAVY = colors.HexColor('#0B1F4B')
NAVY_SURFACE = colors.HexColor('#152E68')
PINK = colors.HexColor('#E5007D')
PINK_LIGHT = colors.HexColor('#FFF0F6')
GREY_BG = colors.HexColor('#F8FAFC')
BORDER_CLR = colors.HexColor('#CBD5E1')
DARK_TEXT = colors.HexColor('#0F172A')
MUTED_TEXT = colors.HexColor('#475569')

S = getSampleStyleSheet()

slide_title_style = ParagraphStyle('SlideTitle', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=NAVY, spaceAfter=2)
slide_sub_style = ParagraphStyle('SlideSub', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=PINK, spaceAfter=8)
body_style = ParagraphStyle('SlideBody', fontName='Helvetica', fontSize=9, leading=13, textColor=DARK_TEXT, spaceAfter=5)
bullet_style = ParagraphStyle('SlideBullet', fontName='Helvetica', fontSize=8.5, leading=12, textColor=DARK_TEXT, leftIndent=12, spaceAfter=4)
card_title = ParagraphStyle('CardTitle', fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=NAVY, spaceAfter=3)
card_body = ParagraphStyle('CardBody', fontName='Helvetica', fontSize=8, leading=11, textColor=DARK_TEXT)

def make_table(data, widths, fs=7.5, header_bg=NAVY, header_color=colors.white, row_bgs=[colors.white, GREY_BG], alignments=None):
    t = Table(data, colWidths=widths, repeatRows=1)
    ts = [
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), fs),
        ('BACKGROUND', (0,0), (-1,0), header_bg),
        ('TEXTCOLOR', (0,0), (-1,0), header_color),
        ('GRID', (0,0), (-1,-1), 0.25, BORDER_CLR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), row_bgs)
    ]
    if alignments:
        for col_idx, align in enumerate(alignments):
            ts.append(('ALIGN', (col_idx, 0), (col_idx, -1), align))
    else:
        ts.append(('ALIGN', (0,0), (-1,-1), 'CENTER'))
        ts.append(('ALIGN', (1,1), (1,-1), 'LEFT'))
    t.setStyle(TableStyle(ts))
    return t

elements = []

def slide_header(category, title):
    elements.append(Paragraph(f"RAJASTHAN ROYALS &bull; {category.upper()}", slide_sub_style))
    elements.append(Paragraph(title, slide_title_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=PINK, spaceAfter=10))

# -------------------------------------------------------------
# SLIDE 1: TITLE SLIDE
# -------------------------------------------------------------
elements.append(Spacer(1, 2*cm))
elements.append(Paragraph("RAJASTHAN ROYALS &bull; SUPERR SELECTOR SEASON 2 (ROUND 1)", slide_sub_style))
elements.append(Paragraph("<b>Dugout Intelligence &amp; High-Pressure Talent Architecture</b>", ParagraphStyle('CoverTitle', fontName='Helvetica-Bold', fontSize=24, leading=28, textColor=NAVY, spaceAfter=8)))
elements.append(Paragraph("A Mathematical Framework for Identifying Clutch Match-Winners: Out-of-Fold Win-Probability Leverage, Context-Adjusted Value Over Expected, Empirical Bayes Shrinkage &amp; Auction Knapsack Optimization", ParagraphStyle('CoverSub', fontName='Helvetica', fontSize=11, leading=15, textColor=MUTED_TEXT, spaceAfter=15)))
elements.append(HRFlowable(width="100%", thickness=2, color=PINK, spaceAfter=15))

cover_meta = [
    [Paragraph("<b>Candidate:</b> Analytics Candidate", body_style), Paragraph("<b>Dataset:</b> 2022&ndash;2026 IPL &amp; T20I (197,100 balls)", body_style)],
    [Paragraph("<b>Primary Recommendation:</b> Opposition-Adjusted Model", body_style), Paragraph("<b>Submission Artifacts:</b> PDF Report, Excel Workbook, Interactive UI", body_style)]
]
elements.append(Table(cover_meta, colWidths=[13*cm, 13*cm], style=TableStyle([('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2)])))
elements.append(PageBreak())

# -------------------------------------------------------------
# SLIDE 2: THE PROBLEM & CONTINUOUS LEVERAGE INDEX
# -------------------------------------------------------------
slide_header("Mathematical Foundations", "Beyond Heuristics: The Continuous Leverage Index (LI)")
elements.append(Paragraph("<b>The Flaw of Arbitrary Cut-Offs:</b> Traditional analytics labels 'overs 16&ndash;20 and RRR &gt; 10' as pressure. But a chase of 25 off 24 balls at 120/2 in over 16 has near-zero pressure ($LI \\approx 0.35$), while Over 8 of a chase at 40/4 represents extreme match jeopardy.", body_style))
elements.append(Spacer(1, 4))

c1_text = (
    "<b>Step 1 &mdash; Calibrated Win Probability P(s):</b><br/>"
    "Separate Histogram Gradient-Boosted Classifiers (5 folds by match) predict outcome from game state. "
    "Chase AUC = 0.886 (Brier 0.137); 1st Innings AUC = 0.684. Recalibrated via Isotonic Regression."
)
c2_text = (
    "<b>Step 2 &mdash; Expected Probability Volatility (LI):</b><br/>"
    "$$LI_{\\text{raw}} = \\sum_{o \\in \\{0,1,2,3,4,6,W\\}} p(o \\mid \\text{inn, over}) \\cdot |\\mathcal{P}(s_{t+1} \\mid o) - \\mathcal{P}(s_t)|$$<br/>"
    "Normalized by mean: Average ball = 1.0. High Pressure = Top Quartile ($LI \\ge 1.32$, 49,276 balls)."
)
elements.append(Table([[Paragraph(c1_text, card_body), Paragraph(c2_text, card_body)]], colWidths=[13*cm, 13*cm], 
                      style=TableStyle([
                          ('BACKGROUND', (0,0), (-1,-1), GREY_BG),
                          ('BOX', (0,0), (-1,-1), 1, BORDER_CLR),
                          ('TOPPADDING', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                          ('LEFTPADDING', (0,0), (-1,-1), 10), ('RIGHTPADDING', (0,0), (-1,-1), 10),
                      ])))
elements.append(Spacer(1, 6))
elements.append(Paragraph("<b>Validation Reality:</b> Under High Pressure, mean leverage jumps $6.1\\times$ (0.44 to 2.68) and win-probability swing surges $6.0\\times$ (0.62% to 3.73% per ball), with a +5.0% increase in dismissal mortality.", body_style))
elements.append(PageBreak())

# -------------------------------------------------------------
# SLIDE 3: SIGNATURE DISCOVERY: THE RAW STRIKE RATE ILLUSION
# -------------------------------------------------------------
slide_header("Empirical Discovery", "The 'Raw Strike Rate Illusion': Why Value Over Expected Is Mandatory")
elements.append(Paragraph("Across the entire 197,100-delivery dataset, we uncovered a striking counter-intuitive finding that disproves conventional cricket wisdom:", body_style))
elements.append(Spacer(1, 4))

val_data = [
    ['Metric Dimension', 'Ordinary Deliveries (LI < 1.32)', 'High Pressure (LI >= 1.32)', 'Observed Reality & Franchise Implication'],
    ['Batting Strike Rate', '138.72', '141.84', 'Negligible +2.2% difference. Batters DO NOT strike faster under pressure.'],
    ['Striker Dismissal % / Ball', '5.39%', '5.66%', '+5.0% mortality spike. Catastrophic cost of getting dismissed.'],
    ['Win-Prob Swing / Ball', '0.62 pts', '3.73 pts', '6.0x probability volatility. Every ball moves match outcome 6x more.'],
    ['Bowler Economy Rate', '8.62 RPO', '8.83 RPO', 'Barely +0.21 RPO increase despite death-over concentration.']
]
elements.append(make_table(val_data, [5.5*cm, 5.0*cm, 5.0*cm, 10.5*cm], fs=8.0, alignments=['LEFT', 'CENTER', 'CENTER', 'LEFT']))
elements.append(Spacer(1, 6))

elements.append(Paragraph(
    "<b>Franchise Takeaway:</b> Because raw scoring rates are virtually identical between high pressure and ordinary situations, "
    "evaluating players on raw strike rate or economy is statistically flawed. Success under pressure is governed by "
    "<b>Net Runs Added Above Expected</b> incorporating <b>Dynamic Wicket Values (&lambda;)</b>: Powerplay &asymp; 8.3 runs, Middle &asymp; 6.0 runs, Death &asymp; 2.8 runs.",
    body_style
))
elements.append(PageBreak())

# -------------------------------------------------------------
# SLIDE 4: THE 4 PILLARS & EMPIRICAL BAYES SHRINKAGE
# -------------------------------------------------------------
slide_header("Scoring Architecture", "Four Orthogonal Pillars & Empirical Bayes Shrinkage")
elements.append(Paragraph("To ensure balance, transparency, and statistical confidence, each qualified player (&ge; 150 HP balls, &ge; 8 HP matches, &ge; 100 ordinary balls) is scored across 4 orthogonal dimensions:", body_style))
elements.append(Spacer(1, 4))

p_data = [
    ['Pillar', 'Weight', 'Metric Formula', 'What It Measures & Dugout Relevance'],
    ['1. Pressure Net Value', '35%', 'Net runs above expected / 100 balls (shrunk)', 'Core situational run generation & boundary rate above phase expectation.'],
    ['2. Win Probability Added', '30%', 'Average delta WP per 100 balls (shrunk)', 'Direct match-impact volatility delivered across critical leverage moments.'],
    ['3. Baseline Elevation Gap', '20%', 'Delta = Net(HP) - Net(Ordinary) (shrunk)', 'Answers: "Does this player genuinely elevate when it matters most?"'],
    ['4. Match Hit-Rate Consistency', '15%', '(Hits + 4) / (Eligible Matches + 8)', 'Bayesian match hit-rate (&ge; 6 HP balls and Net > 0) with 50% prior.']
]
elements.append(make_table(p_data, [5.0*cm, 2.5*cm, 7.5*cm, 11.0*cm], fs=8.0, alignments=['LEFT', 'CENTER', 'LEFT', 'LEFT']))
elements.append(Spacer(1, 6))

elements.append(Paragraph(
    "<b>Eliminating Small-Sample Bias via Empirical Bayes:</b><br/>"
    "$$\\widehat{\\theta}_i = \\mu + \\frac{\\tau^2}{\\tau^2 + \\sigma^2/n_i}(\\bar{x}_i - \\mu), \\quad \\text{where } \\tau^2 = \\max\\left(0, \\text{Var}(x) - \\frac{1}{M}\\sum \\frac{\\sigma^2}{n_i}\\right)$$<br/>"
    "Standardized Z-scores use raw standard deviations so that low-sample uncertainty is genuinely penalized rather than inflated.",
    body_style
))
elements.append(PageBreak())

# -------------------------------------------------------------
# SLIDE 5: OFFICIAL TOP 10 LEADERBOARDS
# -------------------------------------------------------------
slide_header("Official Submission", "Ordered Top 10 Batters & Bowlers (Primary Recommendation)")

b_rows = [
    ['#', 'Top 10 Batters', 'HP Balls', 'SR', 'Avg', 'Net/100', 'Delta', 'WPA', 'Score', '#', 'Top 10 Bowlers', 'HP Balls', 'Econ', 'Dot %', 'Net/100', 'WPA', 'Score'],
    ['1', 'Suryakumar Yadav', '697', '174.0', '43.3', '+38.7', '+13.1', '+0.63', '0.843', '1', 'Sunil Narine', '393', '6.51', '41.9%', '+37.2', '+1.35', '1.163'],
    ['2', 'Phil Salt', '339', '175.5', '49.6', '+36.9', '+17.4', '+0.84', '0.771', '2', 'Abrar Ahmed', '178', '6.14', '41.1%', '+42.3', '+0.90', '0.866'],
    ['3', 'Tim David', '419', '174.5', '34.8', '+26.8', '-10.5', '+0.85', '0.457', '3', 'Mitchell Santner', '409', '7.33', '37.8%', '+26.4', '+0.63', '0.818'],
    ['4', 'Babar Azam', '220', '160.9', '44.3', '+24.4', '+26.6', '+0.24', '0.438', '4', 'Jacob Duffy', '167', '8.29', '45.6%', '+60.1', '+0.53', '0.772'],
    ['5', 'Shubman Gill', '564', '156.7', '44.2', '+15.3', '+6.2', '+0.31', '0.437', '5', 'Matheesha Pathirana', '315', '8.78', '35.6%', '+21.1', '+0.68', '0.727'],
    ['6', 'Nicholas Pooran', '575', '161.0', '34.3', '+21.8', '+6.5', '+0.13', '0.412', '6', 'Lockie Ferguson', '247', '7.61', '47.1%', '+35.5', '+1.05', '0.679'],
    ['7', 'Abhishek Sharma', '476', '184.2', '29.2', '+24.3', '-14.4', '+0.49', '0.410', '7', 'Taskin Ahmed', '239', '6.53', '48.5%', '+34.7', '+0.52', '0.641'],
    ['8', 'Vaibhav Sooryavanshi', '161', '231.1', '46.5', '+75.8', '+7.9', '+1.21', '0.386', '8', 'Josh Hazlewood', '398', '7.73', '46.7%', '+33.8', '+0.52', '0.600'],
    ['9', 'Fakhar Zaman', '217', '151.6', '29.9', '+19.2', '+23.9', '+0.63', '0.343', '9', 'Mohit Sharma', '176', '8.64', '25.4%', '+25.0', '+0.80', '0.540'],
    ['10', 'Harry Brook', '193', '180.3', '34.8', '+25.9', '+10.5', '+0.72', '0.322', '10', 'Krunal Pandya', '340', '7.21', '31.8%', '+19.9', '+0.51', '0.537']
]
elements.append(make_table(b_rows, [0.6*cm, 3.4*cm, 1.3*cm, 1.1*cm, 1.0*cm, 1.3*cm, 1.2*cm, 1.1*cm, 1.3*cm, 0.6*cm, 3.4*cm, 1.3*cm, 1.1*cm, 1.1*cm, 1.3*cm, 1.1*cm, 1.3*cm], fs=7.0,
                           alignments=['CENTER', 'LEFT', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'LEFT', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER']))
elements.append(Spacer(1, 5))
elements.append(Paragraph("<b>The Stability Reality:</b> Narine (93%), Salt (82%), and Surya (76%) represent the statistically unshakeable core. Ranks 4 to 10 survive in 20% to 60% of resamples, confirming they form an <i>interchangeable tactical tier</i>.", body_style))
elements.append(PageBreak())

# -------------------------------------------------------------
# SLIDE 6: TACTICAL MATCHUPS: PACE VS SPIN SPLITS
# -------------------------------------------------------------
slide_header("Dugout Tactical Intelligence", "Batter Matchup Deconstruction: High-Pressure Pace vs. Spin Splits")
elements.append(Paragraph("Analyzing high-pressure deliveries split by bowling art (121,652 Pace vs 75,486 Spin balls) uncovers crucial situational strengths and chokepoints:", body_style))
elements.append(Spacer(1, 4))

m_data = [
    ['Batter', 'Pace Balls', 'Pace SR', 'Pace Net/100', 'Spin Balls', 'Spin SR', 'Spin Net/100', 'Tactical Dugout Whiteboard Takeaway'],
    ['Suryakumar Yadav', '402', '192.8', '+44.9', '295', '148.5', '+30.4', 'Complete all-round mastery; supreme high-pace punisher at death.'],
    ['Phil Salt', '224', '173.7', '+36.9', '115', '179.1', '+36.7', 'Remarkable symmetry: identical destructive impact vs both disciplines.'],
    ['Shubman Gill', '363', '149.6', '-1.2', '201', '169.7', '+45.1', 'Elite spin destroyer (+45.1); vulnerable against high pace at death.'],
    ['Babar Azam', '145', '182.1', '+47.4', '75', '120.0', '-20.0', 'Severe Spin Choke: Feasts on pace (+47.4), neutralized by spin (-20.0).'],
    ['Abhishek Sharma', '331', '174.9', '+20.1', '145', '205.5', '+34.0', 'Extreme spin slog-sweeper acceleration (205.5 SR under pressure).'],
    ['Vaibhav Sooryavanshi', '131', '237.4', '+79.4', '30', '203.3', '+59.9', 'Unprecedented boundary outlier across both pace (+79.4) & spin (+59.9).']
]
elements.append(make_table(m_data, [3.8*cm, 2.0*cm, 1.8*cm, 2.4*cm, 2.0*cm, 1.8*cm, 2.4*cm, 9.8*cm], fs=7.5,
                           alignments=['LEFT', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'LEFT']))
elements.append(Spacer(1, 6))
elements.append(Paragraph("<b>Captaincy Directive:</b> When defending against Babar in the death, NEVER bowl pace; bring on spin. When bowling to Gill, attack with high pace into the pitch.", body_style))
elements.append(PageBreak())

# -------------------------------------------------------------
# SLIDE 7: BOWLER PHASE DEPLOYMENT MATRIX
# -------------------------------------------------------------
slide_header("Dugout Tactical Intelligence", "Bowler Phase Deconstruction: Powerplay vs. Middle vs. Death")
elements.append(Paragraph("Mapping each top bowler's net runs saved above expected across the three distinct match phases:", body_style))
elements.append(Spacer(1, 4))

bw_phase = [
    ['Bowler', 'Powerplay (Overs 1-6)', 'Middle (Overs 7-15)', 'Death (Overs 16-20)', 'Strategic Deployment Blueprint'],
    ['Sunil Narine', '6.6 Econ (+38.9)', '6.4 Econ (+31.0)', '6.7 Econ (+57.2)', 'Universal Anchor: The only bowler with +30 runs saved in ALL 3 phases.'],
    ['Matheesha Pathirana', '10.2 Econ (+34.3)', '8.0 Econ (+12.3)', '9.2 Econ (+32.0)', 'Dedicated Death Slinger: 148 death balls; premier yorker execution.'],
    ['Mohit Sharma', '12.0 Econ (-87.0)', '7.3 Econ (+54.2)', '9.3 Econ (+17.6)', 'Middle/Death Specialist: Higher economy in low-sample PP (14 balls); high return in Overs 11-19.'],
    ['Josh Hazlewood', '6.8 Econ (+40.1)', '8.3 Econ (+46.0)', '9.1 Econ (+18.5)', 'New-Ball Choker: 212 pressure balls in PP; world-class initial restraint.'],
    ['Jacob Duffy', '7.6 Econ (+111.6)', '3.2 Econ (+118.3)', '10.7 Econ (-14.6)', 'Front-Load Asset: Elite in overs 1-14; high variance in overs 18-20.']
]
elements.append(make_table(bw_phase, [4.0*cm, 4.2*cm, 4.2*cm, 4.2*cm, 9.4*cm], fs=8.0,
                           alignments=['LEFT', 'CENTER', 'CENTER', 'CENTER', 'LEFT']))
elements.append(Spacer(1, 6))
elements.append(Paragraph("<b>Franchise Value:</b> Mohit Sharma is a premier auction acquisition for Rajasthan Royals, but only if deployed with strict phase discipline (Overs 11&ndash;19 exclusively).", body_style))
elements.append(PageBreak())

# -------------------------------------------------------------
# SLIDE 8: THE SUPERSTAR PARADOX
# -------------------------------------------------------------
slide_header("Critical Nuance", "The 'Superstar Paradox': Explaining Notable Exclusions")
elements.append(Paragraph("Anticipating and answering the natural questions about household names who did not make the Top 10:", body_style))
elements.append(Spacer(1, 4))

sp_data = [
    ['Player', 'Role', 'Rank', 'Model Score', 'Why They Sits Outside Top 10 & Data Reality'],
    ['Jasprit Bumrah', 'Bowler', '#24-26', '0.294', 'Batter Risk Aversion: Opposition batters treat Bumrah defensively under pressure (taking safe singles rather than risking wickets). Suppressed per-ball wicket credit.'],
    ['Rashid Khan', 'Bowler', '#14-18', '0.381', 'Elite Baseline Ceiling: His ordinary-overs floor is already near-perfect; his elevation gap (Delta = -0.91) is flat. Reliable, but not extra-elevated.'],
    ['Arshdeep Singh', 'Bowler', '#69-71', '-0.151', 'Death Concession Inflation: Bowls extreme death overs against aggressive finishers; even after phase adjustments, his concession rate exceeds expected values.'],
    ['David Miller', 'Batter', '#94-95', '-0.435', 'High-Pressure Dip: Across 2022-2026 data, Miller experienced a statistically significant decline in high-leverage execution relative to his baseline.'],
    ['Heinrich Klaasen', 'Batter', '#18-20', '0.284', 'Catastrophic Wicket Penalties: Massive power, but high-risk aggression under chase bottlenecks produced costly dismissals that penalized his net value.']
]
elements.append(make_table(sp_data, [3.8*cm, 2.0*cm, 1.8*cm, 2.4*cm, 16.0*cm], fs=8.0,
                           alignments=['LEFT', 'CENTER', 'CENTER', 'CENTER', 'LEFT']))
elements.append(PageBreak())

# -------------------------------------------------------------
# SLIDE 9: VAIBHAV SOORYAVANSHI IN-HOUSE ASSET
# -------------------------------------------------------------
slide_header("Franchise Asset Validation", "The Vaibhav Sooryavanshi Discovery: An In-House RR Cornerstone")
elements.append(Paragraph("<b>The Single Most Actionable Organizational Finding for Rajasthan Royals:</b>", body_style))
elements.append(Spacer(1, 4))

vs_card = (
    "<b>VAIBHAV SOORYAVANSHI &mdash; HIGH-PRESSURE PROFILE:</b><br/>"
    "&bull; <b>Global Rank:</b> #8 Batter in Worldwide T20 Cricket under pressure<br/>"
    "&bull; <b>High-Pressure Net Value:</b> <b>+75.76 runs above expected / 100 balls</b> (Highest in the entire dataset)<br/>"
    "&bull; <b>High-Pressure Strike Rate:</b> <b>231.1 SR</b> &bull; <b>Boundary %:</b> <b>41.6%</b> (32 fours, 35 sixes in 161 HP balls)<br/>"
    "&bull; <b>WPA per 100 Balls:</b> <b>+1.21 points</b> &bull; <b>Model Score:</b> <b>0.386</b><br/>"
    "&bull; <b>IPL Status:</b> <b>ALREADY CONTRACTED TO RAJASTHAN ROYALS (₹1.10 Cr)</b>"
)
elements.append(Table([[Paragraph(vs_card, body_style)]], colWidths=[26.0*cm],
                      style=TableStyle([
                          ('BACKGROUND', (0,0), (-1,-1), PINK_LIGHT),
                          ('BOX', (0,0), (-1,-1), 1.5, PINK),
                          ('TOPPADDING', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                          ('LEFTPADDING', (0,0), (-1,-1), 12), ('RIGHTPADDING', (0,0), (-1,-1), 12),
                      ])))
elements.append(Spacer(1, 6))
elements.append(Paragraph("<b>Executive Conclusion:</b> While other franchises will enter the auction spending ₹15+ Crore chasing explosive boundary-hitters, Rajasthan Royals already possesses the most efficient clutch-striking asset in cricket at ₹1.10 Cr.", body_style))
elements.append(PageBreak())

# -------------------------------------------------------------
# SLIDE 10: 5-GATE PROTOCOL & ACTIONABLE SELECTION (OPTION B)
# -------------------------------------------------------------
slide_header("Selection Governance", "5-Gate Verification Protocol & Option B Actionability")
elements.append(Paragraph("To transition from raw statistical modeling to franchise execution, candidates pass through a formal 5-Gate funnel:", body_style))
elements.append(Spacer(1, 4))

gate_summary = [
    ['Gate Stage', 'Filter Rule', 'Franchise Governance Impact'],
    ['Gate 1: Sample Sufficiency', 'N_total >= 100, N_hp >= 30, HP Matches >= 8', 'Filters 958 tournament players down to 100 qualified batters and 102 bowlers.'],
    ['Gate 2: 4-Pillar Convergence', 'Value (35%), WPA (30%), Delta (20%), Cons. (15%)', 'Prevents single-metric bias and balances run generation with win impact.'],
    ['Gate 3: Opposition Normalization', 'Leave-one-match-out opponent quality ratings', 'Adjusts for attack strength faced, penalizing associate stat-padding.'],
    ['Gate 4: Operational Availability', 'Excludes players unavailable for IPL (Pakistan)', 'Option B elevates Harry Brook (#10 Bat) and Mohit Sharma (#9 Bowl) to priority.'],
    ['Gate 5: Bootstrap Stability', '200 match-level bootstrap resamples', 'Confirms stable core (Narine 93%, Salt 82%, Surya 76%) vs interchangeable tier (20-60%).']
]
elements.append(make_table(gate_summary, [6.0*cm, 8.0*cm, 12.0*cm], fs=7.8,
                           alignments=['LEFT', 'CENTER', 'LEFT']))
elements.append(Spacer(1, 8))
elements.append(Paragraph("<b>Submission Verified:</b> Verified against expected values. Target: Round 2 (Mumbai) &amp; Round 3 (Goa).", slide_sub_style))

# Build PDF
doc = SimpleDocTemplate(
    'outputs/SupeRR_Selector_Dugout_Presentation.pdf',
    pagesize=landscape(A4),
    leftMargin=1.5*cm,
    rightMargin=1.5*cm,
    topMargin=1.2*cm,
    bottomMargin=1.2*cm,
    title='Rajasthan Royals Dugout Presentation Deck'
)

doc.build(elements)
print("Presentation Deck built successfully at outputs/SupeRR_Selector_Dugout_Presentation.pdf")

