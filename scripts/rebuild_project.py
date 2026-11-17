import re
import json
import pandas as pd

print("--- Starting Clean Project Rebuild ---")

# 1. Load verified data sources
expected_df = pd.read_csv('expected_dashboard_values.csv')
adj_bat_exp = expected_df[expected_df['role'] == 'bat'].sort_values('rank').to_dict(orient='records')
adj_bowl_exp = expected_df[expected_df['role'] == 'bowl'].sort_values('rank').to_dict(orient='records')

tactical_df = pd.read_csv('tactical_splits_verified.csv')
tactical_records = tactical_df.to_dict(orient='records')

print(f"Loaded: {len(adj_bat_exp)} Adj Batters, {len(adj_bowl_exp)} Adj Bowlers, {len(tactical_records)} Tactical Split rows.")

# 2. Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 3. Update APP_DATA in index.html
pos_app_data = html.find('const APP_DATA =')
pos_app_data_end = html.find(';\n', pos_app_data)
if pos_app_data_end == -1:
    pos_app_data_end = html.find(';', pos_app_data)

json_str = html[pos_app_data + len('const APP_DATA ='):pos_app_data_end].strip()
app_data = json.loads(json_str)

# Ensure adj_batters and adj_bowlers equal expected_dashboard_values.csv
app_data['adj_batters'] = adj_bat_exp
app_data['adj_bowlers'] = adj_bowl_exp

# Update tactical splits to verified
app_data['tactical_splits_verified'] = tactical_records

# Remove optimal_squad and pricing
if 'optimal_squad' in app_data:
    del app_data['optimal_squad']
if 'batter_pace_spin' in app_data:
    del app_data['batter_pace_spin']
if 'bowler_phase' in app_data:
    del app_data['bowler_phase']

new_json_str = json.dumps(app_data, separators=(',', ':'))
html = html[:pos_app_data] + 'const APP_DATA = ' + new_json_str + html[pos_app_data_end:]
print("APP_DATA updated with verified datasets (optimal_squad removed)!")

# 4. Remove tab-squad from navigation rail
nav_squad_pattern = r'<button onclick="switchTab\(\'tab-squad\'\)" id="nav-tab-squad".*?</button>\s*'
html = re.sub(nav_squad_pattern, '', html, flags=re.DOTALL)

# 5. Remove <section id="tab-squad"> ... </section>
section_squad_pattern = r'<!-- TAB: 2027 RR WAR-ROOM SQUAD.*?<section id="tab-squad".*?</section>'
html = re.sub(section_squad_pattern, '', html, flags=re.DOTALL)

# Also check for standalone <section id="tab-squad" if comment was missing
section_squad_standalone = r'<section id="tab-squad" class="tab-pane">.*?</section>'
html = re.sub(section_squad_standalone, '', html, flags=re.DOTALL)

# 6. Relabel Duel Simulator in nav-rail and header
html = html.replace('<span>Dugout Duel Simulator</span>', '<span>Matchup Duel Simulator (Illustrative)</span>')
html = html.replace('<span>⚔️ Duel Sim</span>', '<span>⚔️ Duel Sim (Illustrative)</span>')
html = html.replace('title="Open Interactive Dugout Duel Simulator"', 'title="Open Matchup Duel Simulator (Illustrative toy, not a model output)"')

# Relabel inside tab-duel card
html = html.replace(
    '<span class="card-title-prefix">Part T1:</span> Interactive Dugout Matchup Duel Simulator',
    '<span class="card-title-prefix">Part T1:</span> Interactive Matchup Duel Simulator <span style="font-size: 13px; font-weight: normal; color: var(--rr-text-muted);">(Illustrative toy, not a model output)</span>'
)
html = html.replace(
    '1,000-Iteration Monte Carlo Matchup Engine • Ball-by-Ball Leverage State Space • Empirical Distribution Blending',
    'Illustrative toy, not a model output • Exploratory Monte Carlo scenario exploration tool'
)
# Update disclaimer banner in tab-duel
old_duel_banner = r'<div style="background: rgba\(229,0,125,0\.06\); border-left: 3px solid var\(--rr-pink\); padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">\s*<p style="font-size: 13px; line-height: 1\.5; color: var\(--rr-navy-900\); margin: 0;">\s*<strong>Franchise Tactical Application:.*?</div>'
new_duel_banner = '''<div style="background: rgba(148,163,184,0.1); border-left: 3px solid #64748B; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
            <p style="font-size: 13px; line-height: 1.5; color: var(--rr-navy-900); margin: 0;">
              <strong>Model Boundary Notice:</strong> This interactive simulator is an <em>illustrative toy, not a model output</em>. It serves solely for exploratory matchup visualization and is not part of the empirical 4-pillar scoring engine.
            </p>
          </div>'''
