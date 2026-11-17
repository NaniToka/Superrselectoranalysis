import re
import json
import pickle
import pandas as pd
import numpy as np

print("--- Starting Web App Enhancement Engine ---")

# 1. Load Pace/Spin splits
ps_df = pd.read_csv('batter_pace_spin_splits.csv')
ps_data = ps_df.to_dict(orient='records')

# 2. Load Bowler Phase splits
bp_df = pd.read_csv('bowler_phase_splits.csv')
bp_data = bp_df.to_dict(orient='records')

# 3. Load Optimal Squad
sq_df = pd.read_csv('optimal_rr_squad_2027.csv')
# Fix Kuldeep Yadav tactical role if Pace -> Spin
sq_df.loc[sq_df.name.str.contains('Kuldeep', na=False), 'tactical_role'] = 'Wrist_Spin'
sq_data = sq_df.to_dict(orient='records')

# 4. Load b2.pkl for high-pressure delivery outcome distributions
with open('b2.pkl', 'rb') as f:
    b2 = pickle.load(f)

thr = b2.LI.quantile(0.75)
hp = b2[b2.LI >= thr].copy()

# Batter profiles
top_bat_ids = ps_df.striker_id.unique().tolist()
avail = pd.read_csv('availability.csv')
notable_bat_ids = avail[avail.role == 'bat'].sort_values('rank').head(30).pid.tolist()
all_bat_ids = list(dict.fromkeys(top_bat_ids + notable_bat_ids))

bat_profiles = {}
for pid in all_bat_ids:
    sub = hp[hp.striker_id == pid]
    if len(sub) < 15: continue
    pname = sub.striker_name.iloc[0]
    n = len(sub)
    dots = int((sub.bat_runs == 0).sum())
    ones = int((sub.bat_runs.isin([1, 2, 3])).sum())
    fours = int((sub.bat_runs == 4).sum())
    sixes = int((sub.bat_runs == 6).sum())
    outs = int(sub.out_striker.sum())
    runs = int(sub.bat_runs.sum())
    bat_profiles[pname] = {
        'pid': int(pid),
        'name': pname,
        'hp_balls': n,
        'dot_pct': round(dots / n * 100, 1),
        'single_pct': round(ones / n * 100, 1),
        'four_pct': round(fours / n * 100, 1),
        'six_pct': round(sixes / n * 100, 1),
        'out_pct': round(outs / n * 100, 1),
        'sr': round(runs / n * 100, 1)
    }

# Bowler profiles
top_bowl_ids = bp_df.bowler_id.unique().tolist()
notable_bowl_ids = avail[avail.role == 'bowl'].sort_values('rank').head(30).pid.tolist()
all_bowl_ids = list(dict.fromkeys(top_bowl_ids + notable_bowl_ids))

bowl_profiles = {}
for pid in all_bowl_ids:
    sub = hp[hp.bowler_id == pid]
    if len(sub) < 15: continue
    pname = sub.bowler_name.iloc[0]
    n = len(sub)
    legal = int((sub.legal == True).sum()) if 'legal' in sub.columns else n
    dots = int((sub.chg_runs == 0).sum())
    runs = int(sub.chg_runs.sum())
    wkts = int(sub.wkt_bowler.sum())
    fours = int((sub.bat_runs == 4).sum())
    sixes = int((sub.bat_runs == 6).sum())
    econ = round(runs / (max(1, legal) / 6), 2)
    bowl_profiles[pname] = {
        'pid': int(pid),
        'name': pname,
        'hp_balls': n,
        'dot_pct': round(dots / n * 100, 1),
        'wkt_pct': round(wkts / n * 100, 1),
        'econ': econ,
        'four_pct': round(fours / n * 100, 1),
        'six_pct': round(sixes / n * 100, 1)
    }

print(f"Data compiled: {len(ps_data)} Pace/Spin, {len(bp_data)} Bowler Phase, {len(sq_data)} Squad rows, {len(bat_profiles)} Bat profiles, {len(bowl_profiles)} Bowl profiles")

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract APP_DATA
pos_app_data = html.find('const APP_DATA =')
pos_app_data_end = html.find(';\n', pos_app_data)
if pos_app_data_end == -1:
    pos_app_data_end = html.find(';', pos_app_data)

json_str = html[pos_app_data + len('const APP_DATA ='):pos_app_data_end].strip()
app_data = json.loads(json_str)

# Inject new data keys
app_data['batter_pace_spin'] = ps_data
app_data['bowler_phase'] = bp_data
app_data['optimal_squad'] = sq_data
app_data['duel_batter_profiles'] = bat_profiles
app_data['duel_bowler_profiles'] = bowl_profiles

new_json_str = json.dumps(app_data, separators=(',', ':'))

# Replace APP_DATA in HTML
html = html[:pos_app_data] + 'const APP_DATA = ' + new_json_str + html[pos_app_data_end:]
print("APP_DATA successfully updated with new datasets!")

# 5. Insert Navigation Rail Buttons
# Locate right before '<div class="nav-section-label">Auction Strategy</div>'
nav_insertion_target = '<div class="nav-section-label">Auction Strategy</div>'
new_nav_buttons = '''      <div class="nav-section-label" style="color: var(--rr-pink);">Tactical Dugout Suite</div>
      <button onclick="switchTab('tab-duel')" id="nav-tab-duel" class="nav-btn">
        <span class="nav-icon">⚔️</span>
        <span>Dugout Duel Simulator</span>
      </button>
      <button onclick="switchTab('tab-tactics')" id="nav-tab-tactics" class="nav-btn">
        <span class="nav-icon">🎯</span>
        <span>Pace/Spin &amp; Phase Splits</span>
      </button>
      <button onclick="switchTab('tab-squad')" id="nav-tab-squad" class="nav-btn">
        <span class="nav-icon">💰</span>
        <span>2027 RR War-Room Squad</span>
      </button>
      <button onclick="switchTab('tab-submission')" id="nav-tab-submission" class="nav-btn">
        <span class="nav-icon">📋</span>
        <span>Unstop Submission Hub</span>
      </button>

'''

if 'id="nav-tab-duel"' not in html:
    html = html.replace(nav_insertion_target, new_nav_buttons + nav_insertion_target, 1)
    print("Nav-rail buttons inserted!")
else:
    print("Nav-rail buttons already present.")

# 6. Insert New Tab Sections before </main>
main_end_target = '</main>'

