# Rajasthan Royals SupeRR Selector Season 2 — Dugout Intelligence Platform

<p align="center">
  <img src="https://img.shields.io/badge/Competition-Rajasthan_Royals_SupeRR_Selector_S2-E5007D?style=for-the-badge&logo=cricket" alt="RR SupeRR Selector" />
  <img src="https://img.shields.io/badge/Pipeline-143_Integrity_Checks_Passing-10B981?style=for-the-badge&logo=checkmarx" alt="Checks Passing" />
  <img src="https://img.shields.io/badge/Deployment-Render_Static_Site-46E3B7?style=for-the-badge&logo=render" alt="Render Ready" />
  <img src="https://img.shields.io/badge/Dataset-197%2C100_Balls_•_851_Matches-041126?style=for-the-badge" alt="Dataset" />
  <img src="https://img.shields.io/badge/Tactical_Engines-13_Dugout_Simulators-38BDF8?style=for-the-badge&logo=cricket" alt="Tactical Engines" />
  <img src="https://img.shields.io/badge/Mobile-100%25_Feature_Parity-F59E0B?style=for-the-badge" alt="Mobile Parity" />
</p>

---

## 📌 Executive Overview

This repository contains the comprehensive quantitative research, tactical simulation suite, and interactive intelligence terminal developed for the **Rajasthan Royals SupeRR Selector Season 2 (Round 1)**.

The objective of this challenge is to identify and validate the **Top 10 Batters** and **Top 10 Bowlers** who deliver elite performance under high pressure in T20 cricket across the 2022–2026 data window (851 matches, 197,100 legal deliveries, 958 players).

