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


def summarize_group(sub: pd.DataFrame, role: str) -> dict[str, Any]:
    """Compute exact high-pressure metrics + standard error for any slice of deliveries."""
    n = int(len(sub))
    if n == 0:
        return {
            "n": 0,
            "legal": 0,
            "runs": 0,
            "wkts": 0,
            "sr": None,
            "econ": None,
            "dot_pct": None,
            "boundary_pct": None,
            "net_100": None,
            "std_err": None,
            "wpa_100": None,
            "low_sample": True,
        }

    val_col = "v_bat" if role == "bat" else "v_bowl"
    wpa_col = "wpa_batter" if role == "bat" else "wpa_bowler"
    run_col = "bat_runs" if role == "bat" else "runs"
    wkt_col = "out_striker" if role == "bat" else "wkt_bowler"

    legal = int(sub["legal"].sum())
    runs = int(sub[run_col].sum())
    wkts = int(sub[wkt_col].sum())
    vals = sub[val_col].dropna().astype(float) * 100.0
    net_100 = round(float(vals.mean()), 2) if len(vals) else None
    std_err = round(float(vals.std(ddof=1) / np.sqrt(len(vals))), 2) if len(vals) > 1 else None
    wpas = sub[wpa_col].dropna().astype(float) * 100.0
    wpa_100 = round(float(wpas.mean()), 3) if len(wpas) else None

    dots = int((sub[run_col] == 0).sum()) if role == "bat" else int(((sub["runs"] == 0) & (sub["legal"] == 1)).sum())
    dot_denom = n if role == "bat" else max(legal, 1)
    boundaries = int(((sub["is_four"] == 1) | (sub["is_six"] == 1)).sum())

    return {
        "n": n,
        "legal": legal,
        "runs": runs,
        "wkts": wkts,
        "sr": round(runs / n * 100.0, 1) if n > 0 else None,
        "econ": round(runs / (legal / 6.0), 2) if legal > 0 else None,
        "dot_pct": round(dots / dot_denom * 100.0, 1) if dot_denom > 0 else None,
        "boundary_pct": round(boundaries / n * 100.0, 1) if n > 0 else None,
        "net_100": net_100,
        "std_err": std_err,
        "wpa_100": wpa_100,
        "low_sample": n < 15,
    }


def extract_channel_matrix(player_hp: pd.DataFrame, role: str) -> dict[str, Any]:
    """
    Build Over/Around x Off-side/On-side HP execution matrix, phase splits,
    pace/spin or LHB/RHB matchup splits, and identify the strongest / weakest channel.
    """
    channels: list[dict[str, Any]] = []
    for angle in ("Over", "Around"):
        for line in ("Off-side", "On-side"):
            sub = player_hp[(player_hp["over_or_around"] == angle) & (player_hp["on_or_off"] == line)]
            stats = summarize_group(sub, role)
            stats["angle"] = angle
            stats["line"] = line
            stats["key"] = f"{angle} · {line}"
            channels.append(stats)

    phases = {
        ph: summarize_group(player_hp[player_hp["phase"] == ph], role)
        for ph in ("PP", "MID", "DEATH")
    }

    split_col = "pace_or_spin" if role == "bat" else "batting_type"
    split_vals = ("Pace", "Spin") if role == "bat" else ("LHB", "RHB")
    matchups = {
        sv: summarize_group(player_hp[player_hp[split_col] == sv], role)
        for sv in split_vals
    }

    # Pick reliable (n >= 10, fallback all n > 0) best & vulnerable channel for quick dugout callout
    qualified = [c for c in channels if c["n"] >= 10 and c["net_100"] is not None]
    if not qualified:
        qualified = [c for c in channels if c["n"] > 0 and c["net_100"] is not None]

    best_chan = max(qualified, key=lambda c: c["net_100"]) if qualified else None
    weak_chan = min(qualified, key=lambda c: c["net_100"]) if qualified else None

    return {
        "overall": summarize_group(player_hp, role),
        "matrix": channels,
        "phases": phases,
        "matchups": matchups,
        "best_channel": best_chan["key"] if best_chan else None,
        "best_net": best_chan["net_100"] if best_chan else None,
        "weak_channel": weak_chan["key"] if weak_chan else None,
        "weak_net": weak_chan["net_100"] if weak_chan else None,
    }


