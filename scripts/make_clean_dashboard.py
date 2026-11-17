import re

def clean_dashboard():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Clean up light backgrounds in inline styles
    # Replace common light background patterns with clean dark surfaces
    replacements = [
        # Light card backgrounds
        (r'background:\s*#F8FAFC;', 'background: #091A33;'),
        (r'background:\s*#f8fafc;', 'background: #091A33;'),
        (r'background:\s*#F1F5F9;', 'background: rgba(255, 255, 255, 0.05);'),
        (r'background:\s*#f1f5f9;', 'background: rgba(255, 255, 255, 0.05);'),
        (r'background:\s*#F4F6FA;', 'background: #091A33;'),
        (r'background:\s*#EFF6FF;', 'background: rgba(56, 189, 248, 0.08);'),
        (r'background:\s*#FAF5FF;', 'background: rgba(168, 85, 247, 0.08);'),
        (r'background:\s*#DCFCE7;', 'background: rgba(16, 185, 129, 0.12);'),
        (r'background:\s*#FFF1F7;', 'background: rgba(229, 0, 125, 0.1);'),
        (r'background:\s*#FEF3C7;', 'background: rgba(245, 158, 11, 0.15);'),
        (r'background:\s*#FEF2F2;', 'background: rgba(239, 68, 68, 0.1);'),
        
        # In specific inline card containers
        ('background: #FFFFFF; border: 1px solid var(--rr-border);', 'background: #08162B; border: 1px solid rgba(255,255,255,0.08);'),
        ('background: #FFFFFF;', 'background: #08162B;'),
        ('background: #fff;', 'background: #08162B;'),
        
        # Light borders
        (r'border:\s*1px\s+solid\s+#E2E8F0;', 'border: 1px solid rgba(255, 255, 255, 0.08);'),
        (r'border:\s*1px\s+solid\s+#CBD5E1;', 'border: 1px solid rgba(255, 255, 255, 0.08);'),
        (r'border:\s*1px\s+solid\s+#BFDBFE;', 'border: 1px solid rgba(56, 189, 248, 0.25);'),
        (r'border:\s*1px\s+solid\s+#E9D5FF;', 'border: 1px solid rgba(168, 85, 247, 0.25);'),
        (r'border:\s*1px\s+solid\s+#BBF7D0;', 'border: 1px solid rgba(16, 185, 129, 0.25);'),
        (r'border:\s*1px\s+solid\s+#FCE7F3;', 'border: 1px solid rgba(229, 0, 125, 0.25);'),
        (r'border:\s*1px\s+solid\s+#FDE68A;', 'border: 1px solid rgba(245, 158, 11, 0.35);'),

        # Dark texts that need to be crisp light text
        (r'color:\s*#0F172A;', 'color: #F8FAFC;'),
        (r'color:\s*#0f172a;', 'color: #F8FAFC;'),
        (r'color:\s*#1E293B;', 'color: #F8FAFC;'),
        (r'color:\s*#1e293b;', 'color: #F8FAFC;'),
        (r'color:\s*#334155;', 'color: #CBD5E1;'),
        (r'color:\s*#475569;', 'color: #94A3B8;'),
        (r'color:\s*#64748B;', 'color: #94A3B8;'),
        ('color: var(--rr-navy);', 'color: #FFFFFF;')
    ]

    for pat, rep in replacements:
        if pat.startswith('(') or '\\' in pat or 'r\'' in str(type(pat)):
            html = re.sub(pat, rep, html)
        else:
            html = html.replace(pat, rep)

    # 2. Refine the Section A summary box
    old_sec_a = """          <div style="background: #091A33; border-left: 4px solid var(--rr-navy); padding: 14px 18px; border-radius: 8px; font-size: 13px; line-height: 1.6; color: #F8FAFC;">
            <strong>Method Summary:</strong>"""

    new_sec_a = """          <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid var(--rr-pink); padding: 16px 20px; border-radius: 8px; font-size: 13px; line-height: 1.65; color: #E2E8F0;">
            <strong style="color: #FFFFFF; font-size: 13.5px;">Method Summary:</strong>"""

    html = html.replace(old_sec_a, new_sec_a)

    # 3. Refine Header buttons for a clean, cohesive top bar
    old_header_controls = """        <div class="toggle-group" id="toggle-container">
          <button id="btn-toggle-adj" class="toggle-btn active" onclick="setView('adjusted')">Opposition-Adjusted</button>
          <button id="btn-toggle-orig" class="toggle-btn" onclick="setView('original')">Original Model</button>
        </div>

        <button onclick="switchTab('tab-3d-playground')" class="btn-header-action" title="Open 3D Data Universe Playground" style="background: linear-gradient(135deg, rgba(229,0,125,0.3) 0%, rgba(56,189,248,0.3) 100%); border-color: #38BDF8; box-shadow: 0 0 12px rgba(56,189,248,0.25);">
          <span>🌐 3D Playground</span>
        </button>

        <button onclick="openShortlistDrawer()" class="btn-header-action btn-shortlist-counter" title="Open RR Shortlist Drawer">
          <span>★ Shortlist</span>
          <span id="shortlist-badge-count" class="font-mono bg-white text-rrPink px-1.5 py-0.5 rounded text-[10px] font-black">0</span>
        </button>

        <button onclick="switchTab('tab-duel')" class="btn-header-action" title="Open Matchup Duel Simulator (Illustrative toy, not a model output)" style="background: rgba(229,0,125,0.25); border-color: var(--rr-pink);">
          <span>⚔️ Duel Sim (Illustrative)</span>
        </button>

        <button onclick="switchTab('tab-submission')" class="btn-header-action" title="Open Unstop Submission Hub" style="background: rgba(139,92,246,0.25); border-color: #8B5CF6;">
          <span>📋 Unstop Text</span>
        </button>

        <button onclick="openSelectorsSheet()" class="btn-header-action" title="View Executive Selector's Sheet">
          <span>📄 Selector's Sheet</span>
        </button>

        <button onclick="window.print()" class="btn-header-action" title="Export PDF / Print View">
          <span>🖨️ Export PDF</span>
        </button>"""

    new_header_controls = """        <div class="toggle-group" id="toggle-container">
          <button id="btn-toggle-adj" class="toggle-btn active" onclick="setView('adjusted')">⚡ Opposition-Adjusted</button>
          <button id="btn-toggle-orig" class="toggle-btn" onclick="setView('original')">📊 Original Model</button>
        </div>

        <button onclick="switchTab('tab-3d-playground')" class="btn-header-action" title="Open 3D Data Universe Playground" style="background: rgba(56, 189, 248, 0.12); border-color: rgba(56, 189, 248, 0.35); color: #7DD3FC;">
          <span>🌐 3D Universe</span>
        </button>

        <button onclick="switchTab('tab-duel')" class="btn-header-action" title="Open Matchup Duel Simulator (Illustrative toy, not a model output)">
          <span>⚔️ Duel Sim</span>
        </button>

        <button onclick="switchTab('tab-submission')" class="btn-header-action" title="Open Unstop Submission Hub">
          <span>📋 Unstop Hub</span>
        </button>

        <button onclick="openSelectorsSheet()" class="btn-header-action" title="View Executive Selector's Sheet">
          <span>📄 Sheet</span>
        </button>

        <button onclick="openShortlistDrawer()" class="btn-header-action btn-shortlist-counter" title="Open RR Shortlist Drawer">
          <span>★ Shortlist</span>
          <span id="shortlist-badge-count" class="font-mono bg-white text-rrPink px-1.5 py-0.5 rounded text-[10px] font-black">0</span>
        </button>

        <button onclick="window.print()" class="btn-header-action" title="Export PDF / Print View" style="padding: 7px 10px;">
          <span>🖨️</span>
        </button>"""

    if old_header_controls in html:
        html = html.replace(old_header_controls, new_header_controls)
        print("Replaced header controls with clean, consolidated layout!")
    else:
        print("Warning: old_header_controls not matched exactly, checking substring...")

    # 4. Refine Left Navigation Rail
    old_nav_rail = """    <!-- LEFT NAVIGATION RAIL -->
    <aside class="nav-rail no-print">
      <div class="nav-section-label" style="color: #38BDF8;">3D Data Playground</div>
      <button onclick="switchTab('tab-3d-playground')" id="nav-tab-3d-playground" class="nav-btn" style="border: 1px solid rgba(56, 189, 248, 0.3); background: rgba(56, 189, 248, 0.08); margin-bottom: 6px;">
        <span class="nav-icon">🌐</span>
        <span style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
          <span>3D Data Universe</span>
          <span style="background: linear-gradient(135deg, var(--rr-pink) 0%, #38BDF8 100%); color: #FFFFFF; font-size: 8px; font-weight: 900; padding: 1px 5px; border-radius: 4px;">3D LIVE</span>
        </span>
      </button>

      <div class="nav-section-label">Core Evaluation</div>
      <button onclick="switchTab('tab-summary')" id="nav-tab-summary" class="nav-btn active">
        <span class="nav-icon">📊</span>
        <span>Executive Summary</span>
      </button>
      <button onclick="switchTab('tab-leaderboards')" id="nav-tab-leaderboards" class="nav-btn">
        <span class="nav-icon">🏆</span>
        <span>Top 10 Leaderboards</span>
      </button>
      <button onclick="switchTab('tab-scatter')" id="nav-tab-scatter" class="nav-btn">
        <span class="nav-icon">⚡</span>
        <span>Pressure Scatter</span>
      </button>
      <button onclick="switchTab('tab-slope')" id="nav-tab-slope" class="nav-btn">
        <span class="nav-icon">📈</span>
        <span>Rank Movement</span>
      </button>

      <div class="nav-section-label">Model Mechanics</div>
      <button onclick="switchTab('tab-stability')" id="nav-tab-stability" class="nav-btn">
        <span class="nav-icon">🎲</span>
        <span>Stability &amp; Robustness</span>
      </button>
      <button onclick="switchTab('tab-leverage')" id="nav-tab-leverage" class="nav-btn">
        <span class="nav-icon">⚖️</span>
        <span>Leverage &amp; Calibration</span>
      </button>
      <button onclick="switchTab('tab-weights')" id="nav-tab-weights" class="nav-btn">
        <span class="nav-icon">🎛️</span>
        <span>Weight Lab</span>
      </button>
      <button onclick="switchTab('tab-compare')" id="nav-tab-compare" class="nav-btn">
        <span class="nav-icon">👥</span>
        <span>Player Comparison</span>
      </button>

            <div class="nav-section-label" style="color: var(--rr-pink);">Tactical Dugout Suite</div>
      <button onclick="switchTab('tab-duel')" id="nav-tab-duel" class="nav-btn">
        <span class="nav-icon">⚔️</span>
        <span>Matchup Duel Simulator (Illustrative)</span>
      </button>
      <button onclick="switchTab('tab-tactics')" id="nav-tab-tactics" class="nav-btn">
        <span class="nav-icon">🎯</span>
        <span>Pace/Spin &amp; Phase Splits</span>
      </button>
      <button onclick="switchTab('tab-submission')" id="nav-tab-submission" class="nav-btn">
        <span class="nav-icon">📋</span>
        <span>Unstop Submission Hub</span>
      </button>

<div class="nav-section-label">Auction Strategy</div>
      <button onclick="switchTab('tab-auction')" id="nav-tab-auction" class="nav-btn">
        <span class="nav-icon">🏷️</span>
        <span>Auction &amp; Retention</span>
      </button>
      <button onclick="switchTab('tab-auction'); setTimeout(() => { document.getElementById('rr-squad-audit-table-body')?.scrollIntoView({behavior: 'smooth', block: 'center'}); }, 100);" id="nav-tab-rrsquad" class="nav-btn">
        <span class="nav-icon">🏰</span>
        <span>RR Squad Pressure Audit</span>
      </button>
      <button onclick="switchTab('tab-top1')" id="nav-tab-top1" class="nav-btn">
        <span class="nav-icon">🎯</span>
        <span>Top-1 Recommendation</span>
      </button>
      <button onclick="switchTab('tab-notable')" id="nav-tab-notable" class="nav-btn">
        <span class="nav-icon">⭐</span>
        <span>Notable Names</span>
      </button>

      <div class="nav-section-label">Integrity &amp; Auditing</div>
      <button onclick="switchTab('tab-limitations')" id="nav-tab-limitations" class="nav-btn">
        <span class="nav-icon">⚠️</span>
        <span>Limitations &amp; Nuance</span>
      </button>
      <button onclick="switchTab('tab-audit')" id="nav-tab-audit" class="nav-btn">
        <span class="nav-icon">🔍</span>
        <span>Source Audit</span>
      </button>
    </aside>"""

    new_nav_rail = """    <!-- LEFT NAVIGATION RAIL -->
    <aside class="nav-rail no-print">
      <div class="nav-section-label">Evaluation</div>
      <button onclick="switchTab('tab-summary')" id="nav-tab-summary" class="nav-btn active">
        <span class="nav-icon">📊</span>
        <span>Executive Summary</span>
      </button>
      <button onclick="switchTab('tab-leaderboards')" id="nav-tab-leaderboards" class="nav-btn">
        <span class="nav-icon">🏆</span>
        <span>Top 10 Leaderboards</span>
      </button>
      <button onclick="switchTab('tab-3d-playground')" id="nav-tab-3d-playground" class="nav-btn">
        <span class="nav-icon">🌐</span>
        <span style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
          <span>3D Data Universe</span>
          <span style="background: rgba(56, 189, 248, 0.2); color: #7DD3FC; font-size: 8px; font-weight: 800; padding: 1px 4px; border-radius: 3px; font-family: var(--font-mono);">3D</span>
        </span>
      </button>

      <div class="nav-section-label">Tactical Splits</div>
      <button onclick="switchTab('tab-tactics')" id="nav-tab-tactics" class="nav-btn">
        <span class="nav-icon">🎯</span>
        <span>Pace/Spin &amp; Phases</span>
      </button>
      <button onclick="switchTab('tab-scatter')" id="nav-tab-scatter" class="nav-btn">
        <span class="nav-icon">⚡</span>
        <span>Pressure Scatter</span>
      </button>
      <button onclick="switchTab('tab-slope')" id="nav-tab-slope" class="nav-btn">
        <span class="nav-icon">📈</span>
        <span>Rank Movement</span>
      </button>

      <div class="nav-section-label">Dugout War Room</div>
      <button onclick="switchTab('tab-auction'); setTimeout(() => { document.getElementById('rr-squad-audit-table-body')?.scrollIntoView({behavior: 'smooth', block: 'center'}); }, 100);" id="nav-tab-rrsquad" class="nav-btn">
        <span class="nav-icon">🏰</span>
        <span>RR Squad Pressure</span>
      </button>
      <button onclick="switchTab('tab-duel')" id="nav-tab-duel" class="nav-btn">
        <span class="nav-icon">⚔️</span>
        <span>Matchup Duel Sim</span>
      </button>
      <button onclick="switchTab('tab-compare')" id="nav-tab-compare" class="nav-btn">
        <span class="nav-icon">👥</span>
        <span>Player Comparison</span>
      </button>

      <div class="nav-section-label">Model &amp; Audit</div>
      <button onclick="switchTab('tab-stability')" id="nav-tab-stability" class="nav-btn">
        <span class="nav-icon">🎲</span>
        <span>Stability (Bootstraps)</span>
      </button>
      <button onclick="switchTab('tab-leverage')" id="nav-tab-leverage" class="nav-btn">
        <span class="nav-icon">⚖️</span>
        <span>Leverage &amp; Calibration</span>
      </button>
      <button onclick="switchTab('tab-submission')" id="nav-tab-submission" class="nav-btn">
        <span class="nav-icon">📋</span>
        <span>Unstop Submission Hub</span>
      </button>
      <button onclick="switchTab('tab-audit')" id="nav-tab-audit" class="nav-btn">
        <span class="nav-icon">🔍</span>
        <span>Source Audit Console</span>
      </button>
    </aside>"""

    if old_nav_rail in html:
        html = html.replace(old_nav_rail, new_nav_rail)
        print("Replaced nav rail with clean, organized sections!")

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Clean dashboard upgrades applied successfully!")

if __name__ == '__main__':
    clean_dashboard()
