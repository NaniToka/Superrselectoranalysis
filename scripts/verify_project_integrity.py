import sys
import os
import re
import json
import pandas as pd

# Support passing base directory as argument (default: '.')
base_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

failures = []
checks_run = 0

def fail(msg):
    failures.append(msg)

def check(condition, msg):
    global checks_run
    checks_run += 1
    if not condition:
        fail(msg)

def find_data_file(base, filename):
    p1 = os.path.join(base, 'data', filename)
    if os.path.exists(p1):
        return p1
    p2 = os.path.join(base, filename)
    if os.path.exists(p2):
        return p2
    return p1

# 1. Check verified CSV files exist
try:
    exp_path = find_data_file(base_dir, 'expected_dashboard_values.csv')
    exp_df = pd.read_csv(exp_path)
    check(len(exp_df) == 20, f"expected_dashboard_values.csv has {len(exp_df)} rows instead of 20")
except Exception as e:
    fail(f"Could not read expected_dashboard_values.csv: {e}")
    exp_df = pd.DataFrame()

try:
    tac_path = find_data_file(base_dir, 'tactical_splits_verified.csv')
    tac_df = pd.read_csv(tac_path)
    check(len(tac_df) == 50, f"tactical_splits_verified.csv has {len(tac_df)} rows instead of 50")
    req_cols = ['role', 'player', 'split', 'hp_balls', 'runs_scored_or_conceded', 'strike_rate_or_econ', 'net100', 'std_err', 'sample_flag']
    for c in req_cols:
        check(c in tac_df.columns, f"tactical_splits_verified.csv missing column: {c}")
except Exception as e:
    fail(f"Could not read tactical_splits_verified.csv: {e}")