def extract_delivery_and_stroke_profile(player_hp: pd.DataFrame, role: str) -> dict[str, Any]:
    """
    Extract delivery_style stats, pace speed-band breakdowns (<135, 135-142, >142 kph),
    top stroke distribution, stroke posture mix, and top dismissal stroke traps.
    """
    style_rows: list[dict[str, Any]] = []
    style_counts = player_hp["delivery_style"].dropna().value_counts()
    for style_name, _ in style_counts.head(6).items():
        sub = player_hp[player_hp["delivery_style"] == style_name]
        st = summarize_group(sub, role)
        st["style"] = str(style_name)
        style_rows.append(st)

    pace_sub = player_hp[(player_hp["pace_or_spin"] == "Pace") & (player_hp["bowl_speed"] > 0)]
    speed_bands: list[dict[str, Any]] = []
    band_defs = [
        ("<135 kph", pace_sub["bowl_speed"] < 135.0),
        ("135-142 kph", (pace_sub["bowl_speed"] >= 135.0) & (pace_sub["bowl_speed"] <= 142.0)),
        (">142 kph", pace_sub["bowl_speed"] > 142.0),
    ]
    for label, mask in band_defs:
        sub = pace_sub[mask]
        st = summarize_group(sub, role)
        st["band"] = label
        speed_bands.append(st)

    n_total = max(int(len(player_hp)), 1)
    posture_counts = player_hp["stroke_posture"].value_counts().to_dict()
    posture_pct = {
        k: round(int(posture_counts.get(k, 0)) / n_total * 100.0, 1)
        for k in ("Attacking", "Rotation", "Defensive", "Unrecorded")
    }

    stroke_rows: list[dict[str, Any]] = []
    stroke_counts = player_hp["stroke"].dropna().value_counts()
    for stroke_name, _ in stroke_counts.head(5).items():
        sub = player_hp[player_hp["stroke"] == stroke_name]
        st = summarize_group(sub, role)
        st["stroke"] = str(stroke_name)
        st["posture"] = classify_stroke_posture(stroke_name)
        stroke_rows.append(st)

    wkt_col = "out_striker" if role == "bat" else "wkt_bowler"
    wkt_sub = player_hp[player_hp[wkt_col] == 1].copy()
    wkt_sub["trap_label"] = [
        f"{str(s) if pd.notna(s) else 'Unrecorded'} ({str(dt) if pd.notna(dt) else 'Out'})"
        for s, dt in zip(wkt_sub["stroke"], wkt_sub["dismissal_type"])
    ]
    traps = [
        {"trap": str(lbl), "outs": int(cnt)}
        for lbl, cnt in wkt_sub["trap_label"].value_counts().head(5).items()
    ]

    return {
        "delivery_styles": style_rows,
        "speed_bands": speed_bands,
        "posture_pct": posture_pct,
        "top_strokes": stroke_rows,
        "dismissal_traps": traps,
    }


def _short_comp_label(comp_name: Any, season: Any) -> str:
    """Create readable compact competition label from full competition name."""
    if pd.isna(comp_name):
        return f"T20 ({int(season)})" if pd.notna(season) else "T20"
    name = str(comp_name)
    if "Indian Premier League" in name or "IPL" in name:
        return f"IPL {int(season)}" if pd.notna(season) else "IPL"
    if "T20 World Cup" in name:
        return f"T20 WC {int(season)}" if pd.notna(season) else "T20 WC"
    words = name.split()
    return " ".join(words[:3])


