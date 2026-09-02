#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _curation import frame_rule_ids, load_storyboard_spec, validate_beat_contract, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify beat windows and HyperFrames animation references.")
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--animation-skill", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def verify(spec: dict, animation_skill: Path) -> dict:
    validate_beat_contract(spec, require_windows=True)
    findings: list[dict] = []
    blueprints = animation_skill / "blueprints"
    rules = animation_skill / "rules"
    for frame in spec["frames"]:
        blueprint = str(frame["blueprint"])
        if blueprint != "compose" and not (blueprints / f"{blueprint}.md").is_file():
            findings.append({"level": "error", "code": "blueprint-missing", "frame": frame["id"], "id": blueprint})
        for rule_id in frame_rule_ids(frame):
            if not (rules / f"{rule_id}.md").is_file():
                findings.append({"level": "error", "code": "rule-missing", "frame": frame["id"], "id": rule_id})
    return {
        "schemaVersion": "hyperframes-curated-beat-verification/v1",
        "ok": not any(item["level"] == "error" for item in findings),
        "frames": len(spec["frames"]),
        "findings": findings,
    }


def main() -> int:
    args = parse_args()
    spec = load_storyboard_spec(args.spec.resolve())
    report = verify(spec, args.animation_skill.resolve())
    if args.report:
        write_json(args.report.resolve(), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
