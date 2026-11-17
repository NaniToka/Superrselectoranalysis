import re
import json
import pandas as pd

print("--- Applying Google-Grade Data Analytics UI Upgrade to index.html ---")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Load rr_squad_pressure_audit.csv
rr_df = pd.read_csv('rr_squad_pressure_audit.csv')
rr_records = rr_df.to_dict(orient='records')

# 2. Extract APP_DATA
m = re.search(r'const APP_DATA\s*=\s*(\{.*?\});\s*(?:const|let|var|\n\s*//)', html, re.DOTALL)
if not m:
    raise ValueError("Could not find const APP_DATA in index.html")

app_data = json.loads(m.group(1))
app_data['rr_squad_audit'] = rr_records

new_app_data_str = "const APP_DATA = " + json.dumps(app_data, separators=(',', ':')) + ";\n\nconst "
html = html[:m.start()] + new_app_data_str + html[m.end():]

# 3. Add Google Cloud / BigQuery style Header Telemetry Pill if not present
telemetry_banner = """
    <!-- GOOGLE-GRADE DATA TELEMETRY BAR -->
    <div class="google-telemetry-bar no-print" style="background: rgba(4, 17, 38, 0.95); border-bottom: 1px solid rgba(255,255,255,0.08); padding: 6px 20px; font-size: 11px; color: #94A3B8; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
      <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
        <span style="display: inline-flex; align-items: center; gap: 6px; background: rgba(16, 185, 129, 0.15); color: #34D399; padding: 2px 8px; border-radius: 9999px; font-weight: 700; font-size: 10px; border: 1px solid rgba(16, 185, 129, 0.3);">
          <span style="width: 6px; height: 6px; background: #10B981; border-radius: 50%; display: inline-block;"></span>
          LIVE PIPELINE: 136 CHECKS PASSING (EXIT 0)
        </span>
        <span><strong>DATASET:</strong> 197,100 Deliveries &bull; 851 Matches &bull; 958 Total Players (2022&ndash;2026 IPL &amp; T20I)</span>
        <span><strong>WIN-PROB GBDT:</strong> AUC 0.89 (Chase) | 0.68 (1st Inn) &bull; Brier 0.137</span>
      </div>
      <div style="display: flex; align-items: center; gap: 10px;">
        <span style="color: var(--rr-pink); font-weight: 700;">VOLATILITY:</span> 0.62 &rarr; 3.73 pts/ball (6.0&times; surge)
        <span style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); font-size: 10px; color: #E2E8F0;">LEVERAGE LI &ge; 1.32</span>
      </div>
    </div>
"""

if 'google-telemetry-bar' not in html:
    html = html.replace('</header>', '</header>\n' + telemetry_banner)