html = re.sub(old_duel_banner, lambda m: new_duel_banner, html, flags=re.DOTALL)

# 7. Update Section A facts
old_method_summary = r'<strong>Method Summary:</strong> We define pressure as how much the next delivery can move the match.*?The ranking is then stress-tested with match-level bootstrap resamples.*?\.'
new_method_summary = '''<strong>Method Summary:</strong> We define pressure as how much the next delivery can move the match (a leverage index built from a win-probability model), rather than a hand-picked list of over and run-rate rules. The source data covers IPL and T20I matches from 2022 to 2026 (958 players total; extras1_runs is a type code; byes and leg-bye runs are unrecorded). Deliveries in the top quartile (LI &ge; 1.32; 49,276 deliveries) are classified as high pressure, where win-probability swing averages 3.73 percentage points per ball compared to 0.62 percentage points in ordinary situations. Eligibility requires at least 150 high-pressure deliveries, 8 high-pressure matches (6+ balls each), and 100 ordinary deliveries: 100 batters and 102 bowlers qualify. Each qualified player is scored on Pressure Value (35%), Win Probability Added (30%), Delta vs own baseline (20%), and Consistency (15%), with Empirical Bayes shrinkage applied. In the adjusted model, opposition quality is normalized via leave-one-match-out ratings. Rankings are evaluated across 200 match-level bootstrap resamples for the adjusted model (300 for the original model), in preparation for Round 2 in Mumbai and Round 3 in Goa for the Round 2 winner.'''

html = re.sub(old_method_summary, lambda m: new_method_summary, html, flags=re.DOTALL)

# 8. Update Tactical Splits Tab (tab-tactics)
old_tactics_callouts = r'<!-- KEY CHOKEPOINT CALLOUTS -->.*?<!-- BATTER PACE VS SPIN TABLE -->'
new_tactics_callouts = '''<!-- KEY CHOKEPOINT CALLOUTS -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 24px;">
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #64748B; border-radius: 8px; padding: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 800; color: var(--rr-navy); font-size: 13px;">Babar Azam: Pace vs Spin Split</span>
                <span class="badge" style="background: #E2E8F0; color: #475569;">Sample Caveat</span>
              </div>
              <p style="font-size: 12px; color: #475569; margin: 8px 0 0 0; line-height: 1.4;">
                Pace Net/100: +47.43 (SR 182.1, 145 balls, &plusmn;20.0 SE) vs Spin Net/100: -20.02 (SR 120.0, 75 balls, &plusmn;25.3 SE). <em>Note: Spin sample is limited (&lt;100 balls) with wider standard error.</em>
              </p>
            </div>

            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #64748B; border-radius: 8px; padding: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 800; color: var(--rr-navy); font-size: 13px;">Shubman Gill: Pace vs Spin Split</span>
                <span class="badge" style="background: #DCFCE7; color: #15803D;">Adequate Sample</span>
              </div>
              <p style="font-size: 12px; color: #475569; margin: 8px 0 0 0; line-height: 1.4;">
                Spin Net/100: +45.12 (SR 169.7, 201 balls, &plusmn;13.8 SE) vs Pace Net/100: -1.20 (SR 149.6, 363 balls, &plusmn;12.9 SE). Strong positive execution against spin compared to high-pressure pace.
              </p>
            </div>

            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #64748B; border-radius: 8px; padding: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 800; color: var(--rr-navy); font-size: 13px;">Phil Salt: Pace vs Spin Balance</span>
                <span class="badge" style="background: #DCFCE7; color: #15803D;">Adequate Sample</span>
              </div>
              <p style="font-size: 12px; color: #475569; margin: 8px 0 0 0; line-height: 1.4;">
                Pace Net/100: +36.93 (SR 173.7, 224 balls, &plusmn;16.7 SE) vs Spin Net/100: +36.69 (SR 179.1, 115 balls, &plusmn;23.6 SE). Demonstrates closely matched returns across bowling types.
              </p>
            </div>
          </div>

          <!-- BATTER PACE VS SPIN TABLE -->'''

