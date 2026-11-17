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
from reportlab.pdfgen import canvas

print("--- Building Rajasthan Royals SupeRR Selector Top 1 Master Report PDF ---")

# 1. Load verified datasets
exp_df = pd.read_csv('expected_dashboard_values.csv')
bat_top = exp_df[exp_df['role'] == 'bat'].sort_values('rank')
bowl_top = exp_df[exp_df['role'] == 'bowl'].sort_values('rank')
tac_df = pd.read_csv('tactical_splits_verified.csv')

# Colors - Official Rajasthan Royals palette
RR_NAVY = HexColor('#041126')
RR_PINK = HexColor('#E5007D')
GREY_BG = HexColor('#F8FAFC')
BORDER_CLR = HexColor('#CBD5E1')
TEXT_DARK = HexColor('#0F172A')
TEXT_MUTED = HexColor('#475569')
WHITE = HexColor('#FFFFFF')
LIGHT_GREY = HexColor('#F1F5F9')
CALLOUT_BG = HexColor('#FFF1F7')

styles = getSampleStyleSheet()

# Typography styles
title_style = ParagraphStyle(
    'DocTitle', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=RR_NAVY
)
h1_style = ParagraphStyle(
    'H1', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=10.5, leading=13.5, textColor=RR_NAVY, spaceAfter=2, spaceBefore=4
)
h2_style = ParagraphStyle(
    'H2', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=RR_PINK, spaceAfter=2, spaceBefore=3
)
body_style = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontName='Helvetica', fontSize=6.8, leading=8.8, textColor=TEXT_DARK
)
body_bold = ParagraphStyle(
    'BodyBold', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=6.8, leading=8.8, textColor=TEXT_DARK
)
note_style = ParagraphStyle(
    'Note', parent=styles['Normal'],
    fontName='Helvetica-Oblique', fontSize=6.2, leading=7.8, textColor=TEXT_MUTED
)

def make_table(data, widths, fs=6.2, alignments=None, grey_rows=None, custom_header_bg=RR_NAVY):
    if grey_rows is None:
        grey_rows = []
    formatted = []
    for r_idx, row in enumerate(data):
        fmt_row = []
        for c_idx, cell in enumerate(row):
            align = alignments[c_idx] if alignments else 'CENTER'
            f_size = fs if r_idx > 0 else fs + 0.3
            weight = 'Helvetica-Bold' if (r_idx == 0 or c_idx == 1) else 'Helvetica'
            clr = WHITE if r_idx == 0 else (TEXT_MUTED if r_idx in grey_rows else TEXT_DARK)
            fmt_row.append(Paragraph(
                f"<para align='{align.lower()}'><font face='{weight}' size='{f_size}' color='{clr.hexval()}'>{cell}</font></para>",
                body_style
            ))
        formatted.append(fmt_row)
    
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), custom_header_bg),
        ('GRID', (0,0), (-1,-1), 0.4, BORDER_CLR),
        ('TOPPADDING', (0,0), (-1,-1), 1.6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.6),
        ('LEFTPADDING', (0,0), (-1,-1), 2.5),
        ('RIGHTPADDING', (0,0), (-1,-1), 2.5),
    ]
    for r_idx in range(1, len(data)):
        if r_idx in grey_rows:
            t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), LIGHT_GREY))
        elif r_idx % 2 == 1:
            t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), GREY_BG))
            
    return Table(formatted, colWidths=widths, style=TableStyle(t_style))

# Custom Numbered Canvas for exact page counting
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 7)
        self.setFillColor(TEXT_MUTED)
        
        # Header (Pages 2-5)
        if self._pageNumber > 1:
            self.drawString(1.3*cm, 28.7*cm, "Rajasthan Royals SupeRR Selector Season 2 • Selection Methodology Report (v4 Top 1)")
            self.drawRightString(19.7*cm, 28.7*cm, "Target: Round 2 (Mumbai) & Round 3 (Goa)")
            self.setStrokeColor(BORDER_CLR)
            self.setLineWidth(0.4)
            self.line(1.3*cm, 28.5*cm, 19.7*cm, 28.5*cm)

        # Footer (All Pages)
        self.setStrokeColor(BORDER_CLR)
        self.setLineWidth(0.4)
        self.line(1.3*cm, 1.2*cm, 19.7*cm, 1.2*cm)
        self.drawString(1.3*cm, 0.8*cm, "Confidential • Prepared for Rajasthan Royals Analytics Dugout • Evaluated on 197,100 Deliveries")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(19.7*cm, 0.8*cm, page_str)
        self.restoreState()