def extract_player_receipts(player_hp: pd.DataFrame, role: str, limit: int = 6) -> list[dict[str, Any]]:
    """
    Select top real high-leverage deliveries for a player across distinct matches:
    mixes peak positive WPA swings and key dismissal/boundary turning points.
    """
    if len(player_hp) == 0:
        return []

    wpa_col = "wpa_batter" if role == "bat" else "wpa_bowler"
    val_col = "v_bat" if role == "bat" else "v_bowl"
    wkt_col = "out_striker" if role == "bat" else "wkt_bowler"
    run_col = "bat_runs" if role == "bat" else "runs"
    other_col = "bowler_name" if role == "bat" else "striker_name"
    opp_col = "bowl_team_name" if role == "bat" else "bat_team_name"

    work = player_hp.copy()
    work["abs_wpa"] = work[wpa_col].fillna(0.0).abs()
    work["impact_score"] = work["abs_wpa"] * 100.0 + work[wkt_col].fillna(0) * 6.0 + (
        (work["is_six"] == 1) * 2.5
    )

    # First pick strongest moment per match to ensure multi-match diversity
    best_per_match = work.sort_values(["impact_score", "LI"], ascending=[False, False]).drop_duplicates(
        "match_id"
    )
    chosen = best_per_match.head(limit)
    if len(chosen) < limit:
        rem = work.loc[~work.index.isin(chosen.index)].sort_values(
            ["impact_score", "LI"], ascending=[False, False]
        )
        chosen = pd.concat([chosen, rem.head(limit - len(chosen))])

    receipts: list[dict[str, Any]] = []
    for r in chosen.itertuples(index=False):
        angle = getattr(r, "over_or_around", None)
        line = getattr(r, "on_or_off", None)
        channel = (
            f"{angle} · {line}"
            if pd.notna(angle) and pd.notna(line)
            else (str(line) if pd.notna(line) else "Recorded")
        )
        spd = getattr(r, "bowl_speed", None)
        is_out = bool(getattr(r, wkt_col, 0) == 1)
        dism = getattr(r, "dismissal_type", None)
        receipts.append(
            {
                "date": str(getattr(r, "match_date", ""))[:10],
                "comp": _short_comp_label(getattr(r, "comp_name", None), getattr(r, "season", None)),
                "stage": str(getattr(r, "match_stage", "") or ""),
                "opp": str(getattr(r, opp_col, "Opponent")),
                "other": str(getattr(r, other_col, "")),
                "inn": int(getattr(r, "innings", 1)),
                "ov": f"{int(getattr(r, 'overid', 0))}.{int(getattr(r, 'over_ball_num', 0))}",
                "phase": str(getattr(r, "phase", "")),
                "score": f"{int(getattr(r, 'score_before', 0))}/{int(getattr(r, 'wk_before', 0))}",
                "li": round(float(getattr(r, "LI", 0.0)), 2),
                "channel": channel,
                "style": str(getattr(r, "delivery_style", None) or "Standard"),
                "speed": round(float(spd), 1) if pd.notna(spd) and float(spd) > 0 else None,
                "stroke": str(getattr(r, "stroke", None) or "Unrecorded"),
                "runs": int(getattr(r, run_col, 0)),
                "out": is_out,
                "dism": str(dism) if is_out and pd.notna(dism) else None,
                "wpa": round(float(getattr(r, wpa_col, 0.0)) * 100.0, 2),
                "net": round(float(getattr(r, val_col, 0.0)) * 100.0, 1),
            }
        )
    return receipts


