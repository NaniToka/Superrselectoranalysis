#!/usr/bin/env python3
"""
Build real ball-by-ball Tactical Blueprint & Evidence Vault data from b3.pkl.

Joins b3.pkl with data/raw/matches.csv, data/raw/teams.csv (keyed cleanly on
(comp_id, team_id)), and data/raw/competitions.csv to extract high-leverage
execution matrices, delivery/stroke distributions, match/ball receipts,
historical H2H records, and RR 2026-27 matchup blueprints.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
B3_PATH = ROOT / "b3.pkl"
MATCHES_CSV = ROOT / "data" / "raw" / "matches.csv"
TEAMS_CSV = ROOT / "data" / "raw" / "teams.csv"
COMPETITIONS_CSV = ROOT / "data" / "raw" / "competitions.csv"
INDEX_HTML = ROOT / "index.html"
OUT_JSON = ROOT / "data" / "tactical_blueprint_data.json"

ATTACKING_STROKES = {
    "Pull shot",
    "Cover Drive",
    "Off Drive",
    "Square Cut",
    "On drive",
    "Square drive",
    "Slog",
    "Straight Drive",
    "Slog Sweep",
    "Sweep Shot",
    "Paddle Scoop",
    "Reverse Sweep",
    "UpperCut",
    "PickUp",
    "Inside out",
    "Late Cut",
    "Hook Shot",
    "Paddle Sweep",
    "Reverse Paddle Scoop",
    "Switch",
}

ROTATION_STROKES = {
    "Worked",
    "Flick",
    "Push",
    "Steer",
    "Leg Glance",
    "Glance",
}

DEFENSIVE_STROKES = {
    "Frontfoot defensive",
    "Backfoot defensive",
    "Defense",
    "Intentional Padding",
}

TEAM_SHORT = {
    "Rajasthan Royals": "RR",
    "Mumbai Indians": "MI",
    "Chennai Super Kings": "CSK",
    "Kolkata Knight Riders": "KKR",
    "Royal Challengers Bengaluru": "RCB",
    "Sunrisers Hyderabad": "SRH",
    "Gujarat Titans": "GT",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Lucknow Super Giants": "LSG",
}


def classify_stroke_posture(stroke: Any) -> str:
    """Map raw ball-by-ball stroke label to Attacking, Rotation, Defensive, or Unrecorded."""
    if pd.isna(stroke):
        return "Unrecorded"
    s = str(stroke).strip()
    if s in ATTACKING_STROKES:
        return "Attacking"
    if s in ROTATION_STROKES:
        return "Rotation"
    if s in DEFENSIVE_STROKES:
        return "Defensive"
    return "Other"


def extract_app_data(html_path: Path = INDEX_HTML) -> dict[str, Any]:
    """Read embedded const APP_DATA JSON object from index.html."""
    html = html_path.read_text(encoding="utf-8")
    m = re.search(
        r"const APP_DATA\s*=\s*(\{.*?\});\s*(?:const|let|var|\n\s*//)",
        html,
        re.DOTALL,
    )
    if not m:
        raise ValueError(f"Could not locate const APP_DATA in {html_path}")
    return json.loads(m.group(1))


def load_enriched_deliveries() -> tuple[pd.DataFrame, pd.DataFrame, float]:
    """
    Load b3.pkl, filter canonical innings 1-2 with non-null LI, attach venue,
    competition metadata, and exact (comp_id, team_id) batting/bowling team names.
    """
    b3 = pd.read_pickle(B3_PATH)
    df = b3[b3["innings"].isin([1, 2]) & b3["LI"].notna()].copy()

    matches = pd.read_csv(
        MATCHES_CSV,
        usecols=["match_id", "venue_id", "venue_country", "home_team", "away_team", "stage"],
    ).drop_duplicates("match_id")
    teams = pd.read_csv(TEAMS_CSV, usecols=["comp_id", "team_id", "team_name"]).drop_duplicates(
        ["comp_id", "team_id"]
    )
    comps = pd.read_csv(
        COMPETITIONS_CSV, usecols=["comp_id", "comp_name", "match_format", "season"]
    ).drop_duplicates("comp_id")

    team_lookup = {
        (int(r.comp_id), int(r.team_id)): str(r.team_name)
        for r in teams.itertuples(index=False)
    }

    df = df.merge(
        matches.rename(columns={"stage": "match_stage"}),
        on="match_id",
        how="left",
    )
    df = df.merge(comps, on="comp_id", how="left")

    df["bat_team_name"] = [
        team_lookup.get((int(c), int(t)), f"Team {int(t)}")
        if pd.notna(c) and pd.notna(t)
        else "Unknown"
        for c, t in zip(df["comp_id"], df["batting_team_id"])
    ]
    df["bowl_team_name"] = [
        team_lookup.get((int(c), int(t)), f"Team {int(t)}")
        if pd.notna(c) and pd.notna(t)
        else "Unknown"
        for c, t in zip(df["comp_id"], df["bowling_team_id"])
    ]

    df["stroke_posture"] = df["stroke"].map(classify_stroke_posture)
    li_q75 = float(df["LI"].quantile(0.75))
    hp = df[df["LI"] >= li_q75].copy()
    return df, hp, li_q75


def build_featured_cohort(app_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Build deduplicated list of (pid, role) targets covering:
      - Top 20 batters & Top 20 bowlers (opposition-adjusted)
      - All 15 RR 2026 contracted roster entries
      - Top contracted stars across all 10 IPL franchises (up to 6 bat + 6 bowl per team)
    """
    all_players = app_data.get("adjusted_all_players", [])
    rr_audit = app_data.get("rr_squad_audit", [])

    selected: dict[tuple[int, str], dict[str, Any]] = {}

    def register(rec: dict[str, Any], tag: str) -> None:
        pid = rec.get("pid")
        role = rec.get("role")
        if pid is None or role not in ("bat", "bowl"):
            return
        key = (int(pid), role)
        if key not in selected:
            entry = {
                "pid": int(pid),
                "name": str(rec.get("name", "")),
                "role": role,
                "ipl2026": str(rec.get("ipl2026", "") or ""),
                "nationality": str(rec.get("nationality", "") or ""),
                "adjusted_rank": rec.get("adjusted_rank"),
                "adjusted_score": rec.get("adjusted_score"),
                "net_hp_adj": rec.get("net_hp"),
                "wpa_hp_adj": rec.get("wpa_hp"),
                "n_hp_model": rec.get("n_hp"),
                "tags": [],
            }
            selected[key] = entry
        if tag not in selected[key]["tags"]:
            selected[key]["tags"].append(tag)

    for rec in rr_audit:
        register(rec, "RR_2026")

    for role in ("bat", "bowl"):
        role_rows = sorted(
            [p for p in all_players if p.get("role") == role],
            key=lambda x: x.get("adjusted_rank") or 9999,
        )
        for rec in role_rows[:20]:
            register(rec, "TOP_20")

        for team_full in TEAM_SHORT:
            team_rows = [p for p in role_rows if p.get("ipl2026") == team_full]
            for rec in team_rows[:6]:
                register(rec, f"IPL_{TEAM_SHORT[team_full]}")

    # Ensure Jasprit Bumrah is always included even if ranked outside cutoff in either mode
    for rec in all_players:
        if rec.get("name") == "Jasprit Bumrah" and rec.get("role") == "bowl":
            register(rec, "BENCHMARK_PACE")

    return sorted(
        selected.values(),
        key=lambda r: (
            0 if "RR_2026" in r["tags"] else 1,
            0 if r["role"] == "bat" else 1,
            r["adjusted_rank"] or 9999,
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Tactical Blueprint Vault dataset.")
    parser.add_argument("--check-cohort", action="store_true", help="Print cohort stats only.")
    args = parser.parse_args()

    app_data = extract_app_data()
    cohort = build_featured_cohort(app_data)
    df, hp, li_q75 = load_enriched_deliveries()

    print(
        json.dumps(
            {
                "total_balls": int(len(df)),
                "hp_balls": int(len(hp)),
                "li_q75": round(li_q75, 4),
                "cohort_entries": len(cohort),
                "bat_entries": sum(1 for c in cohort if c["role"] == "bat"),
                "bowl_entries": sum(1 for c in cohort if c["role"] == "bowl"),
                "rr_entries": sum(1 for c in cohort if "RR_2026" in c["tags"]),
            },
            indent=2,
        )
    )
    if args.check_cohort:
        return


if __name__ == "__main__":
    main()
