import re
import sys

def apply_clean_ui():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Replace all dark text colors that should be light text in dark mode
    html = html.replace('color: var(--rr-navy);', 'color: #F8FAFC;')
    html = html.replace('color:var(--rr-navy);', 'color: #F8FAFC;')
    html = html.replace('color: #1E293B;', 'color: #F8FAFC;')
    html = html.replace('color: #0F172A;', 'color: #F8FAFC;')
    html = html.replace('color: #334155;', 'color: #CBD5E1;')
    html = html.replace('color: #475569;', 'color: #94A3B8;')

    # 2. Add comprehensive CSS overrides in <style>
    css_overrides = """
/* =========================================================================
   CLEAN LUXURY DUGOUT DESIGN SYSTEM OVERRIDES
   ========================================================================= */
[style*="color: var(--rr-navy)"],
[style*="color:var(--rr-navy)"],
[style*="color: #1E293B"],
[style*="color: #1e293b"],
[style*="color: #0F172A"],
[style*="color: #0f172a"] {
  color: #F8FAFC !important;
}

[style*="color: #334155"],
[style*="color: #475569"] {
  color: #CBD5E1 !important;
}

/* Ensure all modal and drawer content is crisp and clean */
.drawer-panel, .modal-content {
  background: #08162B !important;
  color: #F8FAFC !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
}

.drawer-header {
  background: #041126 !important;
  border-bottom: 2px solid var(--rr-pink) !important;
  color: #FFFFFF !important;
}

.drawer-body, .modal-body {
  background: #08162B !important;
  color: #F8FAFC !important;
}

/* High-contrast form controls and filters */
select, input[type="text"], input[type="number"] {
  background: #091A33 !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  color: #F8FAFC !important;
  border-radius: 6px !important;
  padding: 6px 10px !important;
}

select:focus, input:focus {
  border-color: #38BDF8 !important;
  outline: none !important;
}

/* Clean up table search input containers */
div[style*="background: rgba(255, 255, 255, 0.05)"] {
  background: #091A33 !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
}

/* Clean scorecards */
.scorecard-table th {
  background: #0B1E38 !important;
  color: #94A3B8 !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.scorecard-table tbody tr {
  background: #08162B;
}

.scorecard-table tbody tr:nth-child(even) {
  background: #0B1D36 !important;
}

.scorecard-table tbody tr:hover {
  background: #132E58 !important;
}

.scorecard-table th.sticky-col-rank,
.scorecard-table th.sticky-col-player {
  background: #0B1E38 !important;
  color: #F8FAFC !important;
}

.sticky-col-rank {
  background-color: #08162B !important;
  color: #CBD5E1 !important;
}

.scorecard-table tbody tr:nth-child(even) .sticky-col-rank {
  background-color: #0B1D36 !important;
}

.scorecard-table tbody tr:hover .sticky-col-rank {
  background-color: #132E58 !important;
}

.sticky-col-player {
  background-color: #08162B !important;
  color: #FFFFFF !important;
}

.scorecard-table tbody tr:nth-child(even) .sticky-col-player {
  background-color: #0B1D36 !important;
}

.scorecard-table tbody tr:hover .sticky-col-player {
  background-color: #132E58 !important;
}
"""

    if '/* CLEAN LUXURY DUGOUT DESIGN SYSTEM OVERRIDES */' not in html:
        html = html.replace('</style>', css_overrides + '\n</style>')
        print("Added clean luxury dugout CSS overrides!")

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Clean UI overhaul applied successfully!")

if __name__ == '__main__':
    apply_clean_ui()