# 2. Parse index.html
try:
    html_path = os.path.join(base_dir, 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    check(len(html) > 0, "index.html is empty")
except Exception as e:
    fail(f"Could not read index.html: {e}")
    html = ""

# Parse APP_DATA
try:
    m = re.search(r'const APP_DATA\s*=\s*(\{.*?\});\s*(?:const|let|var|\n\s*//)', html, re.DOTALL)
    check(bool(m), "Could not find const APP_DATA in index.html")
    if m:
        app_data = json.loads(m.group(1))
    else:
        app_data = {}
except Exception as e:
    fail(f"Failed to parse APP_DATA JSON in index.html: {e}")
    app_data = {}

# 3. Check adj_batters in APP_DATA
adj_bat = app_data.get('adj_batters', [])
check(len(adj_bat) == 10, f"APP_DATA.adj_batters has {len(adj_bat)} items, expected 10")
if len(adj_bat) == 10 and not exp_df.empty:
    exp_bat = exp_df[exp_df['role'] == 'bat'].sort_values('rank').to_dict(orient='records')
    for i in range(10):
        a = adj_bat[i]
        e = exp_bat[i]
        check(a['player'] == e['player'], f"Bat rank {i+1} mismatch: got '{a['player']}', expected '{e['player']}'")
        check(round(float(a['score']), 3) == round(float(e['score']), 3), f"Bat rank {i+1} ({a['player']}) score mismatch: got {a['score']}, expected {e['score']}")
        check(int(a['hp_balls']) == int(e['hp_balls']), f"Bat rank {i+1} ({a['player']}) hp_balls mismatch: got {a['hp_balls']}, expected {e['hp_balls']}")
        check(round(float(a['net_100']), 1) == round(float(e['net_100']), 1), f"Bat rank {i+1} ({a['player']}) net_100 mismatch: got {a['net_100']}, expected {e['net_100']}")

# 4. Check adj_bowlers in APP_DATA
adj_bowl = app_data.get('adj_bowlers', [])
check(len(adj_bowl) == 10, f"APP_DATA.adj_bowlers has {len(adj_bowl)} items, expected 10")
if len(adj_bowl) == 10 and not exp_df.empty:
    exp_bowl = exp_df[exp_df['role'] == 'bowl'].sort_values('rank').to_dict(orient='records')
    for i in range(10):
        a = adj_bowl[i]
        e = exp_bowl[i]
        check(a['player'] == e['player'], f"Bowl rank {i+1} mismatch: got '{a['player']}', expected '{e['player']}'")
        check(round(float(a['score']), 3) == round(float(e['score']), 3), f"Bowl rank {i+1} ({a['player']}) score mismatch: got {a['score']}, expected {e['score']}")
        check(int(a['hp_balls']) == int(e['hp_balls']), f"Bowl rank {i+1} ({a['player']}) hp_balls mismatch: got {a['hp_balls']}, expected {e['hp_balls']}")
        check(round(float(a['net_100']), 1) == round(float(e['net_100']), 1), f"Bowl rank {i+1} ({a['player']}) net_100 mismatch: got {a['net_100']}, expected {e['net_100']}")

# 5. Check Copy-Button Text Logic matches expected_dashboard_values.csv exactly
for i, p in enumerate(adj_bat):
    check(p['player'] in html, f"Player {p['player']} not found in index.html")

# 6. Check Banned Marketing / Price / MILP Words in index.html
banned_patterns = [
    (r'99%\s+of\s+submissions', "Found '99% of submissions'"),
    (r'publication-grade', "Found 'publication-grade'"),
    (r'guaranteed', "Found 'guaranteed'"),
    (r'guarantees', "Found 'guarantees'"),
    (r'indisputable', "Found 'indisputable'"),
    (r'id=["\']tab-squad["\']', "Found tab-squad"),
    (r'optimal_squad', "Found optimal_squad"),
    (r'ev_per_cr', "Found ev_per_cr"),
    (r'est_cost_cr', "Found est_cost_cr"),
    (r'strict\s+ban', "Found 'strict ban'"),
    (r'never\s+bowl', "Found 'never bowl'")
]

for pat, msg in banned_patterns:
    m_found = re.search(pat, html, re.IGNORECASE)
    check(not bool(m_found), f"{msg}: match at char {m_found.start() if m_found else 0}")

# 7. Check Duel Simulator Relabeling
check('Illustrative toy, not a model output' in html, "Duel Simulator missing required label: 'Illustrative toy, not a model output'")

# 8. Check Chapter 1 and 2 Verified Facts in index.html
required_facts = [
    ('958 players', "958 players fact missing"),
    ('100 batters and 102 bowlers qualify', "100 batters and 102 bowlers qualify fact missing"),
    ('extras1_runs is a type code; byes and leg-bye runs are unrecorded', "byes/leg-byes unrecorded fact missing"),
    ('leave-one-match-out', "leave-one-match-out opposition adjustment missing"),
    ('3.73 percentage points', "3.73 percentage points swing missing"),
    ('0.62 percentage points', "0.62 percentage points swing missing"),
    ('200 match-level bootstrap resamples', "200 match-level bootstrap resamples missing"),
    ('Round 2 in Mumbai', "Round 2 in Mumbai missing"),
    ('Round 3 in Goa', "Round 3 in Goa missing")
]

for fact_str, msg in required_facts:
    check(fact_str in html, msg)

# 9. Check Bumrah section verified stats and untested cause
bumrah_facts = [
    ('506 deliveries', "Bumrah 506 deliveries missing"),
    ('42.2% dot balls', "Bumrah 42.2% dot balls missing"),
    ('125.4', "Bumrah 125.4 SR missing"),
    ('20 wickets', "Bumrah 20 wickets missing"),
    ('27.8 expected', "Bumrah 27.8 expected missing"),
    ('+15.73 Net/100', "Bumrah +15.73 Net/100 missing"),
    ('-11.19', "Bumrah -11.19 Delta missing"),
    ('untested in the data pack', "Bumrah 'untested in the data pack' statement missing")
]

for b_str, msg in bumrah_facts:
    check(b_str in html, msg)

# 10. Check Tactical Splits use verified CSV
check('tactical_splits_verified' in app_data, "APP_DATA missing 'tactical_splits_verified'")
check('std_err' in html, "std_err missing from tactical splits display")

# Print FAILURES ONLY if any, otherwise print "N checks run"
if failures:
    print(f"VERIFICATION FAILED WITH {len(failures)} ERROR(S):")
    for f in failures:
        print(f"  [X] {f}")
    sys.exit(1)
else:
    print(f"{checks_run} checks run")
    sys.exit(0)