def build_bumrah_posture_benchmark(hp: pd.DataFrame) -> dict[str, Any]:
    """
    Forensic 506-ball HP defensive posture proof for Jasprit Bumrah vs elite bowling peers.
    Replaces any heuristic phrasing with exact b3.pkl stroke counts & posture value impacts.
    """
    peers = [
        ("Jasprit Bumrah", "Pace"),
        ("Sunil Narine", "Spin"),
        ("Jofra Archer", "Pace"),
        ("Sandeep Sharma", "Pace"),
        ("Rashid Khan", "Spin"),
        ("Mitchell Santner", "Spin"),
        ("Arshdeep Singh", "Pace"),
    ]
    rows: list[dict[str, Any]] = []
    for name, kind in peers:
        sub = hp[hp["bowler_name"] == name]
        n = int(len(sub))
        if n == 0:
            continue
        posture_counts = sub["stroke_posture"].value_counts().to_dict()
        def_n = int(posture_counts.get("Defensive", 0))
        att_n = int(posture_counts.get("Attacking", 0))
        rot_n = int(posture_counts.get("Rotation", 0))
        all_stat = summarize_group(sub, "bowl")
        def_stat = summarize_group(sub[sub["stroke_posture"] == "Defensive"], "bowl")
        att_stat = summarize_group(sub[sub["stroke_posture"] == "Attacking"], "bowl")
        rows.append(
            {
                "name": name,
                "type": kind,
                "n": n,
                "legal": all_stat["legal"],
                "wkts": all_stat["wkts"],
                "econ": all_stat["econ"],
                "dot_pct": all_stat["dot_pct"],
                "net_100": all_stat["net_100"],
                "std_err": all_stat["std_err"],
                "attack_pct": round(att_n / n * 100.0, 1),
                "rotation_pct": round(rot_n / n * 100.0, 1),
                "defensive_pct": round(def_n / n * 100.0, 1),
                "defensive_balls": def_n,
                "defensive_net_100": def_stat["net_100"],
                "attacking_net_100": att_stat["net_100"],
            }
        )

    bum_sub = hp[hp["bowler_name"] == "Jasprit Bumrah"]
    bum_strokes = [
        {
            "stroke": str(st),
            "balls": int(cnt),
            "posture": classify_stroke_posture(st),
            "net_100": summarize_group(bum_sub[bum_sub["stroke"] == st], "bowl")["net_100"],
            "wkts": int(bum_sub[bum_sub["stroke"] == st]["wkt_bowler"].sum()),
        }
        for st, cnt in bum_sub["stroke"].dropna().value_counts().head(10).items()
    ]
    return {
        "bumrah_total_hp_balls": int(len(bum_sub)),
        "peer_comparison": rows,
        "bumrah_top_strokes": bum_strokes,
    }


