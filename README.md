# SupeRR Selector Season 2 — RR Intelligence Platform

<p align="center">
  <img src="https://img.shields.io/badge/Competition-Rajasthan_Royals_SupeRR_Selector_S2-E5007D?style=for-the-badge&logo=cricket" alt="RR SupeRR Selector" />
  <img src="https://img.shields.io/badge/Pipeline-136_Integrity_Checks_Passing-10B981?style=for-the-badge&logo=checkmarx" alt="Checks Passing" />
  <img src="https://img.shields.io/badge/Deployment-Render_Static_Site-46E3B7?style=for-the-badge&logo=render" alt="Render Ready" />
  <img src="https://img.shields.io/badge/Dataset-197%2C100_Balls_•_851_Matches-041126?style=for-the-badge" alt="Dataset" />
</p>

---

## 📌 Executive Overview

This repository houses the official quantitative submission for the **Rajasthan Royals SupeRR Selector Season 2 (Round 1)**.

The objective of this challenge is to identify the **Top 10 Batters** and **Top 10 Bowlers** who perform best under high pressure in T20 cricket (2022–2026), supported by an empirical methodology, an interactive telemetry dashboard, and a publication-grade methodology report.

- 🌐 **Live Interactive Intelligence Dashboard:** [Deploy via Render Static Site / `index.html`]
- 📄 **Official 5-Page Methodology Report:** [`outputs/SupeRR_Selector_Methodology_Report_v4_Top1.pdf`](outputs/SupeRR_Selector_Methodology_Report_v4_Top1.pdf)
- 📊 **Verified Consolidated Datasets:** [`data/`](data/)

---

## 📁 Repository Structure

The project has been organized into a modular directory hierarchy:

```text
superr-selector-analysis/
├── assets/                               # Visualizations and diagnostic charts
│   ├── c1.png                            # Figure 1: Over-by-over Leverage Index & WP Calibration
│   ├── c2.png                            # Figure 2: Pressure Value vs. Ordinary Baseline (Scatter)
│   └── c3.png                            # Figure 3: Bootstrap Stability Distribution (Top 10 / Top 5)
├── data/                                 # Consolidated analysis datasets & verified benchmarks
│   ├── expected_dashboard_values.csv     # Official Top 10 Batters & Bowlers verified benchmark
│   ├── tactical_splits_verified.csv      # Pace/Spin & Match Phase situational breakdowns
│   ├── rr_squad_pressure_audit.csv       # Empirical pressure audit of 15 RR-contracted players
│   ├── adjusted_all_batters.csv          # Complete qualified batters ranking (100 players)
│   ├── adjusted_all_bowlers.csv          # Complete qualified bowlers ranking (102 players)
│   ├── availability.csv                  # Contractual, nationality, and IPL 2026 availability flags
│   └── wp_calibration.csv                # Win-probability model calibration logs
├── outputs/                              # Official deliverables and reports
│   ├── SupeRR_Selector_Methodology_Report_v4_Top1.pdf     # 5-page Master Methodology Report
│   ├── SupeRR_Selector_Methodology_Report_v3_adjusted.pdf # 5-page Version 3 adjusted report
│   ├── SupeRR_Selector_Dugout_Presentation.pdf            # Dugout presentation slides
│   └── SupeRR_Round1_Rankings.xlsx                        # Multi-tab data workbook
├── scripts/                              # Data science pipeline, models & verification
│   ├── verify_project_integrity.py       # Automated 136-assertion integrity test suite
│   ├── build_top1_report.py              # ReportLab generator for 5-page Master PDF
│   ├── compute_tactical_splits.py        # Situational pace/spin and phase metrics extractor
│   ├── s1_build.py to s4_opp.py          # WPA, leverage, and Empirical Bayes shrinkage pipeline
│   └── auction_optimizer.py              # Squad balance and constraint simulation
├── index.html                            # Google-grade interactive intelligence dashboard (SPA)
├── render.yaml                           # 1-click Render static site deployment specification
├── requirements.txt                      # Python dependencies (ReportLab, Pandas, NumPy, etc.)
└── .gitignore                            # Clean version control exclusions
```

---

## 🏆 Verified Top 10 Leaderboards

All metrics are verified across `expected_dashboard_values.csv`, `index.html`, and `SupeRR_Selector_Methodology_Report_v4_Top1.pdf`.

### 🏏 Top 10 Batters Under High Pressure

| Rank | Batter | HP Balls | Net/100 | Delta ($\Delta$) | WPA/100 | Consistency | Adj. Score | Bootstrap Top 10 |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **Suryakumar Yadav** | 697 | +38.74 | +13.10 | +0.629 | 72.9% | **0.843** | 76.0% |
| **2** | **Phil Salt** | 339 | +36.85 | +17.42 | +0.839 | 77.4% | **0.771** | 82.0% |
| **3** | **Tim David** | 419 | +26.85 | -10.51 | +0.847 | 64.9% | **0.457** | 37.5% |
| **4** | **Babar Azam** | 220 | +24.44 | +26.62 | +0.242 | 72.7% | **0.438** | 24.5% |
| **5** | **Shubman Gill** | 564 | +15.31 | +6.22 | +0.310 | 72.3% | **0.437** | 19.5% |
| **6** | **Nicholas Pooran** | 575 | +21.84 | +6.48 | +0.127 | 70.2% | **0.412** | 26.5% |
| **7** | **Abhishek Sharma** | 476 | +24.34 | -14.38 | +0.494 | 67.5% | **0.410** | 16.0% |
| **8** | **Vaibhav Sooryavanshi** | 161 | +75.76 | +7.89 | +1.209 | 55.6% | **0.386** | 39.0% |
| **9** | **Fakhar Zaman** | 217 | +19.25 | +23.87 | +0.635 | 66.7% | **0.343** | 24.0% |
| **10** | **Harry Brook** | 193 | +25.94 | +10.49 | +0.724 | 64.7% | **0.322** | 22.5% |