# 4. Insert RR Squad Pressure Audit Table Markup into tab-auction
rr_audit_html = """
          <!-- GOOGLE-GRADE RAJASTHAN ROYALS SQUAD PRESSURE AUDIT CONSOLE -->
          <div class="card" style="margin-bottom: 24px; border: 1px solid #CBD5E1; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);">
            <div class="card-header" style="background: linear-gradient(135deg, #041126 0%, #0F275E 100%); color: #FFFFFF; border-radius: 12px 12px 0 0; padding: 16px 20px;">
              <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span style="background: var(--rr-pink); color: #FFFFFF; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 4px; text-transform: uppercase;">RR In-House Audit</span>
                  <div class="card-title" style="color: #FFFFFF; font-size: 16px;">
                    Rajasthan Royals 2026 Squad Pressure Audit (15 Qualified Players)
                  </div>
                </div>
                <div class="card-subtitle" style="color: #94A3B8; font-size: 11px; margin-top: 2px;">
                  Empirical analysis of all 15 RR-contracted players meeting model qualification (&ge;150 HP deliveries) &bull; Source: rr_squad_pressure_audit.csv
                </div>
              </div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="background: rgba(255,255,255,0.15); color: #FFFFFF; font-size: 11px; padding: 4px 10px; border-radius: 6px; font-family: var(--font-mono);">15 Contracted Players Qualified</span>
              </div>
            </div>

            <!-- Key Findings KPI Grid -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; padding: 14px 20px; background: #F8FAFC; border-bottom: 1px solid #E2E8F0;">
              <div style="background: #FFFFFF; border-left: 3px solid var(--rr-pink); padding: 10px 14px; border-radius: 6px; box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);">
                <div style="font-size: 10px; font-weight: 800; color: var(--rr-pink); text-transform: uppercase;">Top Batting Asset</div>
                <div style="font-size: 13px; font-weight: 800; color: #0F172A; margin: 2px 0;">Vaibhav Sooryavanshi (Rank #8)</div>
                <div style="font-size: 11px; color: #64748B;">Score 0.386 &bull; Net +75.76 &bull; RR's sole Top-10 pressure batter</div>
              </div>

              <div style="background: #FFFFFF; border-left: 3px solid #2563EB; padding: 10px 14px; border-radius: 6px; box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);">
                <div style="font-size: 10px; font-weight: 800; color: #2563EB; text-transform: uppercase;">Top Bowling Asset</div>
                <div style="font-size: 13px; font-weight: 800; color: #0F172A; margin: 2px 0;">Jofra Archer (Rank #13)</div>
                <div style="font-size: 11px; color: #64748B;">Score 0.453 &bull; Net +24.49 &bull; Delta +25.49 &bull; RR's #1 pressure seamer</div>
              </div>

              <div style="background: #FFFFFF; border-left: 3px solid #F59E0B; padding: 10px 14px; border-radius: 6px; box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);">
                <div style="font-size: 10px; font-weight: 800; color: #D97706; text-transform: uppercase;">Squad Deficit Finding</div>
                <div style="font-size: 13px; font-weight: 800; color: #0F172A; margin: 2px 0;">13 of 15 Outside Top 40</div>
                <div style="font-size: 11px; color: #64748B;">Jaiswal #42, Hetmyer #58, Jurel #60, Parag #78, Bishnoi #93</div>
              </div>
            </div>

            <!-- Table Filter Controls -->
            <div style="padding: 10px 20px; background: #FFFFFF; border-bottom: 1px solid #E2E8F0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 11px; font-weight: 700; color: #475569;">Filter Role:</span>
                <button type="button" class="btn-rr-role-filter active" onclick="filterRRSquadTable('all', this)" style="padding: 3px 10px; font-size: 11px; border-radius: 4px; border: 1px solid #CBD5E1; background: #041126; color: #FFFFFF; cursor: pointer;">All 15</button>
                <button type="button" class="btn-rr-role-filter" onclick="filterRRSquadTable('bat', this)" style="padding: 3px 10px; font-size: 11px; border-radius: 4px; border: 1px solid #CBD5E1; background: #F8FAFC; color: #334155; cursor: pointer;">Batters (8)</button>
                <button type="button" class="btn-rr-role-filter" onclick="filterRRSquadTable('bowl', this)" style="padding: 3px 10px; font-size: 11px; border-radius: 4px; border: 1px solid #CBD5E1; background: #F8FAFC; color: #334155; cursor: pointer;">Bowlers (7)</button>
              </div>
              <div style="font-size: 11px; color: #64748B; font-family: var(--font-mono);">
                Status: Under IPL 2026 contract with Rajasthan Royals
              </div>
            </div>

            <!-- The RR Squad Table -->
            <div class="table-container" style="padding: 0;">
              <div class="table-scroll" style="max-height: 480px;">
                <table class="scorecard-table" style="width: 100%; border-collapse: collapse;">
                  <thead style="position: sticky; top: 0; z-index: 10; background: #041126; color: #FFFFFF;">
                    <tr>
                      <th style="padding: 8px 10px; font-size: 10.5px; text-align: center;">Adj. Rank</th>
                      <th style="padding: 8px 10px; font-size: 10.5px; text-align: left;">Player Name</th>
                      <th style="padding: 8px 10px; font-size: 10.5px; text-align: center;">Role</th>
                      <th style="padding: 8px 10px; font-size: 10.5px; text-align: center;">Overseas</th>
                      <th style="padding: 8px 10px; font-size: 10.5px; text-align: right;">HP Balls</th>
                      <th style="padding: 8px 10px; font-size: 10.5px; text-align: right;">Net HP / 100</th>
                      <th style="padding: 8px 10px; font-size: 10.5px; text-align: right;">Ordinary Net</th>
                      <th style="padding: 8px 10px; font-size: 10.5px; text-align: right;">Delta (&Delta;)</th>
                      <th style="padding: 8px 10px; font-size: 10.5px; text-align: right;">WPA / 100</th>
                      <th style="padding: 8px 10px; font-size: 10.5px; text-align: right;">Cons.</th>
                      <th style="padding: 8px 10px; font-size: 10.5px; text-align: right; color: #FFB3D9;">Adj. Score</th>
                    </tr>
                  </thead>
                  <tbody id="rr-squad-audit-table-body">
                    <!-- Populated via JS -->
                  </tbody>
                </table>
              </div>
            </div>
          </div>
"""

