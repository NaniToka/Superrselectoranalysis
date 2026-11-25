"""Automated static & structural UI smoke verifier for Rajasthan Royals SupeRR Selector."""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

BASE_DIR = sys.argv[1] if len(sys.argv) > 1 else "."
HTML_PATH = os.path.join(BASE_DIR, "index.html")


def main() -> int:
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    checks = 0

    def assert_ok(cond: bool, msg: str) -> None:
        nonlocal checks
        checks += 1
        if not cond:
            raise AssertionError(msg)

    # 1. Zero unrendered raw $...$ LaTeX fragments in visible markup or JS template strings
    bad_latex = []
    for idx, line in enumerate(html.splitlines(), 1):
        st = line.strip()
        if "const APP_DATA =" in line or st.startswith("//"):
            continue
        for m in re.finditer(r"\$[A-Za-z_\[\\][^$\n]{0,40}\$", line):
            bad_latex.append((idx, m.group(0)))
    assert_ok(len(bad_latex) == 0, f"Unrendered $LaTeX$ found: {bad_latex}")

    # 2. Validate every switchTab('...') target exists as a DOM section
    section_ids = set(re.findall(r'<section[^>]+id=["\'](tab-[^"\']+)["\']', html))
    tab_calls = set(re.findall(r"switchTab\(['\"](tab-[^'\"]+)['\"]\)", html))
    missing_tabs = sorted(t for t in tab_calls if t not in section_ids)
    assert_ok(len(missing_tabs) == 0, f"switchTab references missing tab IDs: {missing_tabs}")

    # 3. Validate Mumbai Judge Tour steps map to real sections
    tour_match = re.search(r"const MUMBAI_JUDGE_TOUR_STEPS\s*=\s*\[(.*?)\];", html, re.DOTALL)
    assert_ok(bool(tour_match), "Missing MUMBAI_JUDGE_TOUR_STEPS")
    tour_tabs = re.findall(r"tab:\s*['\"](tab-[^'\"]+)['\"]", tour_match.group(1))
    assert_ok(len(tour_tabs) >= 5, f"Expected >=5 tour steps, found {len(tour_tabs)}")
    for tt in tour_tabs:
        assert_ok(tt in section_ids, f"Tour step targets missing section '{tt}'")

    # 4. Validate Engine dropdown item count matches badge
    dd_match = re.search(
        r'<div id="tactical-dropdown-menu".*?<div class="dropdown-grid">(.*?)</div>\s*</div>\s*</div>',
        html,
        re.DOTALL,
    )
    assert_ok(bool(dd_match), "Missing #tactical-dropdown-menu")
    items = re.findall(r'class="dropdown-item"', dd_match.group(1))
    tag = re.search(r'<span class="dropdown-header-tag">(\d+) ENGINES READY</span>', html)
    assert_ok(bool(tag) and int(tag.group(1)) == len(items), "Dropdown badge mismatch")

    # 5. Validate tactical dropdown positioning prevents left clipping & bottom overflow
    dd_css = re.search(r"\.tactical-dropdown-menu\s*\{(.*?)\}", html, re.DOTALL)
    assert_ok(bool(dd_css) and "left: 0;" in dd_css.group(1) and "overflow-y: auto;" in dd_css.group(1),
              ".tactical-dropdown-menu missing left alignment or scroll bounds")

    # 6. Validate DLS modal wiring & Team 1 score input
    assert_ok('id="dls-team1-score-input"' in html, "Missing #dls-team1-score-input")
    assert_ok('id="dls-confirm-btn"' in html, "Missing #dls-confirm-btn")
    assert_ok('onclick="applyDlsCurtailedMatch(SELECTED_DLS_CURTAILED_OVERS)"' in html,
              "DLS confirm button not bound to SELECTED_DLS_CURTAILED_OVERS")

    # 7. Validate Powerplay & Fielding geometry rules (rx=105, ry=100 around 250,250)
    pp_match = re.search(r"powerplay:\s*\[(.*?)\]", html, re.DOTALL)
    assert_ok(bool(pp_match), "Missing TACTICAL_FIELD_PRESETS.powerplay")
    coords = re.findall(r"x:\s*(\d+),\s*y:\s*(\d+)", pp_match.group(1))
    assert_ok(len(coords) == 10, f"Expected 10 fielders in powerplay preset, got {len(coords)}")
    outside_pp = sum(
        1 for xs, ys in coords
        if ((int(xs) - 250) ** 2) / (105 ** 2) + ((int(ys) - 250) ** 2) / (100 ** 2) > 1.0
    )
    assert_ok(outside_pp <= 2, f"Powerplay preset illegal: {outside_pp} outside 30-yd ring")

    # 8. Validate empirical lookup & telemetry exporter helpers exist
    assert_ok("function lookupEmpiricalPlayerProfile(" in html, "Missing lookupEmpiricalPlayerProfile")
    assert_ok("function exportLiveMatchTelemetry(" in html, "Missing exportLiveMatchTelemetry")

    # 9. Validate JavaScript syntax of all inline scripts when node is available
    node_bin = shutil.which("node")
    if node_bin:
        scripts = re.findall(r"<script(?:\s+[^>]*)?>(.*?)</script>", html, re.DOTALL)
        for idx, s in enumerate(s for s in scripts if s.strip()):
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tf:
                tf.write(s)
                tpath = tf.name
            try:
                res = subprocess.run([node_bin, "--check", tpath], capture_output=True, text=True)
                assert_ok(res.returncode == 0, f"JS syntax error in script #{idx}: {res.stderr}")
            finally:
                os.unlink(tpath)

    print(f"UI SMOKE VERIFICATION PASSED ({checks} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
