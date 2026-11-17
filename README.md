# SupeRR Selector Season 2 — RR Intelligence Platform

> **Rajasthan Royals SupeRR Selector Season 2 (Round 1 Submission)**  
> Quantitative Framework for Identifying the Most Reliable Players Under High Pressure (2022–2026).

---

## 🚀 Live Interactive Dashboard

The dashboard is designed for high-density talent evaluation, pressure telemetry, situational splits, and RR squad audit:
- **Hosted Live on Render:** [Deploy via Render Static Site]
- **Entry File:** `index.html` (Self-contained, responsive, high-performance UI)

---

## 📊 Methodology & Analytical Framework

Pressure is quantified using ball-by-ball **Win Probability Added (WPA)** and **Leverage Index (LI)**:
1. **High Pressure (HP) Definition:** Defined as deliveries in the top 25th percentile of Leverage Index ($\ge 75\text{th}$ percentile of match leverage).
2. **Composite Score:** Shrinkage-adjusted performance using Empirical Bayes across 4 core pillars:
   - **Net Value per 100 Balls ($Net_{100}$):** 35% weight
   - **Win Probability Added ($WPA$):** 30% weight
   - **High-Pressure Delta ($\Delta_{HP}$ vs non-HP):** 20% weight
   - **Consistency Index ($Cons$):** 15% weight
3. **Opposition Quality Adjustment:** Leave-One-Match-Out regression adjustments against opposing bowling/batting units.
4. **Uncertainty Quantification:** 300-resample bootstrap iterations and 7 sensitivity perturbation models.

---

## 🏆 Verified Top 10 Rankings

### Top 10 Batters Under Pressure
1. **Suryakumar Yadav** (Score: 0.843 | 697 HP balls | Net: +38.74 | Delta: +13.10 | WPA: +0.629 | Cons: 72.9%)
2. **Phil Salt** (Score: 0.771 | 339 HP balls | Net: +36.85 | Delta: +17.42 | WPA: +0.839 | Cons: 77.4%)
3. **Tim David** (Score: 0.457 | 419 HP balls | Net: +26.85 | Delta: -10.51 | WPA: +0.847 | Cons: 64.9%)
4. **Babar Azam** (Score: 0.438 | 220 HP balls | Net: +24.44 | Delta: +26.62 | WPA: +0.242 | Cons: 72.7%)
5. **Shubman Gill** (Score: 0.437 | 564 HP balls | Net: +15.31 | Delta: +6.22 | WPA: +0.310 | Cons: 72.3%)
6. **Nicholas Pooran** (Score: 0.412 | 575 HP balls | Net: +21.84 | Delta: +6.48 | WPA: +0.127 | Cons: 70.2%)
7. **Abhishek Sharma** (Score: 0.410 | 476 HP balls | Net: +24.34 | Delta: -14.38 | WPA: +0.494 | Cons: 67.5%)
8. **Vaibhav Sooryavanshi** (Score: 0.386 | 161 HP balls | Net: +75.76 | Delta: +7.89 | WPA: +1.209 | Cons: 55.6%)
9. **Fakhar Zaman** (Score: 0.343 | 217 HP balls | Net: +19.25 | Delta: +23.87 | WPA: +0.635 | Cons: 66.7%)
10. **Harry Brook** (Score: 0.322 | 193 HP balls | Net: +25.94 | Delta: +10.49 | WPA: +0.724 | Cons: 64.7%)

### Top 10 Bowlers Under Pressure
1. **Sunil Narine** (Score: 1.163 | 393 HP balls | Net: +37.20 | Delta: +19.01 | WPA: +1.355 | Cons: 69.0% | Econ: 6.51)
2. **Abrar Ahmed** (Score: 0.866 | 178 HP balls | Net: +42.26 | Delta: +26.40 | WPA: +0.898 | Cons: 72.2% | Econ: 6.14)
3. **Mitchell Santner** (Score: 0.818 | 409 HP balls | Net: +26.38 | Delta: +16.87 | WPA: +0.633 | Cons: 67.6% | Econ: 7.33)
4. **Jacob Duffy** (Score: 0.772 | 167 HP balls | Net: +60.05 | Delta: +59.32 | WPA: +0.533 | Cons: 61.1% | Econ: 8.29)
5. **Matheesha Pathirana** (Score: 0.727 | 315 HP balls | Net: +21.14 | Delta: -0.19 | WPA: +0.677 | Cons: 71.4% | Econ: 8.78)
6. **Lockie Ferguson** (Score: 0.679 | 247 HP balls | Net: +35.49 | Delta: +38.05 | WPA: +1.048 | Cons: 54.2% | Econ: 7.61)
7. **Taskin Ahmed** (Score: 0.641 | 239 HP balls | Net: +34.69 | Delta: +36.49 | WPA: +0.520 | Cons: 60.0% | Econ: 6.53)
8. **Josh Hazlewood** (Score: 0.596 | 398 HP balls | Net: +33.78 | Delta: +23.52 | WPA: +0.524 | Cons: 51.3% | Econ: 7.73)
9. **Mohit Sharma** (Score: 0.540 | 176 HP balls | Net: +24.96 | Delta: +38.51 | WPA: +0.802 | Cons: 60.0% | Econ: 8.64)
10. **Krunal Pandya** (Score: 0.537 | 340 HP balls | Net: +19.88 | Delta: +12.46 | WPA: +0.508 | Cons: 60.6% | Econ: 7.21)

---

## 🛠️ Verification & Quality Assurance

Run the automated verification suite to validate all 136 metric constraints across rankings, pressure thresholds, and squad audits:

```bash
python3 scripts/verify_project_integrity.py
# Output: 136 checks run. All integrity assertions passed.
```

---

## 🌐 Deploy to Render

### Option A: Automatic via Blueprint
1. Connect your repository to Render.
2. Render will automatically detect `render.yaml` and configure the static web service.

### Option B: Manual Static Site Setup
1. On Render Dashboard, click **New +** -> **Static Site**.
2. Connect `https://github.com/NaniToka/Superrselectoranalysis.git`.
3. Set:
   - **Build Command:** *(leave blank or `echo "Ready"`)*
   - **Publish Directory:** `.`
4. Click **Create Static Site**.

---

## 📄 Key Deliverables
- `outputs/SupeRR_Selector_Methodology_Report_v4_Top1.pdf`: Complete 5-Page Master Methodology Report with Rajasthan Royals design system and empirical findings.
- `index.html`: Interactive single-page dashboard with real-time pressure diagnostics, telemetry, and squad audit.
- `expected_dashboard_values.csv`: Exact verified benchmark data for Top 10 rankings.
- `rr_squad_pressure_audit.csv`: Pressure audit for all Rajasthan Royals contracted players.