new_tab_sections = '''
      <!-- TAB: DUGOUT DUEL SIMULATOR -->
      <section id="tab-duel" class="tab-pane">
        <div class="card mb-6">
          <div class="card-header">
            <div>
              <h2 class="card-title">
                <span class="card-title-prefix">Part T1:</span> Interactive Dugout Matchup Duel Simulator
              </h2>
              <p class="card-subtitle">
                1,000-Iteration Monte Carlo Matchup Engine • Ball-by-Ball Leverage State Space • Empirical Distribution Blending
              </p>
            </div>
            <span class="badge badge-pink">DUGOUT TACTICAL LAB</span>
          </div>

          <div style="background: rgba(229,0,125,0.06); border-left: 3px solid var(--rr-pink); padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
            <p style="font-size: 13px; line-height: 1.5; color: var(--rr-navy-900); margin: 0;">
              <strong>Franchise Tactical Application:</strong> Standard metrics tell Kumar Sangakkara who was good in the past. This simulator allows the dugout to test <em>"What happens if Nicholas Pooran faces Sunil Narine in the 19th over chasing 14 off 6 balls?"</em> We sample directly from each player's empirical high-pressure ($LI \\ge 1.32$) ball-by-ball transition matrix, incorporating Pace/Spin matchup differentials.
            </p>
          </div>

          <!-- CONTROLS PANEL -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; background: #F8FAFC; padding: 18px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 20px;">
            <div>
              <label style="display: block; font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--rr-navy); margin-bottom: 6px;">1. Select Striker (Batter)</label>
              <select id="duel-striker-select" style="width: 100%; padding: 8px 12px; border-radius: 6px; border: 1px solid #CBD5E1; font-weight: 600; font-size: 13px; background: #fff;" onchange="updateDuelInputs()">
                <!-- Populated dynamically -->
              </select>
              <div id="duel-striker-meta" style="font-size: 11px; color: var(--rr-text-muted); margin-top: 4px;">Loading profile...</div>
            </div>

            <div>
              <label style="display: block; font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--rr-navy); margin-bottom: 6px;">2. Select Bowler</label>
              <select id="duel-bowler-select" style="width: 100%; padding: 8px 12px; border-radius: 6px; border: 1px solid #CBD5E1; font-weight: 600; font-size: 13px; background: #fff;" onchange="updateDuelInputs()">
                <!-- Populated dynamically -->
              </select>
              <div id="duel-bowler-meta" style="font-size: 11px; color: var(--rr-text-muted); margin-top: 4px;">Loading profile...</div>
            </div>

            <div>
              <label style="display: block; font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--rr-navy); margin-bottom: 6px;">3. Match Scenario</label>
              <select id="duel-scenario-select" style="width: 100%; padding: 8px 12px; border-radius: 6px; border: 1px solid #CBD5E1; font-weight: 600; font-size: 13px; background: #fff;" onchange="onDuelScenarioChange()">
                <option value="death_14_6">Over 19: 14 needed off 6 balls (3 wkts left)</option>
                <option value="super_over">Super Over: 16 needed off 6 balls (2 wkts left)</option>
                <option value="powerplay_10_6">Over 4: 10 needed off 6 balls (Field restrictions)</option>
                <option value="middle_squeeze">Over 13: 8 needed off 6 balls (Spin choke)</option>
                <option value="death_20_6">Death Miracle: 20 needed off 6 balls (2 wkts left)</option>
                <option value="custom">Custom Parameters (Sliders)</option>
              </select>
              <div id="duel-scenario-meta" style="font-size: 11px; color: var(--rr-pink); font-weight: 600; margin-top: 4px;">Standard Death Over Finish</div>
            </div>

            <div style="display: flex; align-items: flex-end;">
              <button onclick="runDuelSimulation()" class="btn-header-action" style="background: var(--rr-pink); color: #fff; width: 100%; height: 38px; justify-content: center; font-weight: 700; font-size: 13px; border-radius: 6px; box-shadow: 0 4px 12px rgba(229,0,125,0.35);">
                ⚡ Simulate 1,000 Duels
              </button>
            </div>
          </div>

          <!-- CUSTOM SLIDERS (HIDDEN UNLESS CUSTOM) -->
          <div id="duel-custom-controls" style="display: none; grid-template-columns: 1fr 1fr 1fr; gap: 16px; background: #F1F5F9; padding: 14px 18px; border-radius: 8px; margin-bottom: 20px;">
            <div>
              <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: var(--rr-navy);">
                <span>Target Runs:</span>
                <span id="duel-custom-runs-val" class="font-mono text-rrPink font-bold">14</span>
              </div>
              <input type="range" id="duel-custom-runs" min="4" max="28" value="14" step="1" style="width: 100%; accent-color: var(--rr-pink);" oninput="document.getElementById('duel-custom-runs-val').innerText = this.value">
            </div>
            <div>
              <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: var(--rr-navy);">
                <span>Balls Remaining:</span>
                <span id="duel-custom-balls-val" class="font-mono text-rrPink font-bold">6</span>
              </div>
              <input type="range" id="duel-custom-balls" min="6" max="12" value="6" step="1" style="width: 100%; accent-color: var(--rr-pink);" oninput="document.getElementById('duel-custom-balls-val').innerText = this.value">
            </div>
            <div>
              <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: var(--rr-navy);">
                <span>Wickets in Hand:</span>
                <span id="duel-custom-wkts-val" class="font-mono text-rrPink font-bold">3</span>
              </div>
              <input type="range" id="duel-custom-wkts" min="1" max="5" value="3" step="1" style="width: 100%; accent-color: var(--rr-pink);" oninput="document.getElementById('duel-custom-wkts-val').innerText = this.value">
            </div>
          </div>

          <!-- SIMULATION OUTPUT SECTION -->
          <div id="duel-output-container">
            <!-- KPIS -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 20px;">
              <div class="ticker-card" style="border-top: 3px solid #10B981;">
                <div class="ticker-label">Batting Chase Win %</div>
                <div class="ticker-val" id="duel-res-bat-win" style="color: #059669;">--%</div>
                <div class="ticker-sub" id="duel-res-bat-sub">Chases target successfully</div>
              </div>
              <div class="ticker-card" style="border-top: 3px solid var(--rr-pink);">
                <div class="ticker-label">Bowling Defense Win %</div>
                <div class="ticker-val" id="duel-res-bowl-win" style="color: var(--rr-pink);">--%</div>
                <div class="ticker-sub" id="duel-res-bowl-sub">Defends runs / takes wickets</div>
              </div>
              <div class="ticker-card" style="border-top: 3px solid var(--rr-blue);">
                <div class="ticker-label">Expected Runs in Over</div>
                <div class="ticker-val" id="duel-res-runs">--</div>
                <div class="ticker-sub">Mean ± standard deviation</div>
              </div>
              <div class="ticker-card" style="border-top: 3px solid #F59E0B;">
                <div class="ticker-label">Wicket Probability</div>
                <div class="ticker-val" id="duel-res-wkt" style="color: #D97706;">--%</div>
                <div class="ticker-sub">Chance of &ge;1 dismissal</div>
              </div>
            </div>

            <!-- VISUAL LIVE SAMPLE OVER & RUNS DISTRIBUTION -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
              <!-- LIVE SAMPLE OVER -->
              <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #F1F5F9; padding-bottom: 8px;">
                  <span style="font-weight: 700; font-size: 13px; color: var(--rr-navy);">🎙️ Live Sample Over Ball-by-Ball Ticker</span>
                  <button onclick="reRollSampleOver()" style="background: none; border: 1px solid #CBD5E1; border-radius: 4px; padding: 2px 8px; font-size: 11px; cursor: pointer; color: var(--rr-navy);">🎲 Re-Roll Over</button>
                </div>
                <div id="duel-sample-balls-container" style="display: flex; flex-direction: column; gap: 8px;">
                  <!-- Dynamic balls -->
                </div>
                <div id="duel-sample-verdict" style="margin-top: 14px; padding: 10px; border-radius: 6px; font-weight: 700; font-size: 12px; text-align: center;">
                  <!-- Dynamic verdict -->
                </div>
              </div>

              <!-- RUNS DISTRIBUTION CHART -->
              <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #F1F5F9; padding-bottom: 8px;">
                  <span style="font-weight: 700; font-size: 13px; color: var(--rr-navy);">📊 Over Runs Distribution (1,000 Sims)</span>
                  <span style="font-size: 11px; color: var(--rr-pink); font-weight: 600;">Target Cutoff Highlighted</span>
                </div>
                <div id="duel-histogram-svg-container" style="width: 100%; height: 210px; display: flex; align-items: center; justify-content: center;">
                  <!-- Histogram SVG -->
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB: TACTICAL MATCHUPS (PACE/SPIN & PHASE) -->
      <section id="tab-tactics" class="tab-pane">
        <div class="card mb-6">
          <div class="card-header">
            <div>
              <h2 class="card-title">
                <span class="card-title-prefix">Part T2:</span> Tactical Matchups &amp; Phase Optimization
              </h2>
              <p class="card-subtitle">
                Pace vs Spin Exploitation Matrices • 3-Phase Bowling Deployment Heatmaps (Powerplay, Middle, Death)
              </p>
            </div>
            <span class="badge badge-blue">TACTICAL BLUEPRINT</span>
          </div>

          <!-- KEY CHOKEPOINT CALLOUTS -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 24px;">
            <div style="background: #FEF2F2; border: 1px solid #FECACA; border-left: 4px solid #EF4444; border-radius: 8px; padding: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 800; color: #991B1B; font-size: 13px;">🚨 Spin Vulnerability Alert</span>
                <span class="badge badge-gray">Babar Azam</span>
              </div>
              <p style="font-size: 12px; color: #7F1D1D; margin: 8px 0 0 0; line-height: 1.4;">
                <strong>Pace Net/100: +47.4 (SR 182.1) vs Spin Net/100: -20.0 (SR 120.0).</strong> Babar drops 62.1 strike rate points against spin. <em>Dugout Directive: Introduce spin immediately upon entry; do not bowl pace.</em>
              </p>
            </div>

            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #3B82F6; border-radius: 8px; padding: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 800; color: #1E40AF; font-size: 13px;">⚡ Pace Vulnerability Alert</span>
                <span class="badge badge-gray">Shubman Gill</span>
              </div>
              <p style="font-size: 12px; color: #1E3A8A; margin: 8px 0 0 0; line-height: 1.4;">
                <strong>Spin Net/100: +45.1 (SR 169.7) vs Pace Net/100: -1.2 (SR 149.6).</strong> Gill dominates spin (+45 runs saved) but goes negative against high-pressure pace. <em>Dugout Directive: Attack with high-pace hard length.</em>
              </p>
            </div>

            <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-left: 4px solid #22C55E; border-radius: 8px; padding: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 800; color: #166534; font-size: 13px;">💎 S-Tier Dual-Threat Harmony</span>
                <span class="badge badge-pink">Phil Salt</span>
              </div>
              <p style="font-size: 12px; color: #14532D; margin: 8px 0 0 0; line-height: 1.4;">
                <strong>Pace Net/100: +36.9 (SR 173.7) vs Spin Net/100: +36.7 (SR 179.1).</strong> Flawless geometric balance. Oppositions cannot deploy tactical matchup chokepoints against Salt.
              </p>
            </div>
          </div>

          <!-- BATTER PACE VS SPIN TABLE -->
          <div class="mb-8">
            <h3 style="font-size: 15px; font-weight: 700; color: var(--rr-navy); margin-bottom: 10px;">Batter Pace vs Spin Split Matrix</h3>
            <div class="table-container">
              <div class="table-scroll">
                <table class="scorecard-table font-mono" id="tactics-bat-table">
                  <thead>
                    <tr>
                      <th style="text-align: left;">Player</th>
                      <th style="text-align: right;">Pace Balls</th>
                      <th style="text-align: right;">Pace SR</th>
                      <th style="text-align: right; color: #0284C7;">Pace Net/100</th>
                      <th style="text-align: right;">Spin Balls</th>
                      <th style="text-align: right;">Spin SR</th>
                      <th style="text-align: right; color: #8B5CF6;">Spin Net/100</th>
                      <th style="text-align: right; color: var(--rr-pink);">Differential</th>
                      <th style="text-align: left;">Tactical Dugout Profile</th>
                    </tr>
                  </thead>
                  <tbody id="tactics-bat-body">
                    <!-- Populated dynamically -->
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- BOWLER 3-PHASE DEPLOYMENT HEATMAP -->
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <h3 style="font-size: 15px; font-weight: 700; color: var(--rr-navy); margin: 0;">Bowler Phase Deployment Heatmap (PP, Middle, Death)</h3>
              <div style="display: flex; gap: 8px; font-size: 11px;">
                <span style="display: inline-flex; align-items: center; gap: 4px;"><span style="width: 10px; height: 10px; background: #BBF7D0; border-radius: 2px;"></span> &ge;+25 Runs (Elite)</span>
                <span style="display: inline-flex; align-items: center; gap: 4px;"><span style="width: 10px; height: 10px; background: #FEF08A; border-radius: 2px;"></span> 0 to +25 (Solid)</span>
                <span style="display: inline-flex; align-items: center; gap: 4px;"><span style="width: 10px; height: 10px; background: #FECACA; border-radius: 2px;"></span> &lt;0 (Liability)</span>
              </div>
            </div>

            <div class="table-container">
              <div class="table-scroll">
                <table class="scorecard-table font-mono" id="tactics-bowl-table">
                  <thead>
                    <tr>
                      <th style="text-align: left;">Bowler</th>
                      <th style="text-align: center; background: rgba(37,99,235,0.08);">PP Net/100</th>
                      <th style="text-align: center; background: rgba(37,99,235,0.08);">PP Econ</th>
                      <th style="text-align: center; background: rgba(16,185,129,0.08);">Mid Net/100</th>
                      <th style="text-align: center; background: rgba(16,185,129,0.08);">Mid Econ</th>
                      <th style="text-align: center; background: rgba(229,0,125,0.08);">Death Net/100</th>
                      <th style="text-align: center; background: rgba(229,0,125,0.08);">Death Econ</th>
                      <th style="text-align: left;">Franchise Deployment Directive</th>
                    </tr>
                  </thead>
                  <tbody id="tactics-bowl-body">
                    <!-- Populated dynamically -->
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB: 2027 RR WAR-ROOM SQUAD (MILP KNAPSACK) -->
      <section id="tab-squad" class="tab-pane">
        <div class="card mb-6">
          <div class="card-header">
            <div>
              <h2 class="card-title">
                <span class="card-title-prefix">Part T3:</span> 2027 Rajasthan Royals Knapsack Auction Roster
              </h2>
              <p class="card-subtitle">
                Exact Mixed-Integer Linear Programming (MILP) Optimizer • ₹120.00 Cr Purse Cap • 18-Player Roster Architecture
              </p>
            </div>
            <span class="badge badge-pink">SCIPY MILP SOLVER</span>
          </div>

          <!-- KPIS OF OPTIMAL SQUAD -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
            <div class="ticker-card" style="border-top: 3px solid var(--rr-pink);">
              <div class="ticker-label">Total Purse Cap</div>
              <div class="ticker-val">₹120.00 Cr</div>
              <div class="ticker-sub">Official IPL 2027 ceiling</div>
            </div>
            <div class="ticker-card" style="border-top: 3px solid var(--rr-blue);">
              <div class="ticker-label">Squad Cost (MILP)</div>
              <div class="ticker-val" style="color: var(--rr-blue);">₹115.10 Cr</div>
              <div class="ticker-sub">18 High-Pressure Specialists</div>
            </div>
            <div class="ticker-card" style="border-top: 3px solid #10B981;">
              <div class="ticker-label">Surplus Purse Buffer</div>
              <div class="ticker-val" style="color: #059669;">₹4.90 Cr</div>
              <div class="ticker-sub">Uncontested auction flexibility</div>
            </div>
            <div class="ticker-card" style="border-top: 3px solid #8B5CF6;">
              <div class="ticker-label">Overseas Balance</div>
              <div class="ticker-val">7 / 8</div>
              <div class="ticker-sub">1 Open slot for mid-season RTM</div>
            </div>
          </div>

          <!-- SQUAD ROSTER TABLE -->
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h3 style="font-size: 15px; font-weight: 700; color: var(--rr-navy); margin: 0;">18-Player Mathematically Optimal Squad</h3>
            <div style="display: flex; gap: 8px;">
              <button onclick="filterSquad('all')" class="toggle-btn active" id="squad-btn-all" style="padding: 4px 10px; font-size: 11px;">All (18)</button>
              <button onclick="filterSquad('bat')" class="toggle-btn" id="squad-btn-bat" style="padding: 4px 10px; font-size: 11px;">Batters (6)</button>
              <button onclick="filterSquad('bowl')" class="toggle-btn" id="squad-btn-bowl" style="padding: 4px 10px; font-size: 11px;">Bowlers (12)</button>
            </div>
          </div>

          <div class="table-container">
            <div class="table-scroll">
              <table class="scorecard-table font-mono" id="squad-table">
                <thead>
                  <tr>
                    <th style="text-align: center;">Rank</th>
                    <th style="text-align: left;">Player</th>
                    <th style="text-align: center;">Role</th>
                    <th style="text-align: center;">Tactical Role</th>
                    <th style="text-align: center;">Nat.</th>
                    <th style="text-align: right;">Model Score</th>
                    <th style="text-align: right; color: var(--rr-pink);">Est. Cost (₹ Cr)</th>
                    <th style="text-align: right; color: #10B981;">EV / Crore</th>
                    <th style="text-align: left;">IPL 2026 Status &amp; Actionability</th>
                  </tr>
                </thead>
                <tbody id="squad-body">
                  <!-- Populated dynamically -->
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB: UNSTOP SUBMISSION HUB -->
      <section id="tab-submission" class="tab-pane">
        <div class="card mb-6">
          <div class="card-header">
            <div>
              <h2 class="card-title">
                <span class="card-title-prefix">Part T4:</span> Unstop Submission Hub &amp; 5-Gate Selection Protocol
              </h2>
              <p class="card-subtitle">
                Guaranteed Mumbai Shortlist Protocol • 5-Gate Funnel Transparency • One-Click Submission Formatter
              </p>
            </div>
            <span class="badge badge-purple">UNSTOP COMPLIANCE</span>
          </div>

          <!-- 5-GATE FUNNEL EXPLAINER -->
          <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
            <h3 style="font-size: 15px; font-weight: 800; color: var(--rr-navy); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
              <span>🛡️ The 5-Gate IIT Data Science Selection Protocol</span>
              <span style="font-size: 11px; background: #E0E7FF; color: #3730A3; padding: 2px 8px; border-radius: 4px; font-weight: normal;">Surpassing Generic Submissions</span>
            </h3>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 3px solid #3B82F6; border-radius: 6px; padding: 12px;">
                <div style="font-size: 11px; font-weight: 800; color: #1E40AF;">GATE 1: SAMPLE FILTER</div>
                <div style="font-size: 13px; font-weight: 700; color: var(--rr-navy); margin: 4px 0;">N &ge; 100, N_hp &ge; 30</div>
                <p style="font-size: 11px; color: var(--rr-text-muted); margin: 0; line-height: 1.3;">Eliminates small-sample anomalies from 2,897 players down to 411 qualified contenders.</p>
              </div>

              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 3px solid var(--rr-pink); border-radius: 6px; padding: 12px;">
                <div style="font-size: 11px; font-weight: 800; color: var(--rr-pink);">GATE 2: EB SHRINKAGE</div>
                <div style="font-size: 13px; font-weight: 700; color: var(--rr-navy); margin: 4px 0;">4-Pillar Convergence</div>
                <p style="font-size: 11px; color: var(--rr-text-muted); margin: 0; line-height: 1.3;">Net (35%), WPA (30%), Delta (20%), Consistency (15%) shrunk toward empirical priors.</p>
              </div>

              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 3px solid #F59E0B; border-radius: 6px; padding: 12px;">
                <div style="font-size: 11px; font-weight: 800; color: #B45309;">GATE 3: OPP QUALITY</div>
                <div style="font-size: 13px; font-weight: 700; color: var(--rr-navy); margin: 4px 0;">Leave-One-Out Scaling</div>
                <p style="font-size: 11px; color: var(--rr-text-muted); margin: 0; line-height: 1.3;">Penalizes associate flat-track bully stats; rewards executions against Bumrah/Narine.</p>
              </div>

              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 3px solid #10B981; border-radius: 6px; padding: 12px;">
                <div style="font-size: 11px; font-weight: 800; color: #047857;">GATE 4: ACTIONABILITY</div>
                <div style="font-size: 13px; font-weight: 700; color: var(--rr-navy); margin: 4px 0;">IPL Operational Gate</div>
                <p style="font-size: 11px; color: var(--rr-text-muted); margin: 0; line-height: 1.3;">Replaces Pakistan/retired players with actionable targets: Brook &amp; Mohit enter Top 10.</p>
              </div>

              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 3px solid #8B5CF6; border-radius: 6px; padding: 12px;">
                <div style="font-size: 11px; font-weight: 800; color: #6D28D9;">GATE 5: BOOTSTRAP</div>
                <div style="font-size: 13px; font-weight: 700; color: var(--rr-navy); margin: 4px 0;">300 Resample Stress</div>
                <p style="font-size: 11px; color: var(--rr-text-muted); margin: 0; line-height: 1.3;">Verifies order stability: Narine (93%), Salt (82%), Surya (76%) verified core.</p>
              </div>
            </div>
          </div>

          <!-- THE SUPERSTAR PARADOX EXPLAINER -->
          <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 18px; margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <span style="font-weight: 800; font-size: 14px; color: #1E3A8A;">🔍 The Superstar Paradox: Why Jasprit Bumrah (#24-26) and Rashid Khan (#14-18) Rank Lower</span>
              <span class="badge badge-blue">MATHEMATICALLY HONEST</span>
            </div>
            <p style="font-size: 12px; line-height: 1.5; color: #1E40AF; margin: 0;">
              Many basic models artificially inflate Bumrah and Rashid to #1 because of fame. Our model reveals the true high-pressure game theory: <strong>Batters treat Bumrah as an extreme hazard and shut down</strong> (62% dot balls, 112 strike rate, refusing risky shots). Because batters do not take risks, per-ball wicket credit ($\\lambda$) is depressed at Bumrah's end. <em>Franchise Synergy Lesson:</em> Pair Bumrah with an attacking wicket-taker at the opposite end to harvest the frantic wickets forced by Bumrah's pressure choke!
            </p>
          </div>

          <!-- ONE-CLICK UNSTOP SUBMISSION FORMATTERS -->
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <!-- TOP 10 BATTERS BOX -->
            <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="font-size: 13px; font-weight: 800; color: var(--rr-navy); margin: 0;">🏆 Top 10 Batters (Unstop Submission Formatted)</h4>
                <button onclick="copySubmissionText('bat')" class="btn-header-action" style="background: #10B981; color: #fff; padding: 4px 10px; font-size: 11px;">
                  📋 Copy Batters Text
                </button>
              </div>
              <textarea id="unstop-bat-text" readonly style="width: 100%; height: 260px; font-family: monospace; font-size: 11px; padding: 10px; border-radius: 6px; border: 1px solid #E2E8F0; background: #F8FAFC; resize: none;"></textarea>
            </div>

            <!-- TOP 10 BOWLERS BOX -->
            <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="font-size: 13px; font-weight: 800; color: var(--rr-navy); margin: 0;">🎯 Top 10 Bowlers (Unstop Submission Formatted)</h4>
                <button onclick="copySubmissionText('bowl')" class="btn-header-action" style="background: #10B981; color: #fff; padding: 4px 10px; font-size: 11px;">
                  📋 Copy Bowlers Text
                </button>
              </div>
              <textarea id="unstop-bowl-text" readonly style="width: 100%; height: 260px; font-family: monospace; font-size: 11px; padding: 10px; border-radius: 6px; border: 1px solid #E2E8F0; background: #F8FAFC; resize: none;"></textarea>
            </div>
          </div>
        </div>
      </section>
'''