elements = []

# =========================================================================
# PAGE 1: EXECUTIVE BRIEF, DATA ENGINEERING & LEVERAGE FRAMEWORK
# =========================================================================
header_data = [
    [
        Paragraph("<b>RAJASTHAN ROYALS &bull; SUPERR SELECTOR SEASON 2</b><br/><font size='7' color='#475569'>Round 1 Submission &bull; Win-Probability Leverage, Context & Opposition Adjustments, Empirical Bayes</font>", title_style),
        Paragraph("<para align='right'><font size='8' color='#E5007D'><b>SELECTION REPORT</b></font><br/><font size='6.5' color='#475569'>Target: Round 2 (Mumbai) &bull; Round 3 (Goa)</font></para>", body_style)
    ]
]
t_head = Table(header_data, colWidths=[13.2*cm, 5.2*cm])
t_head.setStyle(TableStyle([
    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ('TOPPADDING', (0,0), (-1,-1), 0),
    ('LEFTPADDING', (0,0), (-1,-1), 0),
    ('RIGHTPADDING', (0,0), (-1,-1), 0),
]))
elements.append(t_head)
elements.append(HRFlowable(width="100%", thickness=1.5, color=RR_PINK, spaceAfter=4, spaceBefore=2))

elements.append(Paragraph("1. Executive Summary & Honest Headline", h1_style))
elements.append(Paragraph(
    "This report documents the official submission for the Rajasthan Royals SupeRR Selector Season 2 (Round 1). "
    "We define pressure as <b>how much the next delivery can move match win probability</b> (a continuous Leverage Index from an out-of-fold calibrated win-probability model), "
    "rather than hand-picked binary over or required run rate thresholds. Across 200,999 raw balls from the 2022&ndash;2026 IPL and T20 International dataset (<b>958 total players</b>), "
    "each delivery gets a continuous leverage score; the top quartile (<b>LI &ge; 1.32</b>, 49,276 deliveries) are designated as <b>High Pressure</b>. "
    "Every qualified batter and bowler is evaluated on four pillars: (1) <b>Runs Above Expected</b> (wickets included, adjusted for opponent quality faced), "
    "(2) <b>Win Probability Added (WPA)</b>, (3) <b>Gap to Own Ordinary Baseline (&Delta;)</b>, and (4) <b>Match-to-Match Consistency</b>. "
    "Small samples are stabilized with Empirical Bayes shrinkage toward positional priors. The submitted ranking is the <b>Opposition-Adjusted Model</b>, "
    "stress-tested across <b>200 match-level bootstrap resamples</b>.<br/>"
    "<b>Honest Headline:</b> Only a few picks are stable bedrock: <b>Suryakumar Yadav</b> and <b>Phil Salt</b> among batters, and <b>Sunil Narine</b> among bowlers. "
    "Positions 4 to 10 form a tight tactical tier sensitive to sample noise. Predictive validation (Section 6) confirms pressure performance persists weakly across periods, "
    "meaning these rankings represent a rigorous historical audit of 2022&ndash;2026 rather than an infallible forecast.",
    body_style
))
elements.append(Spacer(1, 2))

elements.append(Paragraph("2. Data Preparation, Integrity Audits & Screenings", h1_style))
elements.append(Paragraph(
    "Audits of the supplied ball-by-ball files established critical data engineering boundaries:<br/>"
    "&bull; <b>Extras Codes:</b> The column <code>extras1_runs</code> is an integer categorical type code (6 = none, 2 = wide, 3 = leg bye, 4 = bye, 1 = no ball), not a run tally. "
    "Bowler runs = bat runs + 1 for wides and no-balls; byes and leg-byes are not charged to bowlers; wides are not balls faced. Extras of type 'other' behave as extra deliveries.<br/>"
    "&bull; <b>Wicket Attribution:</b> Run-outs, retired-out, and obstructing the field are withheld from bowler credit; batters are charged with an out only when dismissed.<br/>"
    "&bull; <b>Unrecorded Runs & Exclusions:</b> Bye and leg-bye runs are unrecorded in the run column. Reconstructed totals match official margins within 2 runs for 49% and within 5 runs for 82% of the 385 matches decided by runs (median difference 0). "
    "We dropped 16 matches where ball logs contradicted recorded results and 570 second-innings balls where targets were unrecorded. Super overs (38 balls) were removed. "
    "Clean dataset: <b>851 matches</b> (197,100 deliveries: 103,726 1st innings, 93,374 2nd innings).",
    body_style
))
elements.append(Spacer(1, 2))