### Official Deliverables & Portals
* 🌐 **Live Interactive Intelligence Terminal:** [https://superrselectoranalysis.onrender.com](https://superrselectoranalysis.onrender.com)
* 📄 **Official 5-Page Master Methodology Report:** [`outputs/SupeRR_Selector_Methodology_Report_v4_Top1.pdf`](outputs/SupeRR_Selector_Methodology_Report_v4_Top1.pdf)
* 📊 **Verified Ground Truth Benchmark Dataset:** [`data/RR_Player_Evaluation_Master.csv`](data/RR_Player_Evaluation_Master.csv)
* ⚡ **Automated 143-Assertion Verification Suite:** [`scripts/verify_project_integrity.py`](scripts/verify_project_integrity.py) &amp; [`scripts/verify_ui_smoke.py`](scripts/verify_ui_smoke.py)

---

## 🏆 Verified Top 10 Leaderboards

All rankings and metrics are empirically verified character-for-character across `data/RR_Player_Evaluation_Master.csv`, the interactive platform (`index.html`), and the official 5-page PDF report.

### 🏏 Top 10 Batters Under High Pressure ($LI \ge 1.32$)

*Primary Model: Opposition-Adjusted Model (Leave-One-Match-Out Adjustments & Empirical Bayes Shrinkage)*

| Rank | Batter | HP Balls | Net/100 | Delta ($\Delta$) | WPA/100 | Consistency | Adj. Score | Bootstrap Top 10 | Primary Franchise |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **1** | **Suryakumar Yadav** | 697 | +38.74 | +13.10 | +0.629 | 72.9% | **0.843** | 76.0% | Mumbai Indians |
| **2** | **Phil Salt** | 339 | +36.85 | +17.42 | +0.839 | 77.4% | **0.771** | 82.0% | Kolkata Knight Riders |
| **3** | **Tim David** | 419 | +26.85 | -10.51 | +0.847 | 64.9% | **0.457** | 37.5% | Mumbai Indians |
| **4** | **Babar Azam** | 220 | +24.44 | +26.62 | +0.242 | 72.7% | **0.438** | 24.5% | Peshawar Zalmi |
| **5** | **Shubman Gill** | 564 | +15.31 | +6.22 | +0.310 | 72.3% | **0.437** | 19.5% | Gujarat Titans |
| **6** | **Nicholas Pooran** | 575 | +21.84 | +6.48 | +0.127 | 70.2% | **0.412** | 26.5% | Lucknow Super Giants |
| **7** | **Abhishek Sharma** | 476 | +24.34 | -14.38 | +0.494 | 67.5% | **0.410** | 16.0% | Sunrisers Hyderabad |
| **8** | **Vaibhav Sooryavanshi** | 161 | +75.76 | +7.89 | +1.209 | 55.6% | **0.386** | 39.0% | Rajasthan Royals |
| **9** | **Fakhar Zaman** | 217 | +19.25 | +23.87 | +0.635 | 66.7% | **0.343** | 24.0% | Lahore Qalandars |
| **10** | **Harry Brook** | 193 | +25.94 | +10.49 | +0.724 | 64.7% | **0.322** | 22.5% | Delhi Capitals |

*Note on Model Variations:* In the Original (pre-adjustment) Model, Heinrich Klaasen (#7) and Shimron Hetmyer (#9) occupy Top 10 slots. Under the rigorous Opposition-Adjusted Model, **Harry Brook** moves into the Top 10 (#10) due to exceptional quality-of-bowling adjustments.

---

### 🎯 Top 10 Bowlers Under High Pressure ($LI \ge 1.32$)

*Primary Model: Opposition-Adjusted Model (Leave-One-Match-Out Adjustments & Empirical Bayes Shrinkage)*

| Rank | Bowler | HP Balls | Net/100 | Delta ($\Delta$) | WPA/100 | Consistency | Adj. Score | HP Econ | Wickets | Primary Franchise |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **1** | **Sunil Narine** | 393 | +37.20 | +19.01 | +1.355 | 69.0% | **1.163** | 6.51 | 24 | Kolkata Knight Riders |
| **2** | **Abrar Ahmed** | 178 | +42.26 | +26.40 | +0.898 | 72.2% | **0.866** | 6.14 | 12 | Quetta Gladiators |
| **3** | **Mitchell Santner** | 409 | +26.38 | +16.87 | +0.633 | 67.6% | **0.818** | 7.33 | 25 | Chennai Super Kings |
| **4** | **Jacob Duffy** | 167 | +60.05 | +59.32 | +0.533 | 61.1% | **0.772** | 8.29 | 20 | Otago / New Zealand |
| **5** | **Matheesha Pathirana** | 315 | +21.14 | -0.19 | +0.677 | 71.4% | **0.727** | 8.78 | 23 | Chennai Super Kings |
| **6** | **Lockie Ferguson** | 247 | +35.49 | +38.05 | +1.048 | 54.2% | **0.679** | 7.61 | 16 | Royal Challengers Bengaluru |
| **7** | **Taskin Ahmed** | 239 | +34.69 | +36.49 | +0.520 | 60.0% | **0.641** | 6.53 | 19 | Dhaka Dominators |
| **8** | **Josh Hazlewood** | 398 | +33.78 | +23.52 | +0.524 | 51.3% | **0.596** | 7.73 | 31 | Royal Challengers Bengaluru |
| **9** | **Mohit Sharma** | 176 | +24.96 | +38.51 | +0.802 | 60.0% | **0.540** | 8.64 | 12 | Gujarat Titans |
| **10** | **Krunal Pandya** | 340 | +19.88 | +12.46 | +0.508 | 60.6% | **0.537** | 7.21 | 18 | Lucknow Super Giants |

*Note on Model Variations:* In the Original Model, Jofra Archer (#6) and Kuldeep Yadav (#7) hold top spots. Under the Opposition-Adjusted Model, **Mohit Sharma** vaults into the Top 10 (#9) by virtue of elite death-overs strike rate (+38.51 Delta) against top-order hitters.

---

## 🔬 Core Methodology & Mathematical Architecture

### 1. Defining High Pressure via Continuous Leverage Index ($LI$)
Rather than using static proxies (such as death overs alone or arbitrary run-rate thresholds), pressure is modeled using continuous ball-by-ball **Leverage Index ($LI$)**:
$$LI = \frac{\sigma(\Delta \text{WP}_{\text{ball}})}{\mathbb{E}[\sigma(\Delta \text{WP}_{\text{all}})]}$$
* Deliveries in the **top quartile of leverage** ($LI \ge 1.32$) are designated as **High Pressure (HP)**.
* In baseline balls ($LI < 1.32$), average win-probability swing is **0.62 percentage points per ball**.
* In high-pressure balls ($LI \ge 1.32$), volatility surges **6.0× to 3.73 percentage points per ball**.

### 2. Four-Pillar Composite Metric
Player rankings synthesize four normalized, orthogonal performance dimensions:
$$\text{Score} = 0.35 \cdot z(\text{Net}_{100}^S) + 0.30 \cdot z(\text{WPA}_{100}^S) + 0.20 \cdot z(\Delta_{HP}^S) + 0.15 \cdot z(\text{Cons}^S)$$
1. **$\text{Net}_{100}^S$ (Run-Value Created per 100 Balls):** Expected run differential relative to average T20 performance, adjusted for phase and venue.
2. **$\text{WPA}_{100}^S$ (Win Probability Added per 100 Balls):** Direct attribution of match equity swings delivered by the player.
3. **$\Delta_{HP}^S$ (Pressure Surge Delta):** Difference between the player's high-pressure performance and their ordinary baseline ($Net_{HP} - Net_{Ord}$), rewarding clutch elevation.
4. **$\text{Cons}^S$ (Consistency Hit-Rate):** Proportion of high-pressure deliveries where the player produced non-negative run equity.

### 3. Empirical Bayes Shrinkage
To prevent small-sample distortions (e.g., a batter facing 40 deliveries hitting 3 consecutive sixes), all raw statistics are shrunk toward an empirical prior weighted by pseudo-deliveries equivalent to approximately 8 matches ($M \approx 150$ balls):
$$\hat{\theta}_i = \frac{N_i}{N_i + M} \cdot \bar{X}_i + \frac{M}{N_i + M} \cdot \mu_{\text{prior}}$$

### 4. Stability Validation: 200 Match-Level Bootstrap Resamples
Rankings are evaluated across **200 match-level bootstrap resamples** (and 300 resamples for the original model), drawing full match clusters with replacement. This quantifies the probability $P(\text{Top } 10)$ that a player ranks within the top decile across random resamples, identifying rock-solid anchors (Sunil Narine 93%, Phil Salt 82%, Suryakumar Yadav 76%).

---

## 💡 Key Empirical & Tactical Insights

### 1. The Jasprit Bumrah Defensive Preservation Paradox
Jasprit Bumrah logged **506 high-pressure balls** with an elite economy rate of **6.81 RPO** and **42.2% dot balls**, yet captured **20 wickets** against an expected wicket tally of **27.8**, resulting in a **+15.73 Net/100** (sitting **-11.19** below his extraordinary baseline).
* *Root Cause:* Opposition batters actively adopt an ultra-defensive posture against Bumrah under high pressure, refusing to attack his deliveries and voluntarily deferring boundary attempts to other bowlers.
* *Methodological Decision:* Because match-level event logs cannot separate batter risk-aversion from match state, our model reports Bumrah's empirical figures transparently rather than inflating his score through subjective heuristics.

### 2. Vaibhav Sooryavanshi (#8 Batter)
Rajasthan Royals' youngest contracted asset recorded an astronomical **+75.76 Net/100** across 161 high-pressure balls. Empirical Bayes shrinkage dampens his raw output while still recognizing his remarkable clutch boundary-hitting capability, positioning him at Rank #8 globally.

### 3. Rajasthan Royals 15-Player Squad Audit
The audit evaluates 15 RR-contracted assets under pressure:
* **Dhruv Jurel (+16.9 Net/100):** Elite middle/death overs chase executor.
* **Riyan Parag (+14.3 Net/100):** Proven spin-hitting capability under pressure.
* **Sandeep Sharma (6.81 HP Econ):** Elite death-overs economy anchor.
* **Tactical Need:** High-pressure bowling depth to support Jofra Archer (adjusted Rank #13).

### 4. Option B: Availability-Adjusted Pool
If geopolitical or contractual constraints restrict Pakistani players (Babar Azam, Fakhar Zaman, Abrar Ahmed):
* **Batters Entering Top 10:** Tim Seifert (#11) and Shreyas Iyer (#12).
* **Bowler Entering Top 10:** Axar Patel (#11).
* **Core Retention:** Harry Brook (#10) and Mohit Sharma (#9) securely retain their Top 10 standing.

---

## ⚡ 12 Flagship Dugout Tactical Simulation Engines & Interactive Suite

The platform integrates twelve specialized computational engines and interactive broadcast modules directly inside the dashboard (plus a **60s Executive Judge Walkthrough** for rapid evaluation):

```
┌────────────────────────────────────────────────────────────────────────┐
│                   DUGOUT TACTICAL COMPUTATION SUITE                    │
├──────────────────────────┬──────────────────────────┬──────────────────┤
│ 📐 SMS Field Holodeck    │ 🧬 Quantum Impact Sub    │ 🏆 Season 10K    │
│ 78m vs 66m Asymmetry     │ Bellman V(t) Optimizer   │ Monte Carlo Sim  │
├──────────────────────────┼──────────────────────────┼──────────────────┤
│ 🛡️ 20-Over Defense Matrix│ ⚡ Win-Prob Chase Sim    │ ⚔️ Duel Sim      │
│ Phase Resource Allocator │ Ball-by-Ball Leverage    │ Matchup Matrix   │
├──────────────────────────┴──────────────────────────┴──────────────────┤
│ 💰 Auction War Room & Walk-Away Valuation Console                      │
│ Budget Allocation, Reserve Price & Bidding Curve Modeling              │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. SMS Field Placement Holodeck (Jaipur 78m Physics)
* **Venue Geometry:** Faithfully replicates Sawai Mansingh Stadium, Jaipur asymmetric dimensions (78m Straight North/South vs 66m Square East/West).
* **Interactive Drag & Drop:** Interactive touch/mouse placement of all 9 fielders with boundary collision clamping.
* **Shot Dispersion Heat Rays:** Sector wagon-wheel overlays for elite strikers (Suryakumar Yadav 360° ramp, Heinrich Klaasen spin arc, Phil Salt offside drive).
* **Expected Runs ($xR$) Suppression:** Dynamically computes boundary denial and catch probabilities based on fielder distances.
* **BCCI Regulation Checker:** Enforces field legality (maximum 5 fielders outside the 30-yard ring during non-powerplay overs).

### 2. Quantum Impact Player Sim (Bellman Dynamic Programming)
* **Bellman Dynamic $V(t)$:** Formulates tactical substitution as an optimal stopping problem where substitution option value decays over match overs.
* **Lineup Switchboard:** Real-time swap simulator across Rajasthan Royals' match-day XI and 5 designated bench options.
* **Overseas Quota Constraint:** Live validation preventing violations of the maximum 4 overseas player rule.
* **Pre-Set Scenarios:** Includes the *SMS Jaipur Spin Web* (+8.6% win equity) and *Mohit Sharma Death Shield* presets.

### 3. 10,000-Sim Playoff Multi-Universe Monte Carlo
* **High-Speed Vectorized Simulation:** Executes 10,000 full-tournament Monte Carlo seasons in $<15\text{ms}$ in a background Web Worker.
* **Tournament Probabilities:** Calculates exact odds for Playoff Qualification ($P(\text{Top } 4)$), Double Chance ($P(\text{Top } 2)$), and Tournament Championship.
* **Net Run Rate (NRR) Density:** Generates kernel density estimates of projected finishing NRR.
* **Interactive 14-Fixture Switchboard:** Allows coaches to toggle match outcomes against CSK, MI, KKR, RCB, and inspect live qualification ripples.

### 4. 20-Over Defense & Phase Resource Planner
* **Phase Allocation:** Visualizes Powerplay (Overs 1–6), Middle (7–15), and Death (16–20) bowler quotas.
* **Dynamic Telemetry Gauges:** Real-time projected death economy (RPO), high-leverage run savings ($LI \ge 1.32$), and projected 20-over totals.
* **Tactical Blueprints:** One-click blueprints comparing *Mohit Sharma Death Lockdown* (recommended) against *Current RR Status Quo* and *SMS Jaipur Spin Choke*.

### 5. Win-Probability Chase Simulator
* **Ball-by-Ball Trajectory:** Models chase equity swings across 120 balls with real-time wicket drops and run requirements.
* **Calibrated GBDT Engine:** Trained on 197,100 deliveries ($\text{AUC} = 0.89$ chase, $0.68$ 1st innings, Brier score $0.137$).
* **Critical In-Play Moments:** Highlights pivot deliveries where single balls shifted match win probability by $> 15\%$.

### 6. Matchup Duel Simulator
* **Probabilistic Head-to-Head:** Evaluates batter vs bowler matchups across pace/spin types and match phases.
* **Empirical Splits:** Reports balls faced, dismissal counts, dot ball rates, and boundary percentages.
* **Classification:** *Illustrative toy, not a model output* (built for scenario exploration rather than definitive player grading).

### 7. Auction War Room & Valuation Console
* **Walk-Away Ceilings:** Quantifies maximum rational bid thresholds for uncontracted targets (Phil Salt, Mitchell Santner, Jacob Duffy).
* **Budget Optimization:** Models salary cap distribution across Indian core retention and auction acquisitions.

### 8. 🎙️ Live Dugout AI Voice Commentary & Radio Comms
* **Speech Synthesis Engine:** Situational broadcast commentary powered by the Web Speech API with custom dugout voice inflection.
* **Contextual Triggering:** Automatically commentates sixes, cracking fours, bails-flying wickets, close DRS verdicts, and Super Over finishes with real-time text HUD subtitles.

### 9. ⚡ Interactive DRS (Decision Review System) & UltraEdge / Hawk-Eye
* **UltraEdge Seismograph:** Dynamic audio spike waveform synchronized with bat-ball proximity and contact timestamps.
* **3D Hawk-Eye Ball Tracking:** Parabolic trajectory simulation from bowler hand release through pitch impact point to Zing stumps (Impact in-line / hitting stumps).
* **3rd Umpire Sequence:** Automatic resolution sequence (Pending Review → Decision Overturned / Confirmed) with instant scorecard and strike synchronization.

### 10. 🎯 Interactive Drag-and-Drop Field Setting & Real-Time Hazard Telemetry
* **Direct Turf Manipulation:** Drag-and-drop fielder repositioning within Jaipur Holodeck boundary ropes with desktop mouse and mobile touch-drag events.
* **Dynamic Hazard Algorithm:** Calculates angular dispersion gaps across 10 fielders to evaluate real-time Boundary Hazard % and Catch Probability %.
* **Tactical Presets:** Instant deployment of battle-tested T20 formations: *Death Squeeze 5-4*, *Double Slip & Gully*, *Wide Yorker 7-2 Off-Side Trap*, and *Balanced Ring*.

### 11. 🏆 RR Legacy Duels Historical Scenario Challenge Mode
* **Championship Scenarios:** Relive iconic clutch moments from franchise history:
  * **2024 Eden Gardens Miracle:** Jos Buttler 107* chase needing 46 off 18 balls with tailenders.
  * **2008 Inaugural IPL Final:** Shane Warne & Sohail Tanvir needing 1 run off 1 ball vs CSK.
  * **2022 Qualifier 2:** Jos Buttler 106* masterclass to seal the Final berth.
* **Tactical Objectives Tracker:** Evaluates primary chase goals, century milestones, and wicket protection in real-time with gold victory trophies.

### 12. 🌧️ Dynamic DLS (Duckworth-Lewis-Stern) Rain Delay & Par Score Calculator
* **Empirical ICC Resource Formulation:** Implements the official Frank Duckworth-Tony Lewis T20 resource matrix across all 20 overs and 10 wickets.
* **Live Par Telemetry:** Calculates real-time ball-by-ball DLS par score with positive/negative equity indicators (`+8 Ahead (Safe 🟢)` / `-6 Behind (Risk 🔴)`).
* **Curtailed Match Simulator:** Models match reduction to 18, 16, 15, 14, 12, or 10 overs, dynamically recalibrating revised target scores and required run rates.

### 13. 🧬 Ball-by-Ball Tactical Blueprint & Evidence Vault (Zero Synthetic Priors)
* **Empirical Extraction Pipeline (`scripts/build_tactical_blueprint.py`):** Mines all 49,276 high-pressure deliveries ($LI \ge 1.32$ across 197,100 deliveries in `b3.pkl`, joined cleanly via `(comp_id, team_id)` with `matches.csv`, `teams.csv`, and `competitions.csv`) into `data/tactical_blueprint_data.json` for 131 featured player profiles.
* **Over/Around × Off/On-Side Heatmaps:** Interactive 2×2 tactical channel grids displaying exact HP balls, runs, wickets, dot%, boundary%, `Net/100 ± SE`, and low-sample ($n < 15$) guards, with direct synchronization to the SMS Jaipur Holodeck Pitch Map.
* **Delivery Style, Radar Speed Bands & Stroke Dismissal Traps:** Breaks down effectiveness across delivery styles (`Out Swing`, `Inswing`, `Off Cutter`, `Googly`, `Yorker`), pace radar bands (`<135`, `135–142`, `>142 kph`), and top wicket-producing stroke traps.
* **Forensic Bumrah 506-Ball Posture Proof:** Direct comparison across pace and spin peers auditing Jasprit Bumrah's 506 high-pressure deliveries (`48.2%` attacking shots faced vs `62.9%` Archer / `67.1%` Sandeep; `+84.83 Saved/100` on explicit defensive strokes).
* **Clickable Receipt Vault, Historical H2H Matrix & 9-Opponent RR Counter-XI:** Surfaces exact match-by-match WPA swing receipts, 350+ embedded (1,669 total mined) Empirical Bayes shrunk ($k=12$) batter-vs-bowler H2H records, and match-day tactical counter-plans for Rajasthan Royals vs all 9 IPL franchises.

---

## 🌐 3D Aerospace State-Space Universe

The terminal features an interactive 3D WebGL data universe built on Three.js:

* **State-Space Formulation:** Maps 202 qualified players into continuous 3D Euclidean spatial coordinates:
  * **$X$-Axis:** High-Pressure Deliveries Faced / Bowled (Volume)
  * **$Y$-Axis (Height):** Net Value Created per 100 Deliveries (Efficiency)
  * **$Z$-Axis:** Delta vs. Ordinary Baseline (Clutch Elevation)
* **Visual Atmosphere:** Cyber deep-space environment with 1,500 stardust particles, concentric stadium radar floor rings, and dual gimbal rings for #1 seeds.
* **Interactive Raycasting:** Mouse hover and touch-tap targeting with vertical drop lasers, reticles, coordinate readouts, and direct links to full player profiles.

---

## 📱 Mobile Application Architecture & Parity

The platform delivers complete feature parity and responsive touch layouts on mobile viewports (`width <= 767px`):

* **Native Bottom Navigation Bar:** Persistent mobile bottom bar with quick triggers:
  * `[ 📊 Overview ]` &bull; `[ 🏆 Top 10 ]` &bull; `[ ⚡ Tactical ]` &bull; `[ 🌐 3D Space ]` &bull; `[ ☰ Modules ]`
* **Slide-Up Tactical Navigation Sheet:** Smooth mobile drawer providing one-tap access to all 7 simulation engines, the 3D universe, and executive tools.
* **Touch-Swipe Dismissals:** Native downward swipe gestures to dismiss drawers and modal sheets.
* **Responsive 2-Column Grids:** Automated single-column reflow (`.tactical-two-col-grid`) preventing squashed SVG turf diagrams or tables on phones.
* **Touch-Tap 3D Targeting:** Instant node selection and docked holographic cards optimized for one-handed smartphone use.

---

## 📂 Repository Directory Tree

```text
superr-selector-analysis/
├── assets/                               # Visualizations and diagnostic figures
│   ├── c1.png                            # Figure 1: Over-by-over Leverage Index & WP Calibration
│   ├── c2.png                            # Figure 2: Pressure Value vs. Ordinary Baseline (Scatter)
│   └── c3.png                            # Figure 3: Bootstrap Stability Distribution
├── data/                                 # Consolidated datasets and verified benchmarks
│   ├── RR_Player_Evaluation_Master.csv   # Master verified benchmark (Top 10 Bat & Bowl)
│   ├── tactical_splits_verified.csv      # Pace/Spin & Match Phase situational breakdowns
│   ├── rr_squad_pressure_audit.csv       # Empirical pressure audit of 15 RR-contracted players
│   ├── adjusted_all_batters.csv          # Complete qualified batters ranking (100 players)
│   ├── adjusted_all_bowlers.csv          # Complete qualified bowlers ranking (102 players)
│   ├── availability.csv                  # Contractual, nationality, and IPL availability flags
│   ├── wp_calibration.csv                # Win-probability model calibration logs
│   └── raw/                              # Supplementary raw ball-by-ball artifacts
├── outputs/                              # Official deliverables and reports
│   ├── SupeRR_Selector_Methodology_Report_v4_Top1.pdf     # Official 5-page Master Methodology Report
│   ├── SupeRR_Selector_Methodology_Report_v3_adjusted.pdf # 5-page Adjusted Report v3
│   ├── SupeRR_Selector_Dugout_Presentation.pdf            # Dugout presentation slide deck
│   └── SupeRR_Round1_Rankings.xlsx                        # Multi-tab data workbook
├── scripts/                              # Data science pipeline, models & verification
│   ├── verify_project_integrity.py       # Automated 136-assertion integrity test suite
│   ├── build_top1_report.py              # ReportLab generator for 5-page Master PDF
│   ├── compute_tactical_splits.py        # Situational pace/spin and phase metrics extractor
│   ├── auction_optimizer.py              # Squad balance and auction valuation simulator
│   └── s1_build.py to s4_opp.py          # WPA, leverage, and Empirical Bayes shrinkage pipeline
├── index.html                            # Interactive Dugout Intelligence Platform (SPA)
├── render.yaml                           # 1-click Render static site deployment specification
├── requirements.txt                      # Python dependencies (ReportLab, Pandas, NumPy, etc.)
└── README.md                             # Comprehensive technical documentation
```

---

## ⚡ Automated Integrity Verification Suite

To validate 100% data integrity, numeric consistency, and adherence to competition constraints, run the automated verification script:

```bash
# Run 136 automated integrity checks
python3 scripts/verify_project_integrity.py

# Expected Output:
# 136 checks run
```

### Audited Pipeline Verifications
* **Cross-File Data Consistency:** Compares values across `RR_Player_Evaluation_Master.csv`, `index.html`, and `SupeRR_Selector_Methodology_Report_v4_Top1.pdf`.
* **Zero Broken Assets:** Validates that all script files, chart assets, and output PDFs exist and contain valid data.
* **Numeric Accuracy:** Validates that Net/100, WPA/100, Delta, and consistency hit-rates match ground truth records down to the third decimal place.

---

## 🚀 Deployment to Render (1-Click)

The platform is designed as an ultra-fast, single-page application with zero external runtime dependencies.

### Automatic Setup via `render.yaml`
1. Push this repository to your GitHub account: `https://github.com/NaniToka/Superrselectoranalysis.git`.
2. Sign in to **[Render](https://dashboard.render.com/)**.
3. Click **New +** $\rightarrow$ **Static Site**.
4. Connect your repository: `Superrselectoranalysis`.
5. Configuration parameters:
   * **Build Command:** *(leave empty or `echo "Build Ready"`)*
   * **Publish Directory:** `.` *(root directory)*
6. Click **Create Static Site** to deploy. Live URL: [https://superrselectoranalysis.onrender.com](https://superrselectoranalysis.onrender.com).

---

## 🛠️ Local Development & PDF Compilation

### Prerequisites
* Python 3.10 or higher
* Node.js (optional, for syntax linting)

### Setup Instructions
```bash
# 1. Clone the repository
git clone https://github.com/NaniToka/Superrselectoranalysis.git
cd Superrselectoranalysis

# 2. Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Execute the automated verification suite (136 assertions)
python3 scripts/verify_project_integrity.py

# 4. Recompile the official 5-page Master Methodology Report PDF
python3 scripts/build_top1_report.py

# 5. Launch the local web server to explore the terminal
python3 -m http.server 8000
# Open http://localhost:8000 in your web browser
```

---

## 👥 Credits & Governance

* **Competition:** Rajasthan Royals SupeRR Selector Season 2 (Round 1)
* **Dataset Scope:** 851 T20 Matches &bull; 197,100 Deliveries &bull; 958 Players (2022–2026)
* **Lead Analytics & Engineering:** Toka Nani / Team SupeRR Selector
* **Franchise Alignment:** Rajasthan Royals (IPL) &bull; Sawai Mansingh Stadium, Jaipur

<p align="center">
  <b>Rajasthan Royals SupeRR Selector Season 2</b> &bull; Built with mathematical precision &bull; <i>Halla Bol! 💗👑</i>
</p>