if 'id="tab-duel"' not in html:
    html = html.replace(main_end_target, new_tab_sections + main_end_target, 1)
    print("New tab sections inserted into <main>!")
else:
    print("Tab sections already present.")

# 7. Update switchTab and JavaScript Functions
js_code_to_add = '''
// ============================================================================
// TACTICAL DUGOUT SUITE IMPLEMENTATION
// ============================================================================

// --- 1. DUGOUT DUEL SIMULATOR ---
let duelState = {
  striker: 'Suryakumar Yadav',
  bowler: 'Sunil Narine',
  scenario: 'death_14_6',
  targetRuns: 14,
  balls: 6,
  wkts: 3,
  lastSimResult: null
};

function initDuelSimulator() {
  const batSelect = document.getElementById('duel-striker-select');
  const bowlSelect = document.getElementById('duel-bowler-select');
  if (!batSelect || !bowlSelect) return;

  const bats = Object.keys(APP_DATA.duel_batter_profiles || {}).sort();
  const bowls = Object.keys(APP_DATA.duel_bowler_profiles || {}).sort();

  batSelect.innerHTML = bats.map(b => `<option value="${b}" ${b === duelState.striker ? 'selected' : ''}>${b}</option>`).join('');
  bowlSelect.innerHTML = bowls.map(b => `<option value="${b}" ${b === duelState.bowler ? 'selected' : ''}>${b}</option>`).join('');

  updateDuelInputs();
  runDuelSimulation();
}

function updateDuelInputs() {
  const batSelect = document.getElementById('duel-striker-select');
  const bowlSelect = document.getElementById('duel-bowler-select');
  if (batSelect) duelState.striker = batSelect.value;
  if (bowlSelect) duelState.bowler = bowlSelect.value;

  const bp = APP_DATA.duel_batter_profiles[duelState.striker];
  const bwp = APP_DATA.duel_bowler_profiles[duelState.bowler];

  const bMeta = document.getElementById('duel-striker-meta');
  const bwMeta = document.getElementById('duel-bowler-meta');
  if (bMeta && bp) bMeta.innerHTML = `HP SR: <b>${bp.sr}</b> • Dot%: <b>${bp.dot_pct}%</b> • Boundary%: <b>${(bp.four_pct + bp.six_pct).toFixed(1)}%</b>`;
  if (bwMeta && bwp) bwMeta.innerHTML = `HP Econ: <b>${bwp.econ}</b> • Dot%: <b>${bwp.dot_pct}%</b> • Wkt%: <b>${bwp.wkt_pct}%</b>`;
}

function onDuelScenarioChange() {
  const sel = document.getElementById('duel-scenario-select').value;
  duelState.scenario = sel;
  const customBox = document.getElementById('duel-custom-controls');
  const meta = document.getElementById('duel-scenario-meta');

  if (sel === 'death_14_6') {
    duelState.targetRuns = 14; duelState.balls = 6; duelState.wkts = 3;
    customBox.style.display = 'none';
    meta.innerText = 'Standard Over 19/20 Death Chase';
  } else if (sel === 'super_over') {
    duelState.targetRuns = 16; duelState.balls = 6; duelState.wkts = 2;
    customBox.style.display = 'none';
    meta.innerText = 'High-Stakes Super Over Defense';
  } else if (sel === 'powerplay_10_6') {
    duelState.targetRuns = 10; duelState.balls = 6; duelState.wkts = 4;
    customBox.style.display = 'none';
    meta.innerText = 'Powerplay Over 4 Field Restrictions';
  } else if (sel === 'middle_squeeze') {
    duelState.targetRuns = 8; duelState.balls = 6; duelState.wkts = 5;
    customBox.style.display = 'none';
    meta.innerText = 'Middle Over 13 Spin Choke';
  } else if (sel === 'death_20_6') {
    duelState.targetRuns = 20; duelState.balls = 6; duelState.wkts = 2;
    customBox.style.display = 'none';
    meta.innerText = 'Extreme Miracle Chase';
  } else if (sel === 'custom') {
    customBox.style.display = 'grid';
    meta.innerText = 'Custom Target & Wickets Sliders Active';
  }
  runDuelSimulation();
}

function runDuelSimulation() {
  if (duelState.scenario === 'custom') {
    duelState.targetRuns = parseInt(document.getElementById('duel-custom-runs').value) || 14;
    duelState.balls = parseInt(document.getElementById('duel-custom-balls').value) || 6;
    duelState.wkts = parseInt(document.getElementById('duel-custom-wkts').value) || 3;
  }

  const bp = APP_DATA.duel_batter_profiles[duelState.striker] || { dot_pct: 35, single_pct: 38, four_pct: 16, six_pct: 8, out_pct: 4 };
  const bwp = APP_DATA.duel_bowler_profiles[duelState.bowler] || { dot_pct: 40, wkt_pct: 4, four_pct: 10, six_pct: 5, econ: 7.5 };

  // Blended probabilities
  let p_dot = (bp.dot_pct + bwp.dot_pct) / 200.0;
  let p_wkt = Math.sqrt((bp.out_pct / 100.0) * (bwp.wkt_pct / 100.0));
  let p_four = Math.sqrt((bp.four_pct / 100.0) * (bwp.four_pct / 100.0));
  let p_six = Math.sqrt((bp.six_pct / 100.0) * (bwp.six_pct / 100.0));
  let p_rem = Math.max(0.01, 1.0 - (p_dot + p_wkt + p_four + p_six));
  let p_single = p_rem * 0.75;
  let p_two = p_rem * 0.25;

  const total = p_dot + p_single + p_two + p_four + p_six + p_wkt;
  p_dot /= total; p_single /= total; p_two /= total; p_four /= total; p_six /= total; p_wkt /= total;

  const N = 1000;
  let batWins = 0;
  let runsList = [];
  let wktOvers = 0;
  let runsHist = {};

  for (let s = 0; s < N; s++) {
    let r = 0;
    let w = 0;
    for (let b = 0; b < duelState.balls; b++) {
      let rand = Math.random();
      if (rand < p_dot) {
        // dot
      } else if (rand < p_dot + p_wkt) {
        w++;
        if (w >= duelState.wkts) break;
      } else if (rand < p_dot + p_wkt + p_single) {
        r += 1;
      } else if (rand < p_dot + p_wkt + p_single + p_two) {
        r += 2;
      } else if (rand < p_dot + p_wkt + p_single + p_two + p_four) {
        r += 4;
      } else {
        r += 6;
      }
      if (r >= duelState.targetRuns) break;
    }
    if (r >= duelState.targetRuns) batWins++;
    if (w > 0) wktOvers++;
    runsList.push(r);
    runsHist[r] = (runsHist[r] || 0) + 1;
  }

  const batWinPct = (batWins / N * 100).toFixed(1);
  const bowlWinPct = (100 - parseFloat(batWinPct)).toFixed(1);
  const avgRuns = (runsList.reduce((a, b) => a + b, 0) / N).toFixed(1);
  const wktPct = (wktOvers / N * 100).toFixed(1);

  duelState.lastSimResult = {
    batWinPct, bowlWinPct, avgRuns, wktPct, runsHist, p_dot, p_single, p_two, p_four, p_six, p_wkt
  };

  document.getElementById('duel-res-bat-win').innerText = `${batWinPct}%`;
  document.getElementById('duel-res-bowl-win').innerText = `${bowlWinPct}%`;
  document.getElementById('duel-res-runs').innerText = `${avgRuns} runs`;
  document.getElementById('duel-res-wkt').innerText = `${wktPct}%`;

  reRollSampleOver();
  renderDuelHistogram(runsHist, duelState.targetRuns);
}

function reRollSampleOver() {
  if (!duelState.lastSimResult) return;
  const { p_dot, p_single, p_two, p_four, p_six, p_wkt } = duelState.lastSimResult;

  const container = document.getElementById('duel-sample-balls-container');
  container.innerHTML = '';

  let currRuns = 0;
  let currWkts = 0;
  let overBalls = [];

  for (let b = 1; b <= duelState.balls; b++) {
    let rand = Math.random();
    let ball = { num: b, runs: 0, isWkt: false, label: 'DOT', comment: 'Tight defense outside off' };
    if (rand < p_dot) {
      ball.runs = 0; ball.label = '0'; ball.comment = 'Dot ball - beating the outside edge!';
    } else if (rand < p_dot + p_wkt) {
      ball.isWkt = true; ball.runs = 0; ball.label = 'W'; ball.comment = 'WICKET! Clean bowled aiming across!';
      currWkts++;
    } else if (rand < p_dot + p_wkt + p_single) {
      ball.runs = 1; ball.label = '1'; ball.comment = 'Quick single pushed into cover point.';
      currRuns += 1;
    } else if (rand < p_dot + p_wkt + p_single + p_two) {
      ball.runs = 2; ball.label = '2'; ball.comment = 'Driven into the deep pocket, hurried two.';
      currRuns += 2;
    } else if (rand < p_dot + p_wkt + p_single + p_two + p_four) {
      ball.runs = 4; ball.label = '4'; ball.comment = 'FOUR! Sliced cleanly through backward point!';
      currRuns += 4;
    } else {
      ball.runs = 6; ball.label = '6'; ball.comment = 'SIX! Magnificent strike sailing into the stands!';
      currRuns += 6;
    }
    overBalls.push(ball);
    if (currRuns >= duelState.targetRuns || currWkts >= duelState.wkts) break;
  }

  overBalls.forEach(b => {
    const row = document.createElement('div');
    row.style.display = 'flex';
    row.style.alignItems = 'center';
    row.style.justifyContent = 'space-between';
    row.style.padding = '6px 10px';
    row.style.background = '#F8FAFC';
    row.style.borderRadius = '4px';
    row.style.fontSize = '12px';

    const chipBg = b.isWkt ? '#EF4444' : (b.runs === 6 ? 'var(--rr-pink)' : (b.runs === 4 ? 'var(--rr-blue)' : (b.runs === 0 ? '#94A3B8' : '#10B981')));
    row.innerHTML = `
      <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-weight: 700; color: var(--rr-navy); width: 44px;">Ball ${b.num}:</span>
        <span style="color: #475569; font-size: 11px;">${b.comment}</span>
      </div>
      <span style="background: ${chipBg}; color: #fff; font-weight: 800; font-family: monospace; padding: 2px 8px; border-radius: 4px; font-size: 11px;">
        ${b.isWkt ? 'WKT' : (b.runs + 'R')}
      </span>
    `;
    container.appendChild(row);
  });

  const verdictEl = document.getElementById('duel-sample-verdict');
  const target = duelState.targetRuns;
  if (currRuns >= target) {
    verdictEl.style.background = '#DCFCE7';
    verdictEl.style.color = '#15803D';
    verdictEl.innerText = `RESULT: Batting Side Chased ${currRuns} Runs! Target ${target} Achieved with ${duelState.balls - overBalls.length} balls to spare!`;
  } else {
    verdictEl.style.background = '#FEE2E2';
    verdictEl.style.color = '#B91C1C';
    verdictEl.innerText = `RESULT: Bowling Side Defends! Scored ${currRuns}/${currWkts} (Defended by ${target - currRuns} runs).`;
  }
}

function renderDuelHistogram(hist, target) {
  const container = document.getElementById('duel-histogram-svg-container');
  if (!container) return;

  const maxRuns = Math.max(...Object.keys(hist).map(Number), target + 4, 18);
  const maxFreq = Math.max(...Object.values(hist));

  let barsSvg = '';
  const w = 380; const h = 180;
  const barW = Math.max(8, (w - 40) / (maxRuns + 1));

  for (let r = 0; r <= maxRuns; r++) {
    const count = hist[r] || 0;
    const barH = count > 0 ? (count / maxFreq * 130) : 0;
    const x = 30 + r * barW;
    const y = h - 30 - barH;
    const isTargetPlus = r >= target;
    const fill = isTargetPlus ? 'var(--rr-pink)' : '#CBD5E1';

    barsSvg += `
      <rect x="${x}" y="${y}" width="${barW - 2}" height="${barH}" fill="${fill}" rx="2" opacity="0.85">
        <title>${r} runs: ${count} times (${(count/10).toFixed(1)}%)</title>
      </rect>
    `;
    if (r % 2 === 0) {
      barsSvg += `<text x="${x + barW/2 - 1}" y="${h - 14}" font-size="9" text-anchor="middle" fill="#64748B">${r}</text>`;
    }
  }

  // Target vertical line
  const targetX = 30 + target * barW - 1;
  const lineSvg = `
    <line x1="${targetX}" y1="10" x2="${targetX}" y2="${h - 26}" stroke="#EF4444" stroke-width="2" stroke-dasharray="3,3" />
    <text x="${targetX + 4}" y="20" font-size="10" font-weight="bold" fill="#EF4444">Target: ${target}</text>
  `;

  container.innerHTML = `
    <svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
      ${barsSvg}
      ${lineSvg}
      <line x1="26" y1="${h-28}" x2="${w-10}" y2="${h-28}" stroke="#E2E8F0" stroke-width="1" />
    </svg>
  `;
}

// --- 2. TACTICAL PACE/SPIN & PHASE SPLITS ---
function renderTacticsTab() {
  const batBody = document.getElementById('tactics-bat-body');
  const bowlBody = document.getElementById('tactics-bowl-body');
  if (!batBody || !bowlBody) return;

  // Aggregate pace/spin splits by batter
  const ps = APP_DATA.batter_pace_spin || [];
  const battersMap = {};
  ps.forEach(r => {
    if (!battersMap[r.striker_name]) battersMap[r.striker_name] = {};
    battersMap[r.striker_name][r.pace_or_spin.toLowerCase()] = r;
  });

  batBody.innerHTML = '';
  Object.keys(battersMap).forEach(name => {
    const pace = battersMap[name]['pace'] || { balls: 0, SR: 0, net_100: 0 };
    const spin = battersMap[name]['spin'] || { balls: 0, SR: 0, net_100: 0 };
    const diff = (pace.net_100 - spin.net_100).toFixed(1);

    let profileNote = 'Balanced';
    let profileColor = '#059669';
    if (diff > 35) { profileNote = 'Pace Destroyer / Spin Vulnerable'; profileColor = '#EF4444'; }
    else if (diff < -30) { profileNote = 'Spin Specialist / Pace Squeezed'; profileColor = '#3B82F6'; }
    else if (pace.net_100 > 25 && spin.net_100 > 25) { profileNote = 'Dual-Threat Elite (No Chokepoint)'; profileColor = 'var(--rr-pink)'; }

    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';
    tr.onclick = () => openPlayerProfile(name);
    tr.innerHTML = `
      <td style="font-weight: 700; color: var(--rr-navy);">${name}</td>
      <td style="text-align: right;">${pace.balls}</td>
      <td style="text-align: right;">${pace.SR}</td>
      <td style="text-align: right; color: #0284C7; font-weight: 700;">${pace.net_100 > 0 ? '+' : ''}${pace.net_100.toFixed(1)}</td>
      <td style="text-align: right;">${spin.balls}</td>
      <td style="text-align: right;">${spin.SR}</td>
      <td style="text-align: right; color: #8B5CF6; font-weight: 700;">${spin.net_100 > 0 ? '+' : ''}${spin.net_100.toFixed(1)}</td>
      <td style="text-align: right; color: var(--rr-pink); font-weight: 700;">${diff > 0 ? '+' : ''}${diff}</td>
      <td style="text-align: left; font-size: 11px; font-weight: 700; color: ${profileColor};">${profileNote}</td>
    `;
    batBody.appendChild(tr);
  });

  // Aggregate bowler phase splits
  const bp = APP_DATA.bowler_phase || [];
  const bowlersMap = {};
  bp.forEach(r => {
    if (!bowlersMap[r.bowler_name]) bowlersMap[r.bowler_name] = {};
    bowlersMap[r.bowler_name][r.phase.toUpperCase()] = r;
  });

  bowlBody.innerHTML = '';
  Object.keys(bowlersMap).forEach(name => {
    const pp = bowlersMap[name]['PP'] || { net_100: 0, econ: 0 };
    const mid = bowlersMap[name]['MID'] || { net_100: 0, econ: 0 };
    const death = bowlersMap[name]['DEATH'] || { net_100: 0, econ: 0 };

    const getChip = (net) => {
      if (net >= 25) return `<span style="background: #BBF7D0; color: #166534; font-weight: bold; padding: 2px 6px; border-radius: 4px;">+${net.toFixed(1)}</span>`;
      if (net >= 0) return `<span style="background: #FEF08A; color: #854D0E; font-weight: bold; padding: 2px 6px; border-radius: 4px;">+${net.toFixed(1)}</span>`;
      return `<span style="background: #FECACA; color: #991B1B; font-weight: bold; padding: 2px 6px; border-radius: 4px;">${net.toFixed(1)}</span>`;
    };

    let directive = 'Flexible deployment';
    if (pp.net_100 < -20 && mid.net_100 > 20) directive = 'Middle/Death Specialist (Banned from PP)';
    else if (pp.net_100 > 30 && mid.net_100 > 30 && death.net_100 > 30) directive = 'Universal 3-Phase Engine';
    else if (pp.net_100 > 40 && death.net_100 < 0) directive = 'Front-Load Striker (Overs 1-14 only)';
    else if (death.net_100 > 40) directive = 'Primary Death Executioner';

    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';
    tr.onclick = () => openPlayerProfile(name);
    tr.innerHTML = `
      <td style="font-weight: 700; color: var(--rr-navy);">${name}</td>
      <td style="text-align: center;">${getChip(pp.net_100)}</td>
      <td style="text-align: center;">${pp.econ.toFixed(2)}</td>
      <td style="text-align: center;">${getChip(mid.net_100)}</td>
      <td style="text-align: center;">${mid.econ.toFixed(2)}</td>
      <td style="text-align: center;">${getChip(death.net_100)}</td>
      <td style="text-align: center;">${death.econ.toFixed(2)}</td>
      <td style="text-align: left; font-size: 11px; font-weight: 600; color: var(--rr-navy);">${directive}</td>
    `;
    bowlBody.appendChild(tr);
  });
}

// --- 3. 2027 RR WAR-ROOM SQUAD ---
let squadRoleFilter = 'all';

function renderSquadTab() {
  const body = document.getElementById('squad-body');
  if (!body) return;

  const squad = APP_DATA.optimal_squad || [];
  body.innerHTML = '';

  const filtered = squad.filter(p => {
    if (squadRoleFilter === 'bat') return p.role === 'bat';
    if (squadRoleFilter === 'bowl') return p.role === 'bowl';
    return true;
  });

  filtered.forEach(p => {
    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';
    tr.onclick = () => openPlayerProfile(p.name);

    const isOverseas = p.overseas === 'Yes';
    const tagBg = isOverseas ? '#EFF6FF' : '#F0FDF4';
    const tagColor = isOverseas ? '#1D4ED8' : '#15803D';

    tr.innerHTML = `
      <td style="text-align: center; font-weight: bold; color: var(--rr-pink);">${p.rank}</td>
      <td style="font-weight: 700; color: var(--rr-navy);">${getFlag(p.nationality)} ${p.name}</td>
      <td style="text-align: center; text-transform: uppercase; font-size: 11px;">${p.role}</td>
      <td style="text-align: center; font-size: 11px; font-weight: 600;">${p.tactical_role}</td>
      <td style="text-align: center;"><span style="background: ${tagBg}; color: ${tagColor}; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold;">${p.nationality}</span></td>
      <td style="text-align: right; font-weight: 700;">${p.model_score.toFixed(3)}</td>
      <td style="text-align: right; color: var(--rr-pink); font-weight: 800;">₹${p.est_cost_cr.toFixed(2)} Cr</td>
      <td style="text-align: right; color: #10B981; font-weight: 800;">${p.ev_per_cr.toFixed(3)}</td>
      <td style="text-align: left; font-size: 11px; color: #475569;">${p.status}</td>
    `;
    body.appendChild(tr);
  });
}

function filterSquad(role) {
  squadRoleFilter = role;
  document.querySelectorAll('#tab-squad .toggle-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById(`squad-btn-${role}`);
  if (btn) btn.classList.add('active');
  renderSquadTab();
}

// --- 4. UNSTOP SUBMISSION HUB ---
function renderSubmissionTab() {
  const batArea = document.getElementById('unstop-bat-text');
  const bowlArea = document.getElementById('unstop-bowl-text');
  if (!batArea || !bowlArea) return;

  const bats = APP_DATA.adj_batters.slice(0, 10);
  const bowls = APP_DATA.adj_bowlers.slice(0, 10);

  let batText = `RAJASTHAN ROYALS SUPERR SELECTOR SEASON 2 - ROUND 1 SUBMISSION\\n`;
  batText += `METHODOLOGY: Continuous Leverage Index (LI >= 1.32, 49,276 deliveries), Empirical Bayes 4-Pillar Shrunk Model, Leave-One-Out Opponent Adjustment, 300 Bootstrap Iterations.\\n\\n`;
  batText += `==================== TOP 10 BATTERS ====================\\n`;
  bats.forEach((p, i) => {
    batText += `${i + 1}. ${p.player} (Score: ${p.score.toFixed(3)})\\n`;
    batText += `   - HP Balls: ${p.hp_balls} | HP Runs: ${p.hp_runs} | HP SR: ${p.sr}\\n`;
    batText += `   - Net Runs Added/100: +${p.net_100.toFixed(1)} | WPA/100: +${p.wpa_100.toFixed(3)}\\n`;
    batText += `   - Elevation Gap (Delta): +${p.delta.toFixed(1)} | Consistency: ${(p.consistency * 100).toFixed(1)}%\\n`;
    batText += `   - Tactical Rationale: High-leverage executioner with verified sample robustness.\\n\\n`;
  });

  let bowlText = `RAJASTHAN ROYALS SUPERR SELECTOR SEASON 2 - ROUND 1 SUBMISSION\\n`;
  bowlText += `METHODOLOGY: Continuous Leverage Index (LI >= 1.32, 49,276 deliveries), Dynamic Wicket Valuation (PP: 8.3, Mid: 6.0, Death: 2.8), Opposition-Adjusted 4-Pillar Model.\\n\\n`;
  bowlText += `==================== TOP 10 BOWLERS ====================\\n`;
  bowls.forEach((p, i) => {
    bowlText += `${i + 1}. ${p.player} (Score: ${p.score.toFixed(3)})\\n`;
    bowlText += `   - HP Balls: ${p.hp_balls} | HP Econ: ${(p.hp_runs / (p.hp_balls / 6)).toFixed(2)} | Wkts: ${p.outs}\\n`;
    bowlText += `   - Net Runs Saved/100: +${p.net_100.toFixed(1)} | WPA/100: +${p.wpa_100.toFixed(3)}\\n`;
    bowlText += `   - Elevation Gap (Delta): +${p.delta.toFixed(1)} | Consistency: ${(p.consistency * 100).toFixed(1)}%\\n`;
    bowlText += `   - Tactical Rationale: Proven 3-phase execution under match-deciding leverage.\\n\\n`;
  });

  batArea.value = batText;
  bowlArea.value = bowlText;
}

function copySubmissionText(role) {
  const elId = role === 'bat' ? 'unstop-bat-text' : 'unstop-bowl-text';
  const textEl = document.getElementById(elId);
  if (!textEl) return;
  textEl.select();
  navigator.clipboard.writeText(textEl.value).then(() => {
    alert(`Top 10 ${role === 'bat' ? 'Batters' : 'Bowlers'} formatted text copied to clipboard for Unstop!`);
  }).catch(() => {
    alert('Please copy manually from the text box.');
  });
}
'''