def extract_h2h_encounters(
    df: pd.DataFrame,
    cohort: list[dict[str, Any]],
    li_q75: float,
    min_balls: int = 6,
) -> list[dict[str, Any]]:
    """
    Mine real batter-vs-bowler historical H2H encounters across df between featured
    cohort players, applying Empirical Bayes shrinkage (k=12) toward prior net diff.
    """
    bat_map = {c["pid"]: c for c in cohort if c["role"] == "bat"}
    bowl_map = {c["pid"]: c for c in cohort if c["role"] == "bowl"}
    if not bat_map or not bowl_map:
        return []

    sub = df[
        df["striker_id"].isin(bat_map.keys())
        & df["bowler_id"].isin(bowl_map.keys())
        & (df["faced"] == 1)
    ].copy()

    encounters: list[dict[str, Any]] = []
    for (bid, wid), grp in sub.groupby(["striker_id", "bowler_id"], sort=False):
        n = int(len(grp))
        if n < min_balls:
            continue
        bat_meta = bat_map[int(bid)]
        bowl_meta = bowl_map[int(wid)]
        # Skip encounters unless at least one side is RR_2026 or Top-20 / IPL peer with >= 10 balls
        is_rr_involved = ("RR_2026" in bat_meta["tags"]) or ("RR_2026" in bowl_meta["tags"])
        if not is_rr_involved and n < 12:
            continue

        runs = int(grp["bat_runs"].sum())
        legal = int(grp["legal"].sum())
        outs = int(grp["out_striker"].sum())
        boundaries = int(((grp["is_four"] == 1) | (grp["is_six"] == 1)).sum())
        dots = int((grp["bat_runs"] == 0).sum())
        raw_net = float(grp["v_bat"].dropna().mean() * 100.0) if grp["v_bat"].notna().any() else 0.0
        hp_grp = grp[grp["LI"] >= li_q75]
        hp_n = int(len(hp_grp))
        hp_net = (
            round(float(hp_grp["v_bat"].dropna().mean() * 100.0), 1)
            if hp_n > 0 and hp_grp["v_bat"].notna().any()
            else None
        )

        # Empirical Bayes shrinkage (k=12 balls) toward prior (bat net_hp - bowl net_hp) * 0.5
        bat_prior = float(bat_meta.get("net_hp_adj") or 0.0)
        bowl_prior = float(bowl_meta.get("net_hp_adj") or 0.0)
        prior_net = (bat_prior - bowl_prior) * 0.45
        k = 12.0
        shrunk_net = round((n * raw_net + k * prior_net) / (n + k), 1)

        top_style = (
            str(grp["delivery_style"].dropna().mode().iloc[0])
            if grp["delivery_style"].dropna().shape[0] > 0
            else "Standard"
        )
        top_chan = (
            f"{grp['over_or_around'].dropna().mode().iloc[0]} · {grp['on_or_off'].dropna().mode().iloc[0]}"
            if grp["over_or_around"].dropna().shape[0] > 0
            and grp["on_or_off"].dropna().shape[0] > 0
            else "Recorded"
        )
        last_date = str(grp["match_date"].max())[:10]

        encounters.append(
            {
                "bat_id": int(bid),
                "bat_name": bat_meta["name"],
                "bat_team": TEAM_SHORT.get(bat_meta["ipl2026"], "POOL"),
                "bowl_id": int(wid),
                "bowl_name": bowl_meta["name"],
                "bowl_team": TEAM_SHORT.get(bowl_meta["ipl2026"], "POOL"),
                "n": n,
                "legal": legal,
                "runs": runs,
                "outs": outs,
                "sr": round(runs / max(n, 1) * 100.0, 1),
                "dot_pct": round(dots / max(n, 1) * 100.0, 1),
                "bnd_pct": round(boundaries / max(n, 1) * 100.0, 1),
                "raw_net": round(raw_net, 1),
                "shrunk_net": shrunk_net,
                "hp_n": hp_n,
                "hp_net": hp_net,
                "top_style": top_style,
                "top_channel": top_chan,
                "last_date": last_date,
                "low_sample": n < 12,
                "rr_tag": (
                    "RR_BAT"
                    if "RR_2026" in bat_meta["tags"]
                    else ("RR_BOWL" if "RR_2026" in bowl_meta["tags"] else "IPL")
                ),
            }
        )

    return sorted(encounters, key=lambda e: (-int(e["rr_tag"] != "IPL"), -e["n"]))