html = re.sub(old_tactics_callouts, lambda m: new_tactics_callouts, html, flags=re.DOTALL)

# Update the Batter Pace vs Spin Table Headers
old_bat_headers = r'<table class="scorecard-table font-mono" id="tactics-bat-table">.*?<thead>.*?</thead>'
new_bat_headers = '''<table class="scorecard-table font-mono" id="tactics-bat-table">
                  <thead>
                    <tr>
                      <th style="text-align: left;">Player</th>
                      <th style="text-align: center;">Split</th>
                      <th style="text-align: right;">HP Balls</th>
                      <th style="text-align: right;">Runs</th>
                      <th style="text-align: right;">Strike Rate</th>
                      <th style="text-align: right;">Net/100</th>
                      <th style="text-align: right;">Std. Error (&plusmn;)</th>
                      <th style="text-align: center;">Sample Flag</th>
                    </tr>
                  </thead>'''
html = re.sub(old_bat_headers, lambda m: new_bat_headers, html, flags=re.DOTALL)

# Update Bowler Phase Table Headers
old_bowl_headers = r'<table class="scorecard-table font-mono" id="tactics-bowl-table">.*?<thead>.*?</thead>'
new_bowl_headers = '''<table class="scorecard-table font-mono" id="tactics-bowl-table">
                  <thead>
                    <tr>
                      <th style="text-align: left;">Bowler</th>
                      <th style="text-align: center;">Phase</th>
                      <th style="text-align: right;">HP Deliveries</th>
                      <th style="text-align: right;">Runs Conceded</th>
                      <th style="text-align: right;">Economy</th>
                      <th style="text-align: right;">Net/100</th>
                      <th style="text-align: right;">Std. Error (&plusmn;)</th>
                      <th style="text-align: center;">Sample Flag</th>
                    </tr>
                  </thead>'''
html = re.sub(old_bowl_headers, lambda m: new_bowl_headers, html, flags=re.DOTALL)

# 9. Update Bumrah Section in tab-submission
old_bumrah_section = r'<!-- THE SUPERSTAR PARADOX EXPLAINER -->.*?<!-- ONE-CLICK UNSTOP SUBMISSION FORMATTERS -->'
new_bumrah_section = '''<!-- THE SUPERSTAR PARADOX EXPLAINER -->
          <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid var(--rr-navy); border-radius: 8px; padding: 18px; margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <span style="font-weight: 800; font-size: 14px; color: var(--rr-navy);">Analysis of Jasprit Bumrah (Rank #24 Adjusted • Rank #26 Original)</span>
              <span class="badge" style="background: #E2E8F0; color: #475569;">Untested Cause</span>
            </div>
            <p style="font-size: 12px; line-height: 1.5; color: #334155; margin: 0;">
              In high-pressure deliveries (LI &ge; 1.32), Jasprit Bumrah has <strong>506 deliveries</strong>, with <strong>42.2% dot balls</strong>, a batter strike rate of <strong>125.4</strong>, and <strong>20 wickets</strong> against <strong>27.8 expected</strong>. His pressure value is <strong>+15.73 Net/100</strong>, while his ordinary-level gap (Delta) is <strong>-11.19</strong>. While one possible explanation is that opposing batters adopt an unusually risk-averse approach against him, <em>the underlying cause (e.g. batter risk aversion vs. match state vs. execution) is untested in the data pack</em>.
            </p>
          </div>

          <!-- ONE-CLICK UNSTOP SUBMISSION FORMATTERS -->'''