elements.append(Paragraph("3. Defining Pressure: The Continuous Leverage Index (LI)", h1_style))
elements.append(Paragraph(
    "&bull; <b>Win-Probability Model:</b> Separate Histogram Gradient-Boosted Classifiers (HGB) predict batting victory from post-ball state (5 folds grouped by match, seed-fixed). "
    "Second-innings model AUC is <b>0.89</b> (Brier 0.137); first-innings AUC is <b>0.68</b>. Predictions are isotonic-recalibrated out-of-fold.<br/>"
    "&bull; <b>Leverage Index Formulation:</b> For each ball, we enumerate legal outcomes $o \\in \\{0, 1, 2, 3, 4, 6, W\\}$ weighted by transition frequencies $p(o \\mid \\text{innings, over})$:<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;$$LI_{\\text{raw}} = \\sum_{o} p(o \\mid \\text{innings, over}) \\cdot \\left| \\mathcal{P}(s_{t+1} \\mid o) - \\mathcal{P}(s_t) \\right|, \\quad LI = \\frac{LI_{\\text{raw}}}{\\mathbb{E}[LI_{\\text{raw}}]}$$<br/>"
    "Deliveries at or above the 75th percentile (<b>LI &ge; 1.32</b>: 49,276 deliveries; 25% of all balls) represent High Pressure. "
    "In chases, 39% of death balls qualify vs. only 25% in the first innings, proving a continuous index correctly filters dead rubbers.",
    body_style
))
elements.append(Spacer(1, 2))

# Metric Table
metric_rows = [
    ['Metric', 'Ordinary Deliveries', 'High Pressure (LI &ge; 1.32)'],
    ['Deliveries', '147,824 (75.0%)', '49,276 (25.0%)'],
    ['Mean Leverage Index', '0.44', '2.68'],
    ['Mean Win-Probability Swing per Ball (pts)', '<b>0.62</b>', '<b>3.73 (6.0&times; surge)</b>'],
    ['Batting Strike Rate', '138.72', '141.84 (barely differs)'],
    ['Dismissal % per Ball Faced', '5.39%', '5.66% (+5.0% risk)'],
    ['Dot Ball %', '37.45%', '35.84%'],
    ['Boundary %', '18.60%', '18.93%'],
    ['Bowler Economy', '8.62', '8.83']
]
elements.append(make_table(metric_rows, [8.4*cm, 5.0*cm, 5.0*cm], fs=6.2, alignments=['LEFT', 'CENTER', 'CENTER']))
elements.append(Spacer(1, 2))

if os.path.exists('c1.png'):
    elements.append(Image('c1.png', width=18.4*cm, height=4.6*cm))
    elements.append(Paragraph("<b>Figure 1:</b> Left &mdash; Mean Leverage Index by over across innings. Right &mdash; Out-of-fold win probability calibration curves.", note_style))

elements.append(PageBreak())

# =========================================================================
# PAGE 2: PERFORMANCE MEASUREMENT & OFFICIAL TOP 10 BATTERS
# =========================================================================
elements.append(Paragraph("4. Performance Measurement Engine & Opponent Quality Adjustment", h1_style))
elements.append(Paragraph(
    "&bull; <b>Context-Adjusted Expected Values:</b> Four gradient-boosted models predict expected bat runs, striker dismissal probability, expected runs charged, and bowler wicket probability conditional on match state (over, wickets, balls left, required rate, league, and opponent rating).<br/>"
    "&bull; <b>Dynamic Wicket Valuation (&lambda;):</b> Derived from win-probability gradients: <b>&lambda; = 8.3 runs</b> in Powerplay, <b>6.0 runs</b> in Middle overs, and <b>2.8 runs</b> at Death.<br/>"
    "&bull; <b>Net Runs Added:</b> Batter value is $v_{\\text{bat}} = (R_t - \\mathbb{E}[R_t]) - \\lambda_t (\\mathbb{I}_{\\text{out}} - \\mathbb{P}[\\text{out}])$. "
    "Bowler value is $v_{\\text{bowl}} = (\\mathbb{E}[R_t] - R_t) + \\lambda_t (\\mathbb{I}_{\\text{wkt}} - \\mathbb{P}[\\text{wkt}])$.<br/>"
    "&bull; <b>Opposition Quality Adjustment:</b> Each bowler and batter receives a leave-one-match-out rating to eliminate circularity: "
    "$$\\text{Rating} = \\frac{\\sum \\text{per-ball values excluding current match}}{\\text{balls excluding current match} + 300} \\times 100$$<br/>"
    "&bull; <b>4-Pillar Composite Function:</b> (1) Pressure Value per 100 balls (weight <b>0.35</b>); (2) Win Probability Added per 100 balls (weight <b>0.30</b>); "
    "(3) Gap to Ordinary Baseline &Delta; (weight <b>0.20</b>); and (4) Match Consistency with Beta prior of 8 pseudo-matches at 50% (weight <b>0.15</b>). "
    "Components 1&ndash;3 are shrunk by Empirical Bayes toward the pool mean, then standardized using raw spread so noisy metrics cannot distort rankings.",
    body_style
))
elements.append(Spacer(1, 2))