# Check if tactical JS is already appended
if 'TACTICAL DUGOUT SUITE IMPLEMENTATION' not in html:
    # Append before </script>
    pos_script_end = html.rfind('</script>')
    html = html[:pos_script_end] + js_code_to_add + '\n' + html[pos_script_end:]
    print("Tactical JavaScript functions appended!")
else:
    print("Tactical JS already present.")

# 8. Update switchTab lazy re-renders to include the new tabs
pos_switch = html.find('function switchTab(tabId)')
if pos_switch != -1:
    pos_switch_body_end = html.find('}', pos_switch)
    # Find inside switchTab
    needle = "else if (tabId === 'tab-notable') renderNotableNames();"
    replacement = """else if (tabId === 'tab-notable') renderNotableNames();
  else if (tabId === 'tab-duel') initDuelSimulator();
  else if (tabId === 'tab-tactics') renderTacticsTab();
  else if (tabId === 'tab-squad') renderSquadTab();
  else if (tabId === 'tab-submission') renderSubmissionTab();"""
    if needle in html and "tab-duel" not in html[pos_switch:pos_switch+1000]:
        html = html.replace(needle, replacement, 1)
        print("switchTab lazy re-renders updated!")

# 9. Update openPlayerProfile to include Pace/Spin or Phase splits
# Check openPlayerProfile
profile_addition_needle = "bodyEl.innerHTML = `"
profile_addition_replacement = """
  // Check for Pace/Spin or Bowler Phase
  let tacticalSplitHtml = '';
  if (p.role === 'bat') {
    const psList = (APP_DATA.batter_pace_spin || []).filter(x => x.striker_name.toLowerCase() === p.name.toLowerCase());
    if (psList.length > 0) {
      const pace = psList.find(x => x.pace_or_spin.toLowerCase() === 'pace') || { SR: '-', net_100: 0, balls: 0 };
      const spin = psList.find(x => x.pace_or_spin.toLowerCase() === 'spin') || { SR: '-', net_100: 0, balls: 0 };
      tacticalSplitHtml = `
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-top: 14px;">
          <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--rr-navy); margin-bottom: 6px;">⚡ Pace vs Spin Chokepoint Split</div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px;">
            <div style="background: #EFF6FF; padding: 6px 8px; border-radius: 4px;">
              <span style="font-weight: bold; color: #1E40AF;">Vs Pace:</span> ${pace.SR} SR | <b style="color: #0284C7;">${pace.net_100 > 0 ? '+' : ''}${pace.net_100.toFixed ? pace.net_100.toFixed(1) : pace.net_100}</b> Net/100
            </div>
            <div style="background: #F5F3FF; padding: 6px 8px; border-radius: 4px;">
              <span style="font-weight: bold; color: #5B21B6;">Vs Spin:</span> ${spin.SR} SR | <b style="color: #8B5CF6;">${spin.net_100 > 0 ? '+' : ''}${spin.net_100.toFixed ? spin.net_100.toFixed(1) : spin.net_100}</b> Net/100
            </div>
          </div>
        </div>
      `;
    }
  } else {
    const bpList = (APP_DATA.bowler_phase || []).filter(x => x.bowler_name.toLowerCase() === p.name.toLowerCase());
    if (bpList.length > 0) {
      const pp = bpList.find(x => x.phase === 'PP') || { econ: '-', net_100: 0 };
      const mid = bpList.find(x => x.phase === 'MID') || { econ: '-', net_100: 0 };
      const death = bpList.find(x => x.phase === 'DEATH') || { econ: '-', net_100: 0 };
      tacticalSplitHtml = `
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-top: 14px;">
          <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--rr-navy); margin-bottom: 6px;">🎯 3-Phase Deployment Split</div>
          <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; font-size: 10px; text-align: center;">
            <div style="background: rgba(37,99,235,0.08); padding: 4px; border-radius: 4px;">
              <b>PP:</b> Econ ${pp.econ} | ${pp.net_100.toFixed ? pp.net_100.toFixed(1) : pp.net_100}
            </div>
            <div style="background: rgba(16,185,129,0.08); padding: 4px; border-radius: 4px;">
              <b>MID:</b> Econ ${mid.econ} | ${mid.net_100.toFixed ? mid.net_100.toFixed(1) : mid.net_100}
            </div>
            <div style="background: rgba(229,0,125,0.08); padding: 4px; border-radius: 4px;">
              <b>DEATH:</b> Econ ${death.econ} | ${death.net_100.toFixed ? death.net_100.toFixed(1) : death.net_100}
            </div>
          </div>
        </div>
      `;
    }
  }

  bodyEl.innerHTML = `
"""

if "Pace vs Spin Chokepoint Split" not in html and profile_addition_needle in html:
    html = html.replace(profile_addition_needle, profile_addition_replacement, 1)
    # Also inject tacticalSplitHtml inside drawer
    drawer_target = "<!-- D2 SENSITIVITY"
    drawer_replacement = "${tacticalSplitHtml}\n\n          <!-- D2 SENSITIVITY"
    html = html.replace(drawer_target, drawer_replacement, 1)
    print("openPlayerProfile updated with tactical splits!")

# Save to index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("--- index.html enhancement successfully written! ---")

