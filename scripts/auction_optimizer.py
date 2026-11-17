"""
Rajasthan Royals IPL 2027 Auction War-Room Knapsack Optimizer
Solves an exact Mixed-Integer Linear Program (MILP) to find the mathematically
optimal 18-player Rajasthan Royals squad maximizing High-Pressure Expected Value (EV)
under real IPL budget and squad composition constraints.
"""
import pandas as pd
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

# 1. Load Player Universe & Scores
av = pd.read_csv('availability.csv')
r_opp = pd.read_pickle('res_main_opp.pkl')

# Merge scores
scores = {}
for role in ['bat', 'bowl']:
    for pid, row in r_opp[role].iterrows():
        scores[(role, int(pid))] = row.score

av['model_score'] = av.apply(lambda r: scores.get((r.role, int(r.pid)), 0.0), axis=1)

# Filter out Pakistani players (ineligible) and retired players
market = av[~av.nationality.eq('Pakistan') & ~av.status.str.startswith('Believed')].copy()

# Add realistic estimated auction valuations (₹ Crore)
def estimate_cost(row):
    name = row['name']
    t = str(row.ipl2026)
    role = row.role
    sc = row.model_score
    
    # Existing core RR retentions
    if name == 'Vaibhav Sooryavanshi': return 1.10
    if name == 'Jofra Archer': return 12.50
    if name == 'Sanju Samson': return 18.00
    if name == 'Yashasvi Jaiswal': return 18.00
    if name == 'Riyan Parag': return 14.00
    if name == 'Dhruv Jurel': return 14.00
    if name == 'Shimron Hetmyer': return 11.00
    if name == 'Sandeep Sharma': return 4.00
    
    # Marquee external players (if available)
    if 'Suryakumar' in name: return 18.00
    if 'Salt' in name: return 11.50
    if 'Tim David' in name: return 9.00
    if 'Gill' in name: return 16.50
    if 'Pooran' in name: return 14.00
    if 'Abhishek Sharma' in name: return 14.00
    if 'Narine' in name: return 12.00
    if 'Santner' in name: return 6.00
    if 'Pathirana' in name: return 13.00
    if 'Hazlewood' in name: return 10.00
    
    # High-value unattached auction targets
    if name == 'Mohit Sharma': return 3.50
    if name == 'Harry Brook': return 6.50
    if name == 'Sediqullah Atal': return 1.50
    if name == 'Mujeeb Ur Rahman': return 2.50
    if name == 'Tim Southee': return 2.00
    if name == 'Glenn Maxwell': return 5.50
    if name == 'Andre Russell': return 8.00
    if name == 'Jacob Duffy': return 2.00
    if name == 'Lockie Ferguson': return 5.00
    if name == 'Taskin Ahmed': return 2.00
    if name == 'Tim Seifert': return 2.00
    if name == 'Mark Chapman': return 1.50
    if name == 'Krunal Pandya': return 6.50
    if name == 'Axar Patel': return 16.00
    if name == 'Varun Chakravarthy': return 12.00
    
    # Default model-based price tier
    base = 1.00
    if sc > 0.40: base = 5.00
    elif sc > 0.25: base = 3.00
    elif sc > 0.10: base = 1.50
    else: base = 0.50
    return base

market['est_cost_cr'] = market.apply(estimate_cost, axis=1)

# Categorize Tactical Roles
def tag_role(row):
    r = row.role
    name = row['name']
    if name in ['Phil Salt', 'Nicholas Pooran', 'Tim Seifert', 'Dhruv Jurel', 'Sanju Samson', 'Shai Hope']:
        return 'WK'
    if r == 'bat':
        if row.model_score > 0.35: return 'TopOrder_Finisher'
        return 'Batter'
    if r == 'bowl':
        if name in ['Sunil Narine', 'Mitchell Santner', 'Abrar Ahmed', 'Krunal Pandya', 'Mujeeb Ur Rahman', 'Varun Chakravarthy', 'Axar Patel']:
            return 'Spin'
        return 'Pace'
    return 'Other'