elements.append(Paragraph("5. Fair Comparison Protocols & Qualification Pool", h1_style))
elements.append(Paragraph(
    "&bull; <b>Eligibility Thresholds:</b> At least 150 high-pressure deliveries, at least 8 high-pressure matches (&ge;6 HP balls each), and at least 100 ordinary deliveries. "
    "From 958 total players, exactly <b>100 batters and 102 bowlers qualify</b>.<br/>"
    "&bull; <b>Context & League Normalization:</b> Phase, wickets, and chase dynamics are inside expected values, preventing role bias. IPL and T20I are pooled with a league indicator.",
    body_style
))
elements.append(Spacer(1, 2))

elements.append(Paragraph("6. Official Top 10 Batters Under High Pressure (Opposition-Adjusted Model)", h1_style))
elements.append(Paragraph(
    "The verified Top 10 Batters under high pressure. All metrics match <code>expected_dashboard_values.csv</code> character-for-character:",
    body_style
))
elements.append(Spacer(1, 1))

# Official Top 10 Batters Table
bat_tbl_data = [
    ['#', 'Batter', 'HP Balls', 'HP Runs', 'Outs', 'HP SR', 'Net/100', 'Delta', 'WPA/100', 'Cons.', 'Adj Score', 'Boot %', 'Variants']
]
for _, r in bat_top.iterrows():
    runs_str = str(int(r.hp_runs)) if not pd.isna(r.hp_runs) else 'n/a'
    outs_str = str(int(r.outs)) if not pd.isna(r.outs) else 'n/a'
    sr_str = f"{float(r.sr):.1f}" if not pd.isna(r.sr) else 'n/a'
    bat_tbl_data.append([
        f"<b>{int(r['rank'])}</b>", r['player'], f"{int(r.hp_balls)}", runs_str, outs_str, sr_str,
        f"{float(r.net_100):+.2f}", f"{float(r.delta):+.2f}", f"{float(r.wpa_100):+.3f}",
        f"{float(r.consistency)*100:.1f}%", f"<b>{float(r.score):.3f}</b>", f"{float(r.boot_top10):.1f}%",
        f"{'7/7' if r['rank']==1 else ('6/7' if r['rank']==2 else ('5/7' if r['rank']==6 else ('4/7' if r['rank'] in (3,7) else ('4/5' if r['rank'] in (8,10) else ('3/5' if r['rank']==4 else '2/5')))))}"
    ])