html = re.sub(old_bumrah_section, lambda m: new_bumrah_section, html, flags=re.DOTALL)

# 10. Scrub banned marketing words
html = html.replace('99% of submissions', 'standard submissions')
html = html.replace('publication-grade', 'verified')
html = html.replace('Guaranteed Mumbai Shortlist Protocol', '5-Gate Verification Protocol')
html = html.replace('guaranteed Mumbai shortlist', 'verified selection protocol')
html = html.replace('guarantees of shortlist', 'evaluation criteria')
html = html.replace('indisputable', 'verified')

# 11. Update Javascript implementations
new_js_tactics = '''function renderTacticsTab() {
  const batBody = document.getElementById('tactics-bat-body');
  const bowlBody = document.getElementById('tactics-bowl-body');
  if (!batBody || !bowlBody) return;

  const splits = APP_DATA.tactical_splits_verified || [];
  const batSplits = splits.filter(r => r.role === 'bat');
  const bowlSplits = splits.filter(r => r.role === 'bowl');

  batBody.innerHTML = '';
  batSplits.forEach(r => {
    const tr = document.createElement('tr');
    const isLow = r.sample_flag && r.sample_flag.startsWith('LOW');
    if (isLow) {
      tr.style.opacity = '0.55';
      tr.style.background = '#F8FAFC';
      tr.style.color = '#64748B';
    }
    const flagChip = isLow
      ? `<span class="badge" style="background: #E2E8F0; color: #475569; font-size: 10px;">${r.sample_flag}</span>`
      : `<span class="badge" style="background: #DCFCE7; color: #15803D; font-size: 10px;">OK (&ge;100)</span>`;

    tr.innerHTML = `
      <td style="font-weight: 700;">${r.player}</td>
      <td style="text-align: center;"><span class="badge ${r.split === 'Pace' ? 'badge-blue' : 'badge-purple'}">${r.split}</span></td>
      <td style="text-align: right;">${r.hp_balls}</td>
      <td style="text-align: right;">${r.runs_scored_or_conceded}</td>
      <td style="text-align: right;">${r.strike_rate_or_econ.toFixed(1)}</td>
      <td style="text-align: right; font-weight: 700; color: ${r.net100 >= 0 ? 'var(--rr-pink)' : '#EF4444'};">${r.net100 >= 0 ? '+' : ''}${r.net100.toFixed(2)}</td>
      <td style="text-align: right;">&plusmn;${r.std_err.toFixed(1)}</td>
      <td style="text-align: center;">${flagChip}</td>
    `;
    batBody.appendChild(tr);
  });

  bowlBody.innerHTML = '';
  bowlSplits.forEach(r => {
    const tr = document.createElement('tr');
    const isLow = r.sample_flag && r.sample_flag.startsWith('LOW');
    if (isLow) {
      tr.style.opacity = '0.55';
      tr.style.background = '#F8FAFC';
      tr.style.color = '#64748B';
    }
    const flagChip = isLow
      ? `<span class="badge" style="background: #E2E8F0; color: #475569; font-size: 10px;">${r.sample_flag}</span>`
      : `<span class="badge" style="background: #DCFCE7; color: #15803D; font-size: 10px;">OK (&ge;100)</span>`;

    tr.innerHTML = `
      <td style="font-weight: 700;">${r.player}</td>
      <td style="text-align: center;"><span class="badge badge-gray">${r.split}</span></td>
      <td style="text-align: right;">${r.hp_balls}</td>
      <td style="text-align: right;">${r.runs_scored_or_conceded}</td>
      <td style="text-align: right;">${r.strike_rate_or_econ.toFixed(2)}</td>
      <td style="text-align: right; font-weight: 700; color: ${r.net100 >= 0 ? 'var(--rr-pink)' : '#EF4444'};">${r.net100 >= 0 ? '+' : ''}${r.net100.toFixed(2)}</td>
      <td style="text-align: right;">&plusmn;${r.std_err.toFixed(1)}</td>
      <td style="text-align: center;">${flagChip}</td>
    `;
    bowlBody.appendChild(tr);
  });
}'''