### 🎯 Top 10 Bowlers Under High Pressure

| Rank | Bowler | HP Balls | Net/100 | Delta ($\Delta$) | WPA/100 | Consistency | Adj. Score | HP Econ | Wickets |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **Sunil Narine** | 393 | +37.20 | +19.01 | +1.355 | 69.0% | **1.163** | 6.51 | 24 |
| **2** | **Abrar Ahmed** | 178 | +42.26 | +26.40 | +0.898 | 72.2% | **0.866** | 6.14 | 12 |
| **3** | **Mitchell Santner** | 409 | +26.38 | +16.87 | +0.633 | 67.6% | **0.818** | 7.33 | 25 |
| **4** | **Jacob Duffy** | 167 | +60.05 | +59.32 | +0.533 | 61.1% | **0.772** | 8.29 | 20 |
| **5** | **Matheesha Pathirana** | 315 | +21.14 | -0.19 | +0.677 | 71.4% | **0.727** | 8.78 | 23 |
| **6** | **Lockie Ferguson** | 247 | +35.49 | +38.05 | +1.048 | 54.2% | **0.679** | 7.61 | 16 |
| **7** | **Taskin Ahmed** | 239 | +34.69 | +36.49 | +0.520 | 60.0% | **0.641** | 6.53 | 19 |
| **8** | **Josh Hazlewood** | 398 | +33.78 | +23.52 | +0.524 | 51.3% | **0.596** | 7.73 | 31 |
| **9** | **Mohit Sharma** | 176 | +24.96 | +38.51 | +0.802 | 60.0% | **0.540** | 8.64 | 12 |
| **10** | **Krunal Pandya** | 340 | +19.88 | +12.46 | +0.508 | 60.6% | **0.537** | 7.21 | 18 |

---

## 🔬 Core Methodology & Mathematical Rigor

### 1. Defining High Pressure (Leverage Index)
Pressure is not defined arbitrarily by over number or chasing status alone. Instead, we model ball-by-ball **Leverage Index (LI)**—the expected win-probability swing of the upcoming delivery.
- Deliveries in the **top 25% of leverage** ($\text{LI} \ge 1.32$) are classified as **High Pressure (HP)**.
- In low-pressure balls, average swing is **0.62 percentage points/ball**; in high-pressure balls, volatility surges **6.0× to 3.73 percentage points/ball**.

### 2. Four-Pillar Composite Metric
To evaluate true player quality under pressure, four normalized z-scores are combined:
$$\text{Score} = 0.35 \cdot z(\text{Net}_{100}^S) + 0.30 \cdot z(\text{WPA}_{100}^S) + 0.20 \cdot z(\Delta_{HP}^S) + 0.15 \cdot z(\text{Cons}^S)$$
- **Empirical Bayes Shrinkage:** All statistics are shrunk toward a prior distribution (weighted by 8 pseudo-matches / ~150 deliveries) to eliminate small-sample flukes.
- **Opposition Quality Adjustments:** Leave-one-match-out adjustments account for the strength of opposing batters and bowlers faced.

### 3. The Jasprit Bumrah Empirical Finding
Jasprit Bumrah logged **506 HP deliveries**, conceding just **42.2% dot balls** and a batter strike rate of **125.4**, capturing **20 wickets** against **27.8 expected**, for a **+15.73 Net/100** (sitting **-11.19** below his ordinary baseline).  
*Key Takeaway:* Batters employ extreme defensive preservation against Bumrah under pressure, refusing to hit boundaries and voluntarily suppressing wicket events. Because the data pack cannot isolate batter avoidance from match state, our methodology reports the empirical numbers without speculative post-hoc inflation.

### 4. Option B (Availability-Adjusted Alternative)
If Pakistani players (Babar Azam, Fakhar Zaman, Abrar Ahmed) are excluded due to IPL auction eligibility rules:
- **Batters entering Top 10:** Tim Seifert (#11) and Shreyas Iyer (#12).
- **Bowler entering Top 10:** Axar Patel (#11).
- Harry Brook (#10) and Mohit Sharma (#9) remain within the Top 10.

---

## ⚡ Automated Verification Suite

To guarantee 100% data integrity, character-for-character consistency, and adherence to competition constraints, run the automated verification script:

```bash
# Run 136 automated integrity checks
python3 scripts/verify_project_integrity.py

# Expected Output:
# 136 checks run
```

---

## 🚀 Deployment to Render (1-Click)

The dashboard (`index.html`) is an ultra-fast, single-page application with zero external runtime dependencies.

### Automatic Setup via `render.yaml`
1. Push this repository to your GitHub account.
2. Sign in to **[Render](https://dashboard.render.com/)**.
3. Click **New +** $\rightarrow$ **Static Site**.
4. Select your repository: `Superrselectoranalysis`.
5. Set:
   - **Build Command:** *(leave empty or `echo "Ready"`)*
   - **Publish Directory:** `.` *(root)*
6. Click **Create Static Site** to get your live URL.

---

## 🛠️ Local Development & PDF Compilation

```bash
# Clone the repository
git clone https://github.com/NaniToka/Superrselectoranalysis.git
cd Superrselectoranalysis

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the integrity verification suite
python3 scripts/verify_project_integrity.py

# Recompile the 5-page Master Methodology Report PDF
python3 scripts/build_top1_report.py
```

---

<p align="center">
  <b>Rajasthan Royals SupeRR Selector Season 2</b> &bull; Built with precision for Round 1 &bull; <i>Halla Bol!</i>
</p>