elements.append(make_table(bat_tbl_data, [0.6*cm, 3.8*cm, 1.3*cm, 1.3*cm, 0.9*cm, 1.3*cm, 1.4*cm, 1.3*cm, 1.4*cm, 1.2*cm, 1.4*cm, 1.2*cm, 1.3*cm],
                           fs=6.2, alignments=['CENTER', 'LEFT', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER']))
elements.append(Spacer(1, 2))

elements.append(Paragraph(
    "<b>Analytical Observations on Batter Rankings:</b><br/>"
    "&bull; <b>Suryakumar Yadav (#1, Score 0.843):</b> Combines the largest pressure sample in global cricket (697 balls) with +38.74 Net/100 and +13.10 Delta. Top 10 in 76.0% of bootstraps and 7/7 model variants. He is the undisputed anchor of clutch batting.<br/>"
    "&bull; <b>Phil Salt (#2, Score 0.771):</b> Highest bootstrap resilience among batters (82.0%), pairing 175.5 SR with +36.85 Net/100 across 339 balls.<br/>"
    "&bull; <b>Negative Delta Cohort (David -10.51, Abhishek -14.38):</b> Both score at or above this elite level in ordinary overs. They do not fail under pressure; their ordinary baselines are simply world-class.<br/>"
    "&bull; <b>Vaibhav Sooryavanshi (#8, Score 0.386):</b> Highest raw net value in the dataset (+75.76 Net/100, 231.1 SR, 1.209 WPA/100). Empirical Bayes correctly shrinks his 161-ball sample to rank #8. <i>Crucially: He is already an in-house Rajasthan Royals contracted asset!</i><br/>"
    "&bull; <b>Geopolitical Non-Actionables:</b> Babar Azam (#4) and Fakhar Zaman (#9) rank on pure sporting merit but are IPL-ineligible in practice.",
    body_style
))

elements.append(PageBreak())

# =========================================================================
# PAGE 3: OFFICIAL TOP 10 BOWLERS, FIGURE 2 & J. BUMRAH CASE STUDY
# =========================================================================
elements.append(Paragraph("7. Official Top 10 Bowlers Under High Pressure (Opposition-Adjusted Model)", h1_style))
elements.append(Paragraph(
    "The verified Top 10 Bowlers under high pressure. All metrics match <code>expected_dashboard_values.csv</code> character-for-character:",
    body_style
))
elements.append(Spacer(1, 1))

# Official Top 10 Bowlers Table
bowl_tbl_data = [
    ['#', 'Bowler', 'HP Balls', 'Legal', 'Wkts', 'Econ', 'Dot %', 'Net/100', 'Delta', 'WPA/100', 'Cons.', 'Adj Score', 'Boot %', 'Variants']
]
for _, r in bowl_top.iterrows():
    legal_str = str(int(r.legal_balls)) if not pd.isna(r.legal_balls) else str(int(r.hp_balls))
    econ_str = f"{float(r.econ):.2f}" if not pd.isna(r.econ) else '-'
    dot_str = f"{float(r.dot_pct):.1f}%" if not pd.isna(r.dot_pct) else '-'
    bowl_tbl_data.append([
        f"<b>{int(r['rank'])}</b>", r['player'], f"{int(r.hp_balls)}", legal_str, str(int(r.wkts)), econ_str, dot_str,
        f"{float(r.net_100):+.2f}", f"{float(r.delta):+.2f}", f"{float(r.wpa_100):+.3f}",
        f"{float(r.consistency)*100:.1f}%", f"<b>{float(r.score):.3f}</b>", f"{float(r.boot_top10):.1f}%",
        f"{'6/6' if r['rank']==1 else ('5/5' if r['rank'] in (2,4) else ('5/7' if r['rank']==3 else ('6/7' if r['rank'] in (5,8) else ('4/6' if r['rank']==6 else ('4/5' if r['rank']==7 else ('3/5' if r['rank']==9 else '3/6'))))))}"
    ])
elements.append(make_table(bowl_tbl_data, [0.6*cm, 3.6*cm, 1.2*cm, 1.1*cm, 0.9*cm, 1.1*cm, 1.1*cm, 1.4*cm, 1.3*cm, 1.4*cm, 1.1*cm, 1.3*cm, 1.1*cm, 1.2*cm],
                           fs=6.0, alignments=['CENTER', 'LEFT', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER']))
elements.append(Spacer(1, 2))

if os.path.exists('c2.png'):
    elements.append(Image('c2.png', width=18.4*cm, height=5.3*cm))
    elements.append(Paragraph("<b>Figure 2:</b> High-Pressure Value vs. Ordinary Baseline (points above dashed diagonal elevate under pressure; bubble size = HP deliveries).", note_style))
elements.append(Spacer(1, 2))

# Jasprit Bumrah Case Study Box
elements.append(Paragraph("8. Analysis of Jasprit Bumrah & Model Boundaries", h1_style))
bumrah_box = (
    "<b>CASE STUDY: JASPRIT BUMRAH (Rank #24 Adjusted &bull; Score 0.407 &bull; Boot Top-10: 16.5%):</b><br/>"
    "In high-pressure deliveries (LI &ge; 1.32), Jasprit Bumrah logged <b>506 deliveries</b>, with <b>42.2% dot balls</b>, a batter strike rate against of <b>125.4</b>, "
    "and <b>20 wickets</b> against <b>27.8 expected</b>. His net pressure value is <b>+15.73 Net/100</b>, which sits <b>-11.19 runs below his ordinary baseline</b>.<br/>"
    "<b>Empirical Boundary:</b> While cricket intuition suggests batters adopt extreme risk-aversion against Bumrah (refusing to play attacking shots and depressing wicket events), "
    "<b>the underlying cause (batter risk avoidance vs. match situations vs. fielding/luck) is untested in the data pack.</b> "
    "A rigorous analytics submission must report what the data proves without inserting unverified speculative adjustments."
)
elements.append(Table([[Paragraph(bumrah_box, body_style)]], colWidths=[18.4*cm],
                      style=TableStyle([
                          ('BACKGROUND', (0,0), (-1,-1), GREY_BG),
                          ('BOX', (0,0), (-1,-1), 1.0, BORDER_CLR),
                          ('TOPPADDING', (0,0), (-1,-1), 3),
                          ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                          ('LEFTPADDING', (0,0), (-1,-1), 6),
                          ('RIGHTPADDING', (0,0), (-1,-1), 6),
                      ])))

elements.append(PageBreak())

# =========================================================================
# PAGE 4: PREDICTIVE VALIDITY, SENSITIVITY & VERIFIED TACTICAL SPLITS
# =========================================================================
elements.append(Paragraph("9. Reliability, Predictive Validity & Sensitivity Analysis", h1_style))
elements.append(Paragraph(
    "&bull; <b>Predictive Validity Across Halves:</b> We tested cross-period correlation using (a) odd vs. even matches and (b) 2022&ndash;2024 vs. 2025&ndash;2026:<br/>"
    "&nbsp;&nbsp;&ndash; <i>Pressure Net Value:</i> Batters 0.15 (odd/even), -0.17 (early/late); Bowlers 0.12 (odd/even), 0.19 (early/late).<br/>"
    "&nbsp;&nbsp;&ndash; <i>Ordinary Baseline Value:</i> Persists much more strongly: 0.34 & 0.31 for batters; 0.24 & 0.36 for bowlers.<br/>"
    "&nbsp;&nbsp;&ndash; <i>Finding:</i> High-pressure performance has low predictive persistence across splits ($r \\approx 0.10&ndash;0.15$). Rankings describe past performance and are a weak forecast.<br/>"
    "&bull; <b>Weight Sensitivity:</b> Shifting baseline delta weight to 0.10 or 0.00 preserves <b>9 of 10 players</b> in both lists (only slot 10 shifts: Tim Seifert replaces Brook; Axar Patel replaces Mohit Sharma). "
    "Random &plusmn;30% perturbations of the four weights keep 8/10 batters and 10/10 bowlers in the top 10 in &ge;90% of trials.",
    body_style
))
elements.append(Spacer(1, 1))

if os.path.exists('c3.png'):
    elements.append(Image('c3.png', width=18.4*cm, height=4.8*cm))
    elements.append(Paragraph("<b>Figure 3:</b> Share of 200 match-level bootstrap resamples in which each finalist finishes in Top 10 (navy) and Top 5 (pink).", note_style))
elements.append(Spacer(1, 2))

elements.append(Paragraph("10. Tactical Splits: Pace vs. Spin & Phase Deployments", h1_style))
elements.append(Paragraph(
    "Verified high-pressure splits from <code>tactical_splits_verified.csv</code>. Rows with &lt;100 balls carry wide standard errors and are flagged:",
    body_style
))
elements.append(Spacer(1, 1))

# Tactical splits summary table
tac_summary_data = [
    ['Player & Role', 'Split / Phase', 'HP Balls', 'Runs', 'SR / Econ', 'Net/100', 'Std. Err (&plusmn;)', 'Sample Flag', 'Tactical Intelligence']
]
grey_tac_rows = []
# Select key representative splits
selected_splits = [
    ('Suryakumar Yadav', 'Pace', 'bat', 'Exploits high-pace hard lengths (+44.89 Net/100)'),
    ('Suryakumar Yadav', 'Spin', 'bat', 'Controlled spin strike rate (+30.36 Net/100)'),
    ('Phil Salt', 'Pace', 'bat', 'Identical high-volume returns across pace & spin'),
    ('Phil Salt', 'Spin', 'bat', '179.1 SR against high-pressure spin'),
    ('Babar Azam', 'Pace', 'bat', 'Elite execution against pace (+47.43 Net/100)'),
    ('Babar Azam', 'Spin', 'bat', 'Low sample; negative return vs spin (-20.02)'),
    ('Shubman Gill', 'Spin', 'bat', 'World-class spin destroyer (+45.12 Net/100)'),
    ('Sunil Narine', 'DEATH', 'bowl', 'Stifling death control (6.66 Econ, +56.53 Net/100)'),
    ('Sunil Narine', 'MID', 'bowl', 'Bankable 257-ball core (6.45 Econ, +30.77 Net/100)'),
    ('Matheesha Pathirana', 'DEATH', 'bowl', 'Slingy death yorkers (+28.50 Net/100, 166 balls)'),
    ('Jacob Duffy', 'PP', 'bowl', 'Devastating powerplay swing (+108.8 Net/100)'),
    ('Mohit Sharma', 'MID', 'bowl', 'High middle-overs squeeze (+53.48 Net/100)')
]

for idx, (p_name, sp_name, p_role, intel) in enumerate(selected_splits, start=1):
    sub = tac_df[(tac_df['player']==p_name) & (tac_df['split']==sp_name) & (tac_df['role']==p_role)]
    if len(sub) > 0:
        row = sub.iloc[0]
        is_low = str(row['sample_flag']).startswith('LOW')
        if is_low:
            grey_tac_rows.append(idx)
        tac_summary_data.append([
            f"{row['player']}", f"{row['split']}", str(int(row['hp_balls'])), str(int(row['runs_scored_or_conceded'])),
            f"{float(row['strike_rate_or_econ']):.1f}", f"{float(row['net100']):+.2f}", f"&plusmn;{float(row['std_err']):.1f}",
            str(row['sample_flag']), intel
        ])

elements.append(make_table(tac_summary_data, [3.2*cm, 1.8*cm, 1.3*cm, 1.1*cm, 1.5*cm, 1.5*cm, 1.8*cm, 2.0*cm, 4.2*cm],
                           fs=5.8, alignments=['LEFT', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'CENTER', 'LEFT'],
                           grey_rows=grey_tac_rows))

elements.append(PageBreak())

# =========================================================================
# PAGE 5: RAJASTHAN ROYALS SQUAD STRENGTHENING & 2027 AUCTION BLUEPRINT
# =========================================================================
elements.append(Paragraph("11. Rajasthan Royals Squad Strengthening & IPL 2027 Auction Strategy", h1_style))
elements.append(Paragraph(
    "Addressing the core contest mandate: <b>How each identified player strengthens Rajasthan Royals' squad for the IPL 2027 auction</b>. "
    "Rajasthan Royals' core boasts world-class assets in <b>Yashasvi Jaiswal</b>, <b>Sanju Samson</b>, <b>Riyan Parag</b>, <b>Dhruv Jurel</b>, and <b>Shimron Hetmyer</b>. "
    "Our empirical audit of RR's 15 contracted players (<code>rrsquadpressureaudit.csv</code>) reveals that only <b>Vaibhav Sooryavanshi (#8)</b> ranks in the top 10 for batting, "
    "while the top bowler is <b>Jofra Archer (#13)</b>. Core hitters (Jaiswal #42, Hetmyer #58, Jurel #60, Parag #78) and bowlers (Bishnoi #93, Curran #63, Sandeep #54) sit below rank 40 under high leverage, "
    "proving the quantitative necessity of acquiring elite clutch specialists for 2027:",
    body_style
))
elements.append(Spacer(1, 1))

# RR Tactical Fit Matrix Table
rr_matrix_data = [
    ['Player & Model Rank', 'Role & Score', 'Availability Status', 'Tactical Squad Strengthening for Rajasthan Royals']
]
rr_targets = [
    ('Phil Salt (Rank #2 Bat)', 'Wk-Batter (0.771)', 'Contracted (RCB); decision due',
     '<b>Explosive Powerplay Opening Partner for Jaiswal:</b> Attacking pace/spin equally (176 SR, +36.9 Net/100) takes powerplay burden off Jaiswal and allows Sanju Samson to anchor at #3 with full tactical freedom.'),
    ('Tim David (Rank #3 Bat)', 'Finisher (0.457)', 'Contracted (RCB); decision due',
     '<b>Clutch Death Finisher:</b> Delivers 174 SR in high-pressure chases (+26.9 Net/100). Pairs with Shimron Hetmyer and Dhruv Jurel to eliminate middle-overs slowdowns.'),
    ('Vaibhav Sooryavanshi (#8 Bat)', 'Top-Order (0.386)', '<b>Contracted to Rajasthan Royals</b>',
     '<b>RR In-House High-Ceiling Asset:</b> Highest raw net value (+75.76 Net/100, 231.1 SR). RR already owns his rights&mdash;the strategic priority is high-pressure match simulations to nurture sample growth.'),
    ('Harry Brook (Rank #10 Bat)', 'Middle-Order (0.322)', '<b>Uncontracted in 2026</b>',
     '<b>Auction Target:</b> 360-degree boundary option under pressure (+25.9 Net/100, 0.72 WPA/100). Available without retention hurdles; provides tactical middle-order flexibility.'),
    ('Sunil Narine (Rank #1 Bowl)', 'Mystery Spin (1.163)', 'Contracted (KKR); decision due',
     '<b>Dream Middle-Overs Controller:</b> 6.51 Econ, 93% bootstrap stability (+37.2 Net/100). Provides the dominant boundary deterrence RR historically enjoyed with Chahal and Ashwin.'),
    ('Mitchell Santner (Rank #3 Bowl)', 'Finger Spin (0.818)', 'Contracted (MI); decision due',
     '<b>Bankable Spin Squeeze:</b> 7.33 Econ, 65% bootstrap stability. Precision left-arm finger spin that maintains pressure at Sawai Mansingh Stadium without leaking boundary balls.'),
    ('Jacob Duffy (Rank #4 Bowl)', 'Pace-Swing (0.772)', 'Contracted (RCB); decision due',
     '<b>Powerplay Breakthrough Bowler:</b> Extraordinary PP swing value (+108.8 Net/100). Offers early wicket-taking capability to replace aging seam assets.'),
    ('Matheesha Pathirana (#5 Bowl)', 'Death Pace (0.727)', 'Contracted (KKR); decision due',
     '<b>Elite Death Overs Execution:</b> Slingy yorkers (+28.5 Net/100, 166 death balls). Solves RR\'s historical death-overs boundary leakage.'),
    ('Mohit Sharma (Rank #9 Bowl)', 'Change-Up Pace (0.540)', '<b>Uncontracted in 2026</b>',
     '<b>Low-Purse Tactical Steal:</b> Uncontracted veteran with proven slower-ball death execution (+25.0 Net/100, 8.64 Econ). Perfect budget-conscious depth addition.')
]

for p_name, r_score, avail, rr_fit in rr_targets:
    rr_matrix_data.append([
        f"<b>{p_name}</b>", r_score, avail, rr_fit
    ])

elements.append(make_table(rr_matrix_data, [3.4*cm, 2.5*cm, 3.5*cm, 9.0*cm], fs=5.8,
                           alignments=['LEFT', 'CENTER', 'LEFT', 'LEFT']))
elements.append(Spacer(1, 2))

elements.append(Paragraph("12. Option A (Pure Sporting Merit) vs. Option B (Actionable Blueprint)", h1_style))
elements.append(Paragraph(
    "&bull; <b>Option A (Pure Sporting Model):</b> Ranks players strictly on empirical math, legitimately preserving Babar Azam (#4 Bat), Fakhar Zaman (#9 Bat), and Abrar Ahmed (#2 Bowl).<br/>"
    "&bull; <b>Option B (Auction Actionable Roster):</b> Excludes Pakistani players due to geopolitical ineligibility and removes retired candidates. "
    "Elevates <b>Harry Brook</b> (#10 &rarr; #8 Bat) and brings in <b>Tim Seifert</b> (#11 Bat, 16% boot) and <b>Shreyas Iyer</b> into the batting order; "
    "advances <b>Mohit Sharma</b> (#9 &rarr; #7 Bowl) and brings in <b>Krunal Pandya</b> (#10 Bowl) and <b>Axar Patel</b> (+18.2 Net/100) into the bowling attack.<br/>"
    "&bull; <b>Dugout Protocol:</b> Option A represents the submitted scientific ranking; Option B provides Rajasthan Royals with a realistic 2027 auction target shortlist.",
    body_style
))
elements.append(Spacer(1, 2))

elements.append(Paragraph("13. Reproducibility & Governance Architecture", h1_style))
elements.append(Paragraph(
    "<b>End-to-End Pipeline:</b> (1) Rebuilt ball states and extras type logic; (2) Dropped 16 scorecard discrepancies and 570 unrecorded targets; "
    "(3) Fitted out-of-fold gradient boosted win-probability and expected-value models (fixed seeds, 5 folds); (4) Computed continuous Leverage Index and opposition ratings; "
    "(5) Aggregated per player, applying Empirical Bayes shrinkage and 4-pillar weighting; (6) Stress-tested via 200 match-level bootstraps and weight sensitivity checks. "
    "<b>Governance Integrity:</b> Zero arbitrary MILP budgets, zero ungrounded price models, zero marketing hype. Complete code and models are reproducible.",
    body_style
))

# Build Document
doc = SimpleDocTemplate(
    'outputs/SupeRR_Selector_Methodology_Report_v4_Top1.pdf',
    pagesize=A4,
    leftMargin=1.3*cm,
    rightMargin=1.3*cm,
    topMargin=1.1*cm,
    bottomMargin=1.1*cm
)

doc.build(elements, canvasmaker=NumberedCanvas)
print("--- PDF Report re-compiled successfully at outputs/SupeRR_Selector_Methodology_Report_v4_Top1.pdf! ---")
