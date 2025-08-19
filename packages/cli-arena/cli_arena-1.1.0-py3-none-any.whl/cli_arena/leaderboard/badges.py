from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

from .leaderboard import Leaderboard


def _color_for_rate(rate: float) -> str:
    if rate >= 90:
        return "brightgreen"
    if rate >= 75:
        return "green"
    if rate >= 60:
        return "yellowgreen"
    if rate >= 40:
        return "yellow"
    if rate >= 20:
        return "orange"
    return "red"


def generate_badges(db_path: Path, out_dir: Path) -> Dict[str, Path]:
    """Generate shields.io JSON badges for overall standings and per-agent verify rate.

    Returns a mapping of badge name to path.
    """
    lb = Leaderboard(db_path)
    rows = lb.standings()
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs: Dict[str, Path] = {}

    # Overall top agent badge
    if rows:
        top = rows[0]
        badge = {
            "schemaVersion": 1,
            "label": "Top Agent",
            "message": f"{top['agent']} {top['verify_rate']:.1f}%",
            "color": _color_for_rate(float(top["verify_rate"]))
        }
        p = out_dir / "overall-top-agent.json"
        p.write_text(json.dumps(badge))
        outputs["overall-top-agent"] = p

    # Per-agent verify rate badges
    for r in rows:
        name = r["agent"].replace("/", "-")
        badge = {
            "schemaVersion": 1,
            "label": f"{name} verify",
            "message": f"{r['verify_rate']:.1f}%",
            "color": _color_for_rate(float(r["verify_rate"]))
        }
        p = out_dir / f"agent-{name}-verify.json"
        p.write_text(json.dumps(badge))
        outputs[f"agent-{name}-verify"] = p

        # Flakiness badge (true flake rate)
        fr = float(r.get("flaky_true_rate", 0.0))
        badge2 = {
            "schemaVersion": 1,
            "label": f"{name} flakiness",
            "message": f"{fr:.1f}%",
            "color": _color_for_rate(100 - fr)  # greener when lower flake
        }
        p2 = out_dir / f"agent-{name}-flake.json"
        p2.write_text(json.dumps(badge2))
        outputs[f"agent-{name}-flake"] = p2

    return outputs


