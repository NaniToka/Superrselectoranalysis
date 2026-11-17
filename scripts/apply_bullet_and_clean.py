import re
import sys

def apply_bullet_and_clean():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. New Spacious Bullet Points for Section A Method Summary
    # Exact text preserved for integrity check:
    # '958 players', '100 batters and 102 bowlers qualify',
    # 'extras1_runs is a type code; byes and leg-bye runs are unrecorded',
    # 'leave-one-match-out', '3.73 percentage points', '0.62 percentage points',
    # '200 match-level bootstrap resamples', 'Round 2 in Mumbai', 'Round 3 in Goa'

    old_sec_a_regex = r'<div style="background:\s*rgba\(255,\s*255,\s*255,\s*0\.03\);[\s\S]*?Round 3 in Goa for the Round 2 winner\.\s*</div>'

    new_sec_a_html = """<div class="method-summary-bullet-container" style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px;">
            <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid var(--rr-pink); border-radius: 10px; padding: 16px 20px;">
              <div style="display: flex; align-items: flex-start; gap: 12px;">
                <span style="font-size: 20px; line-height: 1.2;">🎯</span>
                <div style="font-size: 15px; line-height: 1.7; color: #F1F5F9;">
                  <strong style="color: #FFFFFF; font-size: 15.5px;">Leverage-Based Pressure Definition:</strong> We define pressure as how much the next delivery can move the match (a leverage index built from a win-probability model), rather than a hand-picked list of over and run-rate rules.
                </div>
              </div>
            </div>

            <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid #38BDF8; border-radius: 10px; padding: 16px 20px;">
              <div style="display: flex; align-items: flex-start; gap: 12px;">
                <span style="font-size: 20px; line-height: 1.2;">📊</span>
                <div style="font-size: 15px; line-height: 1.7; color: #F1F5F9;">
                  <strong style="color: #FFFFFF; font-size: 15.5px;">Dataset Scope &amp; Structural Data Quality:</strong> The source data covers IPL and T20I matches from 2022 to 2026 (<strong>958 players</strong> total; <strong>extras1_runs is a type code; byes and leg-bye runs are unrecorded</strong>).
                </div>
              </div>
            </div>

            <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid #F59E0B; border-radius: 10px; padding: 16px 20px;">
              <div style="display: flex; align-items: flex-start; gap: 12px;">
                <span style="font-size: 20px; line-height: 1.2;">⚡</span>
                <div style="font-size: 15px; line-height: 1.7; color: #F1F5F9;">
                  <strong style="color: #FFFFFF; font-size: 15.5px;">Continuous High-Pressure Cutoff (Top Quartile):</strong> Deliveries in the top quartile (LI &ge; 1.32; 49,276 deliveries) are classified as high pressure, where win-probability swing averages <strong>3.73 percentage points</strong> per ball compared to <strong>0.62 percentage points</strong> in ordinary situations.
                </div>
              </div>
            </div>

            <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid #10B981; border-radius: 10px; padding: 16px 20px;">
              <div style="display: flex; align-items: flex-start; gap: 12px;">
                <span style="font-size: 20px; line-height: 1.2;">🛡️</span>
                <div style="font-size: 15px; line-height: 1.7; color: #F1F5F9;">
                  <strong style="color: #FFFFFF; font-size: 15.5px;">Rigorous Eligibility Hurdles:</strong> Eligibility requires at least 150 high-pressure deliveries, 8 high-pressure matches (6+ balls each), and 100 ordinary deliveries: <strong>100 batters and 102 bowlers qualify</strong>.
                </div>
              </div>
            </div>

            <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid #A855F7; border-radius: 10px; padding: 16px 20px;">
              <div style="display: flex; align-items: flex-start; gap: 12px;">
                <span style="font-size: 20px; line-height: 1.2;">⚖️</span>
                <div style="font-size: 15px; line-height: 1.7; color: #F1F5F9;">
                  <strong style="color: #FFFFFF; font-size: 15.5px;">Empirical Bayes 4-Pillar Convergence:</strong> Each qualified player is scored on Pressure Value (35%), Win Probability Added (30%), Delta vs own baseline (20%), and Consistency (15%), with Empirical Bayes shrinkage applied.
                </div>
              </div>
            </div>

            <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid #EC4899; border-radius: 10px; padding: 16px 20px;">
              <div style="display: flex; align-items: flex-start; gap: 12px;">
                <span style="font-size: 20px; line-height: 1.2;">🔄</span>
                <div style="font-size: 15px; line-height: 1.7; color: #F1F5F9;">
                  <strong style="color: #FFFFFF; font-size: 15.5px;">Opposition Normalization &amp; Cross-Validation:</strong> In the adjusted model, opposition quality is normalized via <strong>leave-one-match-out</strong> ratings to neutralize associate-level distortions.
                </div>
              </div>
            </div>

            <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid #06B6D4; border-radius: 10px; padding: 16px 20px;">
              <div style="display: flex; align-items: flex-start; gap: 12px;">
                <span style="font-size: 20px; line-height: 1.2;">🎲</span>
                <div style="font-size: 15px; line-height: 1.7; color: #F1F5F9;">
                  <strong style="color: #FFFFFF; font-size: 15.5px;">Bootstrap Resample Validation &amp; Tournament Path:</strong> Rankings are evaluated across <strong>200 match-level bootstrap resamples</strong> for the adjusted model (300 for the original model), in preparation for <strong>Round 2 in Mumbai</strong> and <strong>Round 3 in Goa</strong> for the Round 2 winner.
                </div>
              </div>
            </div>
          </div>"""

    m = re.search(old_sec_a_regex, html)
    if m:
        html = html[:m.start()] + new_sec_a_html + html[m.end():]
        print("Replaced dense Method Summary paragraph with spacious 15px bullet points!")
    else:
        print("Warning: old_sec_a_regex did not match, trying direct string search...")
        # fallback search
        target = "Method Summary:</strong> We define pressure"
        idx = html.find(target)
        if idx != -1:
            start_div = html.rfind('<div', 0, idx)
            end_div = html.find('</div>', idx) + 6
            html = html[:start_div] + new_sec_a_html + html[end_div:]
            print("Found via fallback and replaced with bullet points!")

    # 2. Increase font sizes and padding in Dugout Flowchart and 4 Pillars
    old_flowchart = """          <!-- DUGOUT 6-STAGE FLOWCHART -->
          <div style="margin-top: 18px; padding: 16px; background: var(--rr-navy-900); border-radius: 10px; color: #FFFFFF;">
            <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #FF85C0; margin-bottom: 10px;">
              Dugout Decision Architecture (From Ball Event to Auction Target)
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; text-align: center; font-size: 11px; font-family: var(--font-mono);">
              <div style="background: rgba(255,255,255,0.06); padding: 10px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
                <div style="color: #FF85C0; font-weight: 700;">1. Ball Event</div>
                <div style="font-size: 9px; color: #CBD5E1; margin-top: 2px;">197,100 Deliveries</div>
              </div>
              <div style="background: rgba(255,255,255,0.06); padding: 10px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
                <div style="color: #FF85C0; font-weight: 700;">2. Win Prob</div>
                <div style="font-size: 9px; color: #CBD5E1; margin-top: 2px;">Calibrated AUC 0.89</div>
              </div>
              <div style="background: rgba(255,255,255,0.06); padding: 10px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
                <div style="color: #FF85C0; font-weight: 700;">3. Leverage LI</div>
                <div style="font-size: 9px; color: #CBD5E1; margin-top: 2px;">Top 25% (LI &ge; 1.32)</div>
              </div>
              <div style="background: rgba(255,255,255,0.06); padding: 10px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
                <div style="color: #FF85C0; font-weight: 700;">4. Value Added</div>
                <div style="font-size: 9px; color: #CBD5E1; margin-top: 2px;">&lambda; Wicket Run Valuation</div>
              </div>
              <div style="background: rgba(255,255,255,0.06); padding: 10px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
                <div style="color: #FF85C0; font-weight: 700;">5. EB Shrink</div>
                <div style="font-size: 9px; color: #CBD5E1; margin-top: 2px;">Shrink Small Samples</div>
              </div>
              <div style="background: var(--rr-pink); padding: 10px 8px; border-radius: 6px; font-weight: 700;">
                <div style="color: #FFFFFF;">6. Auction Pool</div>
                <div style="font-size: 9px; color: #FFF0F6; margin-top: 2px;">Option B &amp; RR Targets</div>
              </div>
            </div>
          </div>"""

    new_flowchart = """          <!-- DUGOUT 6-STAGE FLOWCHART -->
          <div style="margin-top: 22px; padding: 20px; background: rgba(4, 17, 38, 0.9); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; color: #FFFFFF;">
            <div style="font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #FF85C0; margin-bottom: 14px;">
              Dugout Decision Architecture (From Ball Event to Auction Target)
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; text-align: center; font-family: var(--font-mono);">
              <div style="background: rgba(255,255,255,0.05); padding: 12px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12);">
                <div style="color: #FF85C0; font-weight: 800; font-size: 13px;">1. Ball Event</div>
                <div style="font-size: 11px; color: #E2E8F0; margin-top: 3px;">197,100 Deliveries</div>
              </div>
              <div style="background: rgba(255,255,255,0.05); padding: 12px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12);">
                <div style="color: #38BDF8; font-weight: 800; font-size: 13px;">2. Win Prob</div>
                <div style="font-size: 11px; color: #E2E8F0; margin-top: 3px;">Calibrated AUC 0.89</div>
              </div>
              <div style="background: rgba(255,255,255,0.05); padding: 12px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12);">
                <div style="color: #F59E0B; font-weight: 800; font-size: 13px;">3. Leverage LI</div>
                <div style="font-size: 11px; color: #E2E8F0; margin-top: 3px;">Top 25% (LI &ge; 1.32)</div>
              </div>
              <div style="background: rgba(255,255,255,0.05); padding: 12px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12);">
                <div style="color: #34D399; font-weight: 800; font-size: 13px;">4. Value Added</div>
                <div style="font-size: 11px; color: #E2E8F0; margin-top: 3px;">&lambda; Wicket Run Valuation</div>
              </div>
              <div style="background: rgba(255,255,255,0.05); padding: 12px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12);">
                <div style="color: #C084FC; font-weight: 800; font-size: 13px;">5. EB Shrink</div>
                <div style="font-size: 11px; color: #E2E8F0; margin-top: 3px;">Shrink Small Samples</div>
              </div>
              <div style="background: var(--rr-pink); padding: 12px 10px; border-radius: 8px; font-weight: 800; box-shadow: 0 4px 14px rgba(229,0,125,0.4);">
                <div style="color: #FFFFFF; font-size: 13px;">6. Auction Pool</div>
                <div style="font-size: 11px; color: #FFF0F6; margin-top: 3px;">Option B &amp; RR Targets</div>
              </div>
            </div>
          </div>"""

    if old_flowchart in html:
        html = html.replace(old_flowchart, new_flowchart)
        print("Updated Dugout Flowchart to larger, spacious fonts!")

    # 3. Increase font sizes in 4 Pillars Grid
    old_pillars = """          <!-- 4 PILLARS GRID -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-top: 18px;">
            <div style="background: var(--rr-pink-light); border: 1px solid var(--rr-pink-subtle); padding: 14px; border-radius: 10px;">
              <div style="font-size: 10px; font-weight: 800; color: var(--rr-pink); text-transform: uppercase;">1. Pressure Value (35%)</div>
              <div style="font-size: 14px; font-weight: 800; color: #F8FAFC; margin-top: 2px;">Runs Above Expected</div>
              <p style="font-size: 11px; color: var(--rr-text-muted); margin-top: 4px;">
                Bat runs minus expected runs, with wickets valued contextually: &lambda; &approx; 8.3 (PP), 6.0 (Mid), 2.8 (Death).
              </p>
            </div>

            <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.25); padding: 14px; border-radius: 10px;">
              <div style="font-size: 10px; font-weight: 800; color: #1D4ED8; text-transform: uppercase;">2. Win Prob Added (30%)</div>
              <div style="font-size: 14px; font-weight: 800; color: #F8FAFC; margin-top: 2px;">Win Probability Added (WPA)</div>
              <p style="font-size: 11px; color: var(--rr-text-muted); margin-top: 4px;">
                Direct change in calibrated win probability (&Delta;WP) produced by execution on high-pressure balls.
              </p>
            </div>

            <div style="background: rgba(168, 85, 247, 0.08); border: 1px solid rgba(168, 85, 247, 0.25); padding: 14px; border-radius: 10px;">
              <div style="font-size: 10px; font-weight: 800; color: #7E22CE; text-transform: uppercase;">3. Elevation Gap (20%)</div>
              <div style="font-size: 14px; font-weight: 800; color: #F8FAFC; margin-top: 2px;">Delta vs Baseline</div>
              <p style="font-size: 11px; color: var(--rr-text-muted); margin-top: 4px;">
                Separates situational elevation from general baseline skill: net_HP minus net_ordinary on the same player.
              </p>
            </div>

            <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.25); padding: 14px; border-radius: 10px;">
              <div style="font-size: 10px; font-weight: 800; color: #047857; text-transform: uppercase;">4. Consistency (15%)</div>
              <div style="font-size: 14px; font-weight: 800; color: #F8FAFC; margin-top: 2px;">Bayesian Hit-Rate</div>
              <p style="font-size: 11px; color: var(--rr-text-muted); margin-top: 4px;">
                (Hits + 4) / (Matches + 8), where a hit requires &ge;6 HP balls and positive net value. Shrunk with 8 pseudo-matches at 50%.
              </p>
            </div>
          </div>"""

    new_pillars = """          <!-- 4 PILLARS GRID -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-top: 20px;">
            <div style="background: rgba(229, 0, 125, 0.09); border: 1px solid rgba(229, 0, 125, 0.28); padding: 18px; border-radius: 10px;">
              <div style="font-size: 11px; font-weight: 800; color: var(--rr-pink); text-transform: uppercase; letter-spacing: 0.06em;">1. Pressure Value (35%)</div>
              <div style="font-size: 16px; font-weight: 800; color: #FFFFFF; margin-top: 4px;">Runs Above Expected</div>
              <p style="font-size: 13px; line-height: 1.6; color: #CBD5E1; margin-top: 6px;">
                Bat runs minus expected runs, with wickets valued contextually: &lambda; &approx; 8.3 (PP), 6.0 (Mid), 2.8 (Death).
              </p>
            </div>

            <div style="background: rgba(56, 189, 248, 0.09); border: 1px solid rgba(56, 189, 248, 0.28); padding: 18px; border-radius: 10px;">
              <div style="font-size: 11px; font-weight: 800; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.06em;">2. Win Prob Added (30%)</div>
              <div style="font-size: 16px; font-weight: 800; color: #FFFFFF; margin-top: 4px;">Win Probability Added (WPA)</div>
              <p style="font-size: 13px; line-height: 1.6; color: #CBD5E1; margin-top: 6px;">
                Direct change in calibrated win probability (&Delta;WP) produced by execution on high-pressure balls.
              </p>
            </div>

            <div style="background: rgba(168, 85, 247, 0.09); border: 1px solid rgba(168, 85, 247, 0.28); padding: 18px; border-radius: 10px;">
              <div style="font-size: 11px; font-weight: 800; color: #C084FC; text-transform: uppercase; letter-spacing: 0.06em;">3. Elevation Gap (20%)</div>
              <div style="font-size: 16px; font-weight: 800; color: #FFFFFF; margin-top: 4px;">Delta vs Baseline</div>
              <p style="font-size: 13px; line-height: 1.6; color: #CBD5E1; margin-top: 6px;">
                Separates situational elevation from general baseline skill: net_HP minus net_ordinary on the same player.
              </p>
            </div>

            <div style="background: rgba(16, 185, 129, 0.09); border: 1px solid rgba(16, 185, 129, 0.28); padding: 18px; border-radius: 10px;">
              <div style="font-size: 11px; font-weight: 800; color: #34D399; text-transform: uppercase; letter-spacing: 0.06em;">4. Consistency (15%)</div>
              <div style="font-size: 16px; font-weight: 800; color: #FFFFFF; margin-top: 4px;">Bayesian Hit-Rate</div>
              <p style="font-size: 13px; line-height: 1.6; color: #CBD5E1; margin-top: 6px;">
                (Hits + 4) / (Matches + 8), where a hit requires &ge;6 HP balls and positive net value. Shrunk with 8 pseudo-matches at 50%.
              </p>
            </div>
          </div>"""

    if old_pillars in html:
        html = html.replace(old_pillars, new_pillars)
        print("Updated 4 Pillars Grid to 16px headers and 13px descriptions!")

    # 4. REMOVE UNSTOP HUB FEATURE
    # A. Remove Unstop Hub from Header
    unstop_header_btn = """        <button onclick="switchTab('tab-submission')" class="btn-header-action" title="Open Unstop Submission Hub">
          <span>📋 Unstop Hub</span>
        </button>"""
    if unstop_header_btn in html:
        html = html.replace(unstop_header_btn, '')
        print("Removed Unstop Hub button from top header!")

    # B. Remove Unstop Hub from Left Navigation Rail
    unstop_nav_btn = """      <button onclick="switchTab('tab-submission')" id="nav-tab-submission" class="nav-btn">
        <span class="nav-icon">📋</span>
        <span>Unstop Submission Hub</span>
      </button>"""
    if unstop_nav_btn in html:
        html = html.replace(unstop_nav_btn, '')
        print("Removed Unstop Hub button from left navigation rail!")

    # C. Remove Unstop Hub from Mobile Bottom Sheet
    unstop_mob_btn = """      <button class="mobile-sheet-item" onclick="mobileSwitchTab('tab-submission')"><span>📋</span> Unstop Hub</button>"""
    if unstop_mob_btn in html:
        html = html.replace(unstop_mob_btn, '')
        print("Removed Unstop Hub from mobile bottom sheet!")

    # D. Ensure Bumrah verified facts are placed safely inside tab-limitations
    # '506 deliveries', '42.2% dot balls', '125.4', '20 wickets', '27.8 expected', '+15.73 Net/100', '-11.19', 'untested in the data pack'
    bumrah_card_html = """
            <!-- THE SUPERSTAR PARADOX EXPLAINER (JASPRIT BUMRAH CASE STUDY) -->
            <div style="background: #091A33; border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid var(--rr-pink); border-radius: 8px; padding: 18px; margin-top: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 800; font-size: 14px; color: #F8FAFC;">Case Study: Analysis of Jasprit Bumrah (Rank #24 Adjusted &bull; Rank #26 Original)</span>
                <span class="badge" style="background: rgba(255,255,255,0.08); color: #94A3B8; font-size: 10px; padding: 2px 6px; border-radius: 4px;">Untested Cause</span>
              </div>
              <p style="font-size: 13px; line-height: 1.6; color: #CBD5E1; margin: 0;">
                In high-pressure deliveries (LI &ge; 1.32), Jasprit Bumrah has <strong>506 deliveries</strong>, with <strong>42.2% dot balls</strong>, a batter strike rate of <strong>125.4</strong>, and <strong>20 wickets</strong> against <strong>27.8 expected</strong>. His pressure value is <strong>+15.73 Net/100</strong>, while his ordinary-level gap (Delta) is <strong>-11.19</strong>. While one possible explanation is that opposing batters adopt an unusually risk-averse approach against him, <em>the underlying cause (e.g. batter risk aversion vs. match state vs. execution) is untested in the data pack</em>.
              </p>
            </div>"""

    if '<!-- THE SUPERSTAR PARADOX EXPLAINER (JASPRIT BUMRAH CASE STUDY) -->' not in html:
        # Insert inside tab-limitations right after Known Model Limitations
        target_limitations_div = '</ul>\n            </div>'
        if target_limitations_div in html:
            html = html.replace(target_limitations_div, target_limitations_div + bumrah_card_html, 1)
            print("Safely embedded verified Bumrah case study in Section F Limitations & Nuance!")

    # E. Hide or remove tab-submission section
    # Replace tab-submission with hidden container or remove
    html = re.sub(r'<!-- TAB: UNSTOP SUBMISSION HUB -->[\s\S]*?</section>', '', html)
    print("Completely purged tab-submission section from HTML!")

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Script finished successfully.")

if __name__ == '__main__':
    apply_bullet_and_clean()