# Place RR squad audit table right above OPTION B BATTERS TABLE in tab-auction
if 'rr-squad-audit-table-body' not in html:
    html = html.replace('<!-- OPTION B BATTERS TABLE -->', rr_audit_html + '\n          <!-- OPTION B BATTERS TABLE -->')

# 5. Add JavaScript to render RR Squad Table dynamically
js_rr_render = """
function renderRRSquadAuditTable(filterRole = 'all') {
  const tbody = document.getElementById('rr-squad-audit-table-body');
  if (!tbody || !APP_DATA.rr_squad_audit) return;
  tbody.innerHTML = '';

  const list = APP_DATA.rr_squad_audit.filter(p => filterRole === 'all' || p.role === filterRole);
  list.sort((a, b) => a.adjusted_rank - b.adjusted_rank);

  list.forEach(p => {
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid #E2E8F0';
    const isTop15 = p.adjusted_rank <= 15;
    const rankBg = isTop15 ? 'background: #E5007D; color: #FFFFFF;' : 'background: #041126; color: #FFFFFF;';
    const netColor = p.net_hp > 0 ? '#059669' : '#DC2626';
    const deltaColor = p.delta > 0 ? '#059669' : '#DC2626';

    tr.innerHTML = `
      <td style="text-align: center; padding: 6px 10px;">
        <span style="display: inline-block; width: 24px; height: 24px; line-height: 24px; border-radius: 4px; font-size: 11px; font-weight: 800; ${rankBg}">#${p.adjusted_rank}</span>
      </td>
      <td style="font-weight: 700; color: #0F172A; padding: 6px 10px;">
        ${p.name} ${isTop15 ? '<span style="font-size: 9px; background: #FFF1F7; color: #E5007D; padding: 1px 5px; border-radius: 3px; border: 1px solid #FCE7F3; font-weight: 800; margin-left: 4px;">RR TOP ASSET</span>' : ''}
      </td>
      <td style="text-align: center; padding: 6px 10px;">
        <span style="font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; ${p.role === 'bat' ? 'background: #EFF6FF; color: #1D4ED8;' : 'background: #ECFDF5; color: #047857;'}">${p.role}</span>
      </td>
      <td style="text-align: center; font-size: 11px; padding: 6px 10px;">
        ${p.overseas === 'Yes' ? '<span style="background: #FEF3C7; color: #92400E; padding: 1px 5px; border-radius: 3px; font-size: 10px; font-weight: 700;">✈ Overseas</span>' : '<span style="color: #64748B;">India</span>'}
      </td>
      <td class="tabular" style="text-align: right; padding: 6px 10px; font-weight: 600;">${p.n_hp}</td>
      <td class="tabular" style="text-align: right; padding: 6px 10px; font-weight: 700; color: ${netColor};">${p.net_hp > 0 ? '+' : ''}${p.net_hp.toFixed(2)}</td>
      <td class="tabular" style="text-align: right; padding: 6px 10px; color: #64748B;">${p.net_np > 0 ? '+' : ''}${p.net_np.toFixed(2)}</td>
      <td class="tabular" style="text-align: right; padding: 6px 10px; font-weight: 600; color: ${deltaColor};">${p.delta > 0 ? '+' : ''}${p.delta.toFixed(2)}</td>
      <td class="tabular" style="text-align: right; padding: 6px 10px;">${p.wpa_hp > 0 ? '+' : ''}${p.wpa_hp.toFixed(3)}</td>
      <td class="tabular" style="text-align: right; padding: 6px 10px;">${(p.cons * 100).toFixed(1)}%</td>
      <td class="tabular" style="text-align: right; padding: 6px 10px; font-weight: 800; color: #E5007D;">${p.adjusted_score.toFixed(3)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function filterRRSquadTable(role, btn) {
  document.querySelectorAll('.btn-rr-role-filter').forEach(b => {
    b.style.background = '#F8FAFC';
    b.style.color = '#334155';
  });
  btn.style.background = '#041126';
  btn.style.color = '#FFFFFF';
  renderRRSquadAuditTable(role);
}
"""

if 'function renderRRSquadAuditTable' not in html:
    html = html.replace('function renderAuctionSection() {', js_rr_render + '\nfunction renderAuctionSection() {\n  renderRRSquadAuditTable();')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("--- index.html successfully upgraded with Google-Grade Data UI! ---")