def build_rr_counter_plans(
    cohort: list[dict[str, Any]],
    profiles: dict[str, dict[str, Any]],
    h2h: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Build empirical match-day blueprints for RR vs all 9 IPL 2026 opponents
    combining real historical H2H receipts and channel/pace-spin vulnerability data.
    """
    rr_bats = [c for c in cohort if "RR_2026" in c["tags"] and c["role"] == "bat"]
    rr_bowls = [c for c in cohort if "RR_2026" in c["tags"] and c["role"] == "bowl"]

    h2h_by_pair = {(e["bat_id"], e["bowl_id"]): e for e in h2h}
    plans: dict[str, Any] = {}

    for team_full, code in TEAM_SHORT.items():
        if code == "RR":
            continue
        opp_bats = sorted(
            [c for c in cohort if c["ipl2026"] == team_full and c["role"] == "bat"],
            key=lambda x: x["adjusted_rank"] or 9999,
        )[:5]
        opp_bowls = sorted(
            [c for c in cohort if c["ipl2026"] == team_full and c["role"] == "bowl"],
            key=lambda x: x["adjusted_rank"] or 9999,
        )[:5]

        defensive_assignments: list[dict[str, Any]] = []
        for ob in opp_bats:
            prof = profiles.get(f"bat_{ob['pid']}", {})
            chans = prof.get("channels", {})
            weak_ch = chans.get("weak_channel") or "Over · Off-side"
            weak_net = chans.get("weak_net")
            styles = prof.get("styles", {}).get("delivery_styles", [])
            # Lowest batter net_100 style with >= 10 balls
            qual_styles = [s for s in styles if s.get("n", 0) >= 10 and s.get("net_100") is not None]
            best_trap_style = min(qual_styles, key=lambda s: s["net_100"])["style"] if qual_styles else "Hard Length"

            # Find best historical RR bowler vs this opponent batter (or best statistical match)
            candidates: list[tuple[float, dict[str, Any], dict[str, Any] | None]] = []
            for rb in rr_bats + rr_bowls:
                if rb["role"] != "bowl":
                    continue
                pair = h2h_by_pair.get((ob["pid"], rb["pid"]))
                score = (-pair["shrunk_net"] if pair else float(rb.get("net_hp_adj") or 0.0) * 0.6)
                if pair and pair["n"] >= 6:
                    score += min(pair["outs"] * 8.0, 24.0)
                candidates.append((score, rb, pair))
            candidates.sort(key=lambda t: t[0], reverse=True)
            chosen_rb, chosen_pair = (candidates[0][1], candidates[0][2]) if candidates else (rr_bowls[0], None)

            defensive_assignments.append(
                {
                    "opp_batter": ob["name"],
                    "opp_pid": ob["pid"],
                    "opp_rank": ob["adjusted_rank"],
                    "rr_bowler": chosen_rb["name"],
                    "rr_bowler_pid": chosen_rb["pid"],
                    "target_channel": weak_ch,
                    "target_net": weak_net,
                    "target_style": best_trap_style,
                    "h2h_balls": chosen_pair["n"] if chosen_pair else 0,
                    "h2h_runs": chosen_pair["runs"] if chosen_pair else 0,
                    "h2h_outs": chosen_pair["outs"] if chosen_pair else 0,
                    "h2h_sr": chosen_pair["sr"] if chosen_pair else None,
                    "evidence_mode": (
                        f"H2H Receipt ({chosen_pair['n']}b, {chosen_pair['outs']}w, SR {chosen_pair['sr']})"
                        if chosen_pair
                        else f"Channel Vulnerability (Net/100 {weak_net:+.1f})"
                        if weak_net is not None
                        else "Role Matchup"
                    ),
                }
            )

        batting_assignments: list[dict[str, Any]] = []
        for ow in opp_bowls:
            prof = profiles.get(f"bowl_{ow['pid']}", {})
            chans = prof.get("channels", {})
            # Weakest bowler channel (where bowler net_100 is lowest = batters score most)
            weak_ch = chans.get("weak_channel") or "Over · On-side"
            weak_net = chans.get("weak_net")

            candidates_b: list[tuple[float, dict[str, Any], dict[str, Any] | None]] = []
            for rbat in rr_bats:
                pair = h2h_by_pair.get((rbat["pid"], ow["pid"]))
                score = (pair["shrunk_net"] if pair else float(rbat.get("net_hp_adj") or 0.0) * 0.5)
                if pair and pair["outs"] == 0 and pair["n"] >= 8:
                    score += 12.0
                candidates_b.append((score, rbat, pair))
            candidates_b.sort(key=lambda t: t[0], reverse=True)
            chosen_bat, chosen_pair_b = (candidates_b[0][1], candidates_b[0][2]) if candidates_b else (rr_bats[0], None)

            batting_assignments.append(
                {
                    "opp_bowler": ow["name"],
                    "opp_pid": ow["pid"],
                    "opp_rank": ow["adjusted_rank"],
                    "rr_enforcer": chosen_bat["name"],
                    "rr_enforcer_pid": chosen_bat["pid"],
                    "attack_channel": weak_ch,
                    "bowler_weak_net": weak_net,
                    "h2h_balls": chosen_pair_b["n"] if chosen_pair_b else 0,
                    "h2h_runs": chosen_pair_b["runs"] if chosen_pair_b else 0,
                    "h2h_outs": chosen_pair_b["outs"] if chosen_pair_b else 0,
                    "h2h_sr": chosen_pair_b["sr"] if chosen_pair_b else None,
                    "evidence_mode": (
                        f"H2H Receipt ({chosen_pair_b['n']}b, SR {chosen_pair_b['sr']}, {chosen_pair_b['outs']}w)"
                        if chosen_pair_b
                        else f"Bowler Vulnerable Zone ({weak_ch})"
                    ),
                }
            )

        plans[code] = {
            "team_code": code,
            "team_name": team_full,
            "defensive_plan": defensive_assignments,
            "batting_plan": batting_assignments,
        }

    return plans


def build_full_payload(
    app_data: dict[str, Any],
    df: pd.DataFrame,
    hp: pd.DataFrame,
    li_q75: float,
) -> dict[str, Any]:
    """Assemble compact empirical Tactical Blueprint & Evidence Vault JSON payload."""
    cohort = build_featured_cohort(app_data)
    profiles: dict[str, dict[str, Any]] = {}

    for meta in cohort:
        pid = meta["pid"]
        role = meta["role"]
        key = f"{role}_{pid}"
        if role == "bat":
            sub = hp[(hp["striker_id"] == pid) & (hp["faced"] == 1)]
        else:
            sub = hp[hp["bowler_id"] == pid]

        channels = extract_channel_matrix(sub, role)
        styles = extract_delivery_and_stroke_profile(sub, role)
        receipts = extract_player_receipts(sub, role, limit=4)

        profiles[key] = {
            "key": key,
            "pid": pid,
            "name": meta["name"],
            "role": role,
            "ipl2026": meta["ipl2026"],
            "team_code": TEAM_SHORT.get(meta["ipl2026"], "POOL"),
            "nationality": meta["nationality"],
            "adjusted_rank": meta["adjusted_rank"],
            "adjusted_score": meta["adjusted_score"],
            "net_hp_adj": meta["net_hp_adj"],
            "tags": meta["tags"],
            "channels": channels,
            "styles": styles,
            "receipts": receipts,
        }

    h2h_all = extract_h2h_encounters(df, cohort, li_q75, min_balls=6)
    counter_plans = build_rr_counter_plans(cohort, profiles, h2h_all)
    bumrah_proof = build_bumrah_posture_benchmark(hp)

    # Keep all H2H pairs used in Counter-Plans + top RR/IPL encounters up to 350 rows
    plan_pairs: set[tuple[int, int]] = set()
    for pl in counter_plans.values():
        for d in pl["defensive_plan"]:
            plan_pairs.add((d["opp_pid"], d["rr_bowler_pid"]))
        for b in pl["batting_plan"]:
            plan_pairs.add((b["rr_enforcer_pid"], b["opp_pid"]))

    must_keep = [e for e in h2h_all if (e["bat_id"], e["bowl_id"]) in plan_pairs]
    seen_pairs = {(e["bat_id"], e["bowl_id"]) for e in must_keep}
    extras = [e for e in h2h_all if (e["bat_id"], e["bowl_id"]) not in seen_pairs]
    capped_h2h = must_keep + extras[: max(0, 350 - len(must_keep))]

    return {
        "meta": {
            "total_deliveries": int(len(df)),
            "hp_deliveries": int(len(hp)),
            "li_q75": round(li_q75, 4),
            "profile_count": len(profiles),
            "h2h_total_mined": len(h2h_all),
            "h2h_embedded": len(capped_h2h),
            "counter_plan_teams": len(counter_plans),
        },
        "profiles": profiles,
        "player_index": [
            {
                "key": k,
                "pid": v["pid"],
                "name": v["name"],
                "role": v["role"],
                "team_code": v["team_code"],
                "ipl2026": v["ipl2026"],
                "adjusted_rank": v["adjusted_rank"],
                "n_hp": v["channels"]["overall"]["n"],
                "tags": v["tags"],
            }
            for k, v in profiles.items()
        ],
        "bumrah_proof": bumrah_proof,
        "h2h_encounters": capped_h2h,
        "counter_plans": counter_plans,
    }


def inject_into_index_html(payload: dict[str, Any], html_path: Path = INDEX_HTML) -> int:
    """Safely update APP_DATA['tactical_blueprint'] in index.html using compact JSON."""
    html = html_path.read_text(encoding="utf-8")
    m = re.search(
        r"(const APP_DATA\s*=\s*)(\{.*?\})(;\s*(?:const|let|var|\n\s*//))",
        html,
        re.DOTALL,
    )
    if not m:
        raise ValueError(f"Could not locate const APP_DATA in {html_path}")
    app_data = json.loads(m.group(2))
    app_data["tactical_blueprint"] = payload
    compact = json.dumps(app_data, separators=(",", ":"))
    updated_html = html[: m.start(2)] + compact + html[m.end(2) :]
    html_path.write_text(updated_html, encoding="utf-8")
    return len(compact)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Tactical Blueprint Vault dataset.")
    parser.add_argument("--check-cohort", action="store_true", help="Print cohort stats only.")
    parser.add_argument("--check-channels", action="store_true", help="Print sample channel matrices.")
    parser.add_argument("--check-styles", action="store_true", help="Print sample style & stroke traps.")
    parser.add_argument("--check-receipts", action="store_true", help="Print receipts & Bumrah 506 proof.")
    parser.add_argument("--check-h2h", action="store_true", help="Print H2H count & MI counter-plan sample.")
    parser.add_argument("--inject", action="store_true", help="Export JSON and inject into index.html.")
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
    if args.check_h2h:
        h2h = extract_h2h_encounters(df, cohort, li_q75)
        print("H2H encounters extracted:", len(h2h))
        print("Sample RR H2H:", json.dumps([e for e in h2h if e["rr_tag"] != "IPL"][:4], indent=2))
        return
    if args.check_channels or args.check_styles or args.check_receipts:
        if args.check_receipts:
            print("=== BUMRAH 506 POSTURE PROOF ===")
            print(json.dumps(build_bumrah_posture_benchmark(hp), indent=2))
        for name, pid, role in [
            ("Yashasvi Jaiswal", 6819, "bat"),
            ("Jasprit Bumrah", 652, "bowl"),
        ]:
            sub = hp[(hp["striker_id"] == pid) & (hp["faced"] == 1)] if role == "bat" else hp[hp["bowler_id"] == pid]
            if len(sub) == 0:
                sub = hp[(hp["striker_name"] == name) & (hp["faced"] == 1)] if role == "bat" else hp[hp["bowler_name"] == name]
            print(f"=== {name} ({role}) ===")
            if args.check_channels:
                print(json.dumps(extract_channel_matrix(sub, role), indent=2))
            if args.check_styles:
                print(json.dumps(extract_delivery_and_stroke_profile(sub, role), indent=2))
            if args.check_receipts:
                print(json.dumps(extract_player_receipts(sub, role, limit=3), indent=2))
        return

    payload = build_full_payload(app_data, df, hp, li_q75)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, separators=(",", ":"), allow_nan=False), encoding="utf-8")
    out_kb = OUT_JSON.stat().st_size / 1024.0
    print(f"Exported {OUT_JSON} ({out_kb:.1f} KB) - meta: {payload['meta']}")
    if args.inject:
        app_len = inject_into_index_html(payload)
        print(f"Injected tactical_blueprint into index.html (APP_DATA = {app_len / 1024.0:.1f} KB)")


if __name__ == "__main__":
    main()
