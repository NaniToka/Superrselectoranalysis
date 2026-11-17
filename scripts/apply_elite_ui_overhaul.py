import re
import sys

def overhaul_ui():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Fix the CSS block in <style>
    # Find the malformed block between .scorecard-table tbody tr:nth-child(even) and .rank-chip
    old_css_target = """  font-size: 12.5px;
  text-align: left;
  background: var(--rr-surface);
}

.scorecard-table th {
  background: var(--rr-surface-subtle);
  color: #EDE8DE;
  font-family: var(--font-mono);
  font-weight: 600;
  padding: 10px 12px;
  border-bottom: 1px solid var(--rr-border);
  white-space: nowrap;
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.scorecard-table td {
  padding: 9px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: var(--rr-text);
}

.scorecard-table tbody tr {
  transition: background 0.15s ease;
}

.scorecard-table tbody tr:hover {
  background: var(--rr-surface-hover) !important;
}

.scorecard-table tbody tr:nth-child(even) {
  background: rgba(255, 255, 255, 0.015);
}
  color: #1E293B;
  vertical-align: middle;
}

.scorecard-table tr:nth-child(even) {
  background: #FAFCFE;
}

.scorecard-table tr:hover {
  background: #FFF5F9;
}

/* STICKY COLUMNS */
.sticky-col-rank {
  position: sticky;
  left: 0;
  z-index: 10;
  background-color: #FFFFFF;
  width: 44px;
  text-align: center;
}

.scorecard-table tr:nth-child(even) .sticky-col-rank {
  background-color: #FAFCFE;
}
.scorecard-table tr:hover .sticky-col-rank {
  background-color: #FFF5F9;
}

.sticky-col-player {
  position: sticky;
  left: 44px;
  z-index: 10;
  background-color: #FFFFFF;
  font-weight: 700;
  min-width: 170px;
  box-shadow: 3px 0 6px -2px rgba(11, 31, 75, 0.07);
}

.scorecard-table tr:nth-child(even) .sticky-col-player {
  background-color: #FAFCFE;
}
.scorecard-table tr:hover .sticky-col-player {
  background-color: #FFF5F9;
}

.scorecard-table th.sticky-col-rank,
.scorecard-table th.sticky-col-player {
  background-color: #F8FAFC;
  z-index: 11;
}"""

    new_css_replacement = """  font-size: 12.5px;
  text-align: left;
  background: #08162B;
}

.scorecard-table th {
  background: #0B1E38;
  color: #F8FAFC;
  font-family: var(--font-mono);
  font-weight: 700;
  padding: 10px 12px;
  border-bottom: 1px solid var(--rr-border);
  white-space: nowrap;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.scorecard-table td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: var(--rr-text);
  font-size: 12.5px;
  vertical-align: middle;
}

.scorecard-table tbody tr {
  background: #08162B;
  transition: background 0.15s ease;
}

.scorecard-table tbody tr:nth-child(even) {
  background: #0B1D36;
}

.scorecard-table tbody tr:hover {
  background: #132E58 !important;
}

/* STICKY COLUMNS (Seamless High-Contrast Dark Navy) */
.sticky-col-rank {
  position: sticky;
  left: 0;
  z-index: 10;
  background-color: #08162B;
  width: 48px;
  text-align: center;
  color: #CBD5E1;
}

.scorecard-table tbody tr:nth-child(even) .sticky-col-rank {
  background-color: #0B1D36;
}
.scorecard-table tbody tr:hover .sticky-col-rank {
  background-color: #132E58 !important;
}

.sticky-col-player {
  position: sticky;
  left: 48px;
  z-index: 10;
  background-color: #08162B;
  font-weight: 700;
  min-width: 175px;
  color: #FFFFFF;
  box-shadow: 3px 0 10px rgba(0, 0, 0, 0.45);
}

.scorecard-table tbody tr:nth-child(even) .sticky-col-player {
  background-color: #0B1D36;
}
.scorecard-table tbody tr:hover .sticky-col-player {
  background-color: #132E58 !important;
}

.scorecard-table th.sticky-col-rank,
.scorecard-table th.sticky-col-player {
  background-color: #0B1E38;
  z-index: 11;
  color: #F8FAFC;
}"""

    if old_css_target in html:
        html = html.replace(old_css_target, new_css_replacement)
        print("Replaced malformed scorecard-table CSS successfully!")
    else:
        print("Warning: old_css_target not found verbatim, attempting regex replace...")

    # Also fix drawer and modal background colors
    html = re.sub(r'\.drawer-panel\s*\{\s*position:\s*fixed;[\s\S]*?background:\s*#FFFFFF;', 
                  """.drawer-panel {
  position: fixed;
  top: 0; right: 0; bottom: 0;
  width: 480px;
  max-width: 92vw;
  background: #08162B;
  color: #F8FAFC;
  border-left: 1px solid rgba(255, 255, 255, 0.12);""", html)

    html = re.sub(r'\.modal-content\s*\{\s*background:\s*#FFFFFF;',
                  """.modal-content {
  background: #08162B;
  color: #F8FAFC;
  border: 1px solid rgba(255, 255, 255, 0.14);""", html)

    # Enhance Master Dark Overrides
    dark_overrides_target = """div[style*="background: #FFFFFF"],
div[style*="background: #ffffff"],
div[style*="background:#FFFFFF"],
div[style*="background:#ffffff"],
div[style*="background: #F8FAFC"],
div[style*="background: #f8fafc"],
div[style*="background: #F4F6FA"] {
  background: var(--rr-surface) !important;
  color: var(--rr-text) !important;
  border-color: var(--rr-border) !important;
}"""

    enhanced_dark_overrides = """/* Universal High-End Dark Theme Normalization */
div[style*="background: #FFFFFF"],
div[style*="background: #ffffff"],
div[style*="background:#FFFFFF"],
div[style*="background:#ffffff"],
div[style*="background: #F8FAFC"],
div[style*="background: #f8fafc"],
div[style*="background: #FAF5FF"],
div[style*="background: #faf5ff"],
div[style*="background: #F4F6FA"],
div[style*="background: #F1F5F9"],
section[style*="background: #FFFFFF"],
section[style*="background: #F8FAFC"] {
  background: #0A1B33 !important;
  color: #F8FAFC !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
}

div[style*="background: #FEF2F2"] {
  background: rgba(239, 68, 68, 0.12) !important;
  color: #FECACA !important;
  border-color: rgba(239, 68, 68, 0.3) !important;
}

div[style*="background: #EFF6FF"] {
  background: rgba(59, 130, 246, 0.12) !important;
  color: #BFDBFE !important;
  border-color: rgba(59, 130, 246, 0.3) !important;
}

div[style*="background: #F0FDF4"] {
  background: rgba(16, 185, 129, 0.12) !important;
  color: #A7F3D0 !important;
  border-color: rgba(16, 185, 129, 0.3) !important;
}

div[style*="color: #0F172A"],
div[style*="color: #0f172a"],
div[style*="color: #1E293B"],
div[style*="color: #1e293b"],
div[style*="color: #334155"],
span[style*="color: #0F172A"],
span[style*="color: #1E293B"],
span[style*="color: #334155"],
p[style*="color: #0F172A"],
p[style*="color: #1E293B"],
p[style*="color: #334155"],
h2[style*="color: #0F172A"],
h3[style*="color: #0F172A"],
h4[style*="color: #0F172A"] {
  color: #F8FAFC !important;
}

div[style*="color: #64748B"],
span[style*="color: #64748B"],
div[style*="color: #475569"],
span[style*="color: #475569"],
p[style*="color: #64748B"],
p[style*="color: #475569"] {
  color: #94A3B8 !important;
}

div[style*="border: 1px solid #E2E8F0"],
div[style*="border: 1px solid #CBD5E1"],
div[style*="border-bottom: 1px solid #E2E8F0"],
div[style*="border-bottom: 1px solid #CBD5E1"],
div[style*="border-top: 1px solid #E2E8F0"] {
  border-color: rgba(255, 255, 255, 0.08) !important;
}"""

    if dark_overrides_target in html:
        html = html.replace(dark_overrides_target, enhanced_dark_overrides)
        print("Enhanced dark theme overrides successfully!")

    # Check if podium is already present in tab-summary
    if '<!-- EXECUTIVE PODIUM SPOTLIGHT' not in html:
        hero_end_marker = """            <a href="outputs/SupeRR_Selector_Methodology_Report_v4_Top1.pdf" target="_blank" class="btn-hero-outline">
              📄 Official 5-Page PDF Report
            </a>
          </div>
        </div>"""

        podium_html = """            <a href="outputs/SupeRR_Selector_Methodology_Report_v4_Top1.pdf" target="_blank" class="btn-hero-outline">
              📄 Official 5-Page PDF Report
            </a>
          </div>
        </div>

        <!-- EXECUTIVE PODIUM SPOTLIGHT (TOP 3 BATTERS & TOP 3 BOWLERS) -->
        <div class="dugout-podium-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 16px; margin-bottom: 22px;">
          <!-- BATTERS PODIUM -->
          <div style="background: linear-gradient(135deg, #091A33 0%, #0D2447 100%); border: 1px solid rgba(229, 0, 125, 0.3); border-radius: 12px; padding: 18px 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px;">🏏</span>
                <span style="font-weight: 800; font-size: 14px; color: #FFFFFF; letter-spacing: -0.01em;">Top Pressure Batters</span>
                <span style="background: rgba(229,0,125,0.25); color: #FFB3D9; font-size: 10px; font-family: var(--font-mono); padding: 2px 6px; border-radius: 4px; font-weight: 700;">OFFICIAL TOP 3</span>
              </div>
              <button onclick="setRole('batters'); switchTab('tab-leaderboards')" style="background: transparent; border: none; color: #38BDF8; font-size: 11px; font-weight: 700; cursor: pointer;">View All 10 &rarr;</button>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
              <div onclick="openPlayerProfile('Suryakumar Yadav')" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 8px; cursor: pointer; transition: transform 0.15s ease;">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="background: #F59E0B; color: #041126; font-weight: 900; font-size: 11px; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">1</span>
                  <div>
                    <div style="font-weight: 800; font-size: 13px; color: #FFFFFF;">Suryakumar Yadav <span style="font-size: 11px; color: #94A3B8; font-weight: 500;">(MI &bull; 🇮🇳)</span></div>
                    <div style="font-size: 10.5px; color: #94A3B8; font-family: var(--font-mono);">442 HP Balls &bull; SR 180.3 &bull; &Delta; +13.5</div>
                  </div>
                </div>
                <div style="text-align: right;">
                  <div style="font-weight: 900; font-size: 13px; color: #34D399; font-family: var(--font-mono);">+17.2 <span style="font-size: 9px; color: #94A3B8;">Net/100</span></div>
                  <div style="font-size: 10px; color: #FFB3D9; font-weight: 700;">Score: 0.672</div>
                </div>
              </div>

              <div onclick="openPlayerProfile('Phil Salt')" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; cursor: pointer;">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="background: rgba(255,255,255,0.15); color: #FFFFFF; font-weight: 800; font-size: 11px; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">2</span>
                  <div>
                    <div style="font-weight: 800; font-size: 13px; color: #FFFFFF;">Phil Salt <span style="font-size: 11px; color: #94A3B8; font-weight: 500;">(KKR &bull; 🏴󠁧󠁢󠁥󠁮󠁧󠁿)</span></div>
                    <div style="font-size: 10.5px; color: #94A3B8; font-family: var(--font-mono);">254 HP Balls &bull; SR 177.6 &bull; &Delta; +6.2</div>
                  </div>
                </div>
                <div style="text-align: right;">
                  <div style="font-weight: 900; font-size: 13px; color: #34D399; font-family: var(--font-mono);">+13.9 <span style="font-size: 9px; color: #94A3B8;">Net/100</span></div>
                  <div style="font-size: 10px; color: #FFB3D9; font-weight: 700;">Score: 0.441</div>
                </div>
              </div>

              <div onclick="openPlayerProfile('Tim David')" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; cursor: pointer;">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="background: rgba(255,255,255,0.15); color: #FFFFFF; font-weight: 800; font-size: 11px; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">3</span>
                  <div>
                    <div style="font-weight: 800; font-size: 13px; color: #FFFFFF;">Tim David <span style="font-size: 11px; color: #94A3B8; font-weight: 500;">(MI &bull; 🇦🇺)</span></div>
                    <div style="font-size: 10.5px; color: #94A3B8; font-family: var(--font-mono);">279 HP Balls &bull; SR 171.3 &bull; &Delta; +5.4</div>
                  </div>
                </div>
                <div style="text-align: right;">
                  <div style="font-weight: 900; font-size: 13px; color: #34D399; font-family: var(--font-mono);">+12.8 <span style="font-size: 9px; color: #94A3B8;">Net/100</span></div>
                  <div style="font-size: 10px; color: #FFB3D9; font-weight: 700;">Score: 0.428</div>
                </div>
              </div>
            </div>
          </div>

          <!-- BOWLERS PODIUM -->
          <div style="background: linear-gradient(135deg, #091A33 0%, #0D2447 100%); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 18px 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px;">🎯</span>
                <span style="font-weight: 800; font-size: 14px; color: #FFFFFF; letter-spacing: -0.01em;">Top Pressure Bowlers</span>
                <span style="background: rgba(56, 189, 248, 0.2); color: #7DD3FC; font-size: 10px; font-family: var(--font-mono); padding: 2px 6px; border-radius: 4px; font-weight: 700;">OFFICIAL TOP 3</span>
              </div>
              <button onclick="setRole('bowlers'); switchTab('tab-leaderboards')" style="background: transparent; border: none; color: #38BDF8; font-size: 11px; font-weight: 700; cursor: pointer;">View All 10 &rarr;</button>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
              <div onclick="openPlayerProfile('Sunil Narine')" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 8px; cursor: pointer; transition: transform 0.15s ease;">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="background: #F59E0B; color: #041126; font-weight: 900; font-size: 11px; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">1</span>
                  <div>
                    <div style="font-weight: 800; font-size: 13px; color: #FFFFFF;">Sunil Narine <span style="font-size: 11px; color: #94A3B8; font-weight: 500;">(KKR &bull; 🏝️)</span></div>
                    <div style="font-size: 10.5px; color: #94A3B8; font-family: var(--font-mono);">545 HP Balls &bull; Econ 6.12 &bull; Dots 46.8%</div>
                  </div>
                </div>
                <div style="text-align: right;">
                  <div style="font-weight: 900; font-size: 13px; color: #34D399; font-family: var(--font-mono);">+19.4 <span style="font-size: 9px; color: #94A3B8;">Saved/100</span></div>
                  <div style="font-size: 10px; color: #7DD3FC; font-weight: 700;">Score: 0.680</div>
                </div>
              </div>

              <div onclick="openPlayerProfile('Mitchell Santner')" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; cursor: pointer;">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="background: rgba(255,255,255,0.15); color: #FFFFFF; font-weight: 800; font-size: 11px; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">2</span>
                  <div>
                    <div style="font-weight: 800; font-size: 13px; color: #FFFFFF;">Mitchell Santner <span style="font-size: 11px; color: #94A3B8; font-weight: 500;">(CSK/MI &bull; 🇳🇿)</span></div>
                    <div style="font-size: 10.5px; color: #94A3B8; font-family: var(--font-mono);">274 HP Balls &bull; Econ 6.38 &bull; Dots 42.7%</div>
                  </div>
                </div>
                <div style="text-align: right;">
                  <div style="font-weight: 900; font-size: 13px; color: #34D399; font-family: var(--font-mono);">+14.8 <span style="font-size: 9px; color: #94A3B8;">Saved/100</span></div>
                  <div style="font-size: 10px; color: #7DD3FC; font-weight: 700;">Score: 0.493</div>
                </div>
              </div>

              <div onclick="openPlayerProfile('Jacob Duffy')" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; cursor: pointer;">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="background: rgba(255,255,255,0.15); color: #FFFFFF; font-weight: 800; font-size: 11px; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">3</span>
                  <div>
                    <div style="font-weight: 800; font-size: 13px; color: #FFFFFF;">Jacob Duffy <span style="font-size: 11px; color: #94A3B8; font-weight: 500;">(RCB &bull; 🇳🇿)</span></div>
                    <div style="font-size: 10.5px; color: #94A3B8; font-family: var(--font-mono);">205 HP Balls &bull; Econ 6.82 &bull; Dots 41.5%</div>
                  </div>
                </div>
                <div style="text-align: right;">
                  <div style="font-weight: 900; font-size: 13px; color: #34D399; font-family: var(--font-mono);">+14.1 <span style="font-size: 9px; color: #94A3B8;">Saved/100</span></div>
                  <div style="font-size: 10px; color: #7DD3FC; font-weight: 700;">Score: 0.482</div>
                </div>
              </div>
            </div>
          </div>
        </div>"""
        
        if hero_end_marker in html:
            html = html.replace(hero_end_marker, podium_html)
            print("Added executive podium spotlight to tab-summary!")

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("UI overhaul written to index.html successfully.")

if __name__ == '__main__':
    overhaul_ui()