market['tactical_role'] = market.apply(tag_role, axis=1)
market = market.drop_duplicates(subset=['role', 'pid']).reset_index(drop=True)

# -------------------------------------------------------------
# MILP Optimization Setup
# Maximize: sum(model_score * x_i)
# Constraints:
# 1. Total players = 18
# 2. Total cost <= 120 Cr
# 3. Overseas players <= 8
# 4. Mandatory RR core assets (Vaibhav Sooryavanshi, Jofra Archer) must be included
# 5. At least 2 Wicketkeepers
# 6. At least 6 Batters / Top-Order
# 7. At least 3 Spinners
# 8. At least 5 Pacers
# -------------------------------------------------------------

N = len(market)
c = -market.model_score.values  # minimize negative score to maximize score

# Constraints matrix
A_rows = []
b_l = []
b_u = []

# 1. Total players == 18
A_rows.append(np.ones(N))
b_l.append(18)
b_u.append(18)

# 2. Total cost <= 120.0 Cr
A_rows.append(market.est_cost_cr.values)
b_l.append(0.0)
b_u.append(120.0)

# 3. Overseas <= 8
A_rows.append((market.overseas == 'Yes').astype(float).values)
b_l.append(0.0)
b_u.append(8.0)

# 4. Minimum 2 WKs
A_rows.append((market.tactical_role == 'WK').astype(float).values)
b_l.append(2.0)
b_u.append(18.0)

# 5. Minimum 6 Batters (including WKs and Top-order)
A_rows.append((market.role == 'bat').astype(float).values)
b_l.append(6.0)
b_u.append(18.0)

# 6. Minimum 3 Spinners
A_rows.append((market.tactical_role == 'Spin').astype(float).values)
b_l.append(3.0)
b_u.append(18.0)

# 7. Minimum 5 Pacers
A_rows.append((market.tactical_role == 'Pace').astype(float).values)
b_l.append(5.0)
b_u.append(18.0)

# 8. Mandatory inclusions: Vaibhav Sooryavanshi & Jofra Archer
vaibhav_idx = market[market['name'] == 'Vaibhav Sooryavanshi'].index[0]
archer_idx = market[market['name'] == 'Jofra Archer'].index[0]

v_row = np.zeros(N); v_row[vaibhav_idx] = 1.0
A_rows.append(v_row); b_l.append(1.0); b_u.append(1.0)

a_row = np.zeros(N); a_row[archer_idx] = 1.0
A_rows.append(a_row); b_l.append(1.0); b_u.append(1.0)

A = np.vstack(A_rows)
constraints = LinearConstraint(A, b_l, b_u)
integrality = np.ones(N)  # all binary variables
bounds = Bounds(0, 1)

res = milp(c=c, integrality=integrality, constraints=constraints, bounds=bounds)

if res.success:
    selected_indices = np.where(res.x > 0.5)[0]
    squad = market.iloc[selected_indices].copy().sort_values(['role', 'model_score'], ascending=[True, False])
    total_cost = squad.est_cost_cr.sum()
    total_score = squad.model_score.sum()
    overseas_count = (squad.overseas == 'Yes').sum()
    
    squad['ev_per_cr'] = (squad.model_score / squad.est_cost_cr).round(3)
    squad.to_csv('optimal_rr_squad_2027.csv', index=False)
    
    print("=== MILP OPTIMIZATION SOLVED SUCCESSFULLY ===")
    print(f"Optimal Squad Size: {len(squad)} players")
    print(f"Total Projected Purse Spent: ₹{total_cost:.2f} Cr / ₹120.00 Cr (Purse Remaining: ₹{120-total_cost:.2f} Cr)")
    print(f"Overseas Slots Used: {overseas_count} / 8")
    print(f"Aggregated Squad High-Pressure Model Score: {total_score:.3f}")
    print("\nOPTIMAL SQUAD LIST:")
    print(squad[['name', 'role', 'tactical_role', 'nationality', 'overseas', 'est_cost_cr', 'model_score', 'ev_per_cr']].to_string(index=False))
else:
    print("Optimization failed:", res.status)