new_js_submission = '''function renderSubmissionTab() {
  const batArea = document.getElementById('unstop-bat-text');
  const bowlArea = document.getElementById('unstop-bowl-text');
  if (!batArea || !bowlArea) return;

  const bats = APP_DATA.adj_batters.slice(0, 10);
  const bowls = APP_DATA.adj_bowlers.slice(0, 10);

  let batText = `RAJASTHAN ROYALS SUPERR SELECTOR SEASON 2 - ROUND 1 SUBMISSION\\n`;
  batText += `METHODOLOGY: Continuous Leverage Index (LI >= 1.32, 49,276 deliveries), Empirical Bayes 4-Pillar Shrunk Model, Leave-One-Out Opponent Adjustment, 200 Bootstrap Resamples.\\n\\n`;
  batText += `==================== TOP 10 BATTERS (OPPOSITION-ADJUSTED) ====================\\n`;
  bats.forEach((p, i) => {
    batText += `${i + 1}. ${p.player} (Score: ${p.score.toFixed(3)})\\n`;
    batText += `   - HP Balls: ${p.hp_balls} | HP Runs: ${p.hp_runs} | HP SR: ${p.sr}\\n`;
    batText += `   - Net Runs Added/100: +${p.net_100.toFixed(2)} | WPA/100: +${p.wpa_100.toFixed(3)}\\n`;
    batText += `   - Elevation Gap (Delta): ${p.delta >= 0 ? '+' : ''}${p.delta.toFixed(2)} | Consistency: ${(p.consistency * 100).toFixed(1)}% | Bootstrap Top 10: ${p.boot_top10.toFixed(1)}%\\n\\n`;
  });

  let bowlText = `RAJASTHAN ROYALS SUPERR SELECTOR SEASON 2 - ROUND 1 SUBMISSION\\n`;
  bowlText += `METHODOLOGY: Continuous Leverage Index (LI >= 1.32, 49,276 deliveries), Dynamic Wicket Valuation (PP: 8.3, Mid: 6.0, Death: 2.8), Opposition-Adjusted 4-Pillar Model, 200 Bootstrap Resamples.\\n\\n`;
  bowlText += `==================== TOP 10 BOWLERS (OPPOSITION-ADJUSTED) ====================\\n`;
  bowls.forEach((p, i) => {
    bowlText += `${i + 1}. ${p.player} (Score: ${p.score.toFixed(3)})\\n`;
    bowlText += `   - HP Balls: ${p.hp_balls} | HP Econ: ${p.econ.toFixed(2)} | Wickets: ${p.wkts}\\n`;
    bowlText += `   - Net Runs Saved/100: +${p.net_100.toFixed(2)} | WPA/100: +${p.wpa_100.toFixed(3)}\\n`;
    bowlText += `   - Elevation Gap (Delta): ${p.delta >= 0 ? '+' : ''}${p.delta.toFixed(2)} | Consistency: ${(p.consistency * 100).toFixed(1)}% | Bootstrap Top 10: ${p.boot_top10.toFixed(1)}%\\n\\n`;
  });

  batArea.value = batText;
  bowlArea.value = bowlText;
}'''

# Replace old functions in html
pos_tactics_fn = html.find('function renderTacticsTab()')
pos_submission_fn = html.find('function renderSubmissionTab()')
pos_submission_fn_end = html.find('function copySubmissionText', pos_submission_fn)

if pos_tactics_fn != -1 and pos_submission_fn_end != -1:
    html = html[:pos_tactics_fn] + new_js_tactics + '\n\n' + new_js_submission + '\n\n' + html[pos_submission_fn_end:]
    print("Updated renderTacticsTab and renderSubmissionTab in JavaScript!")

# Remove tab-squad lazy render from switchTab
html = html.replace("else if (tabId === 'tab-squad') renderSquadTab();\n  ", "")

# 12. Write updated index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("--- Clean Project Rebuild written to index.html successfully! ---")
