#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from director_plan import load_json, plan_metrics, validate_plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Visual Director machine authority.")
    parser.add_argument("plan", type=Path)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    plan = load_json(args.plan)
    catalog = load_json(args.catalog) if args.catalog else None
    errors = validate_plan(plan, catalog)
    report = {"valid": not errors, "errors": errors, "metrics": plan_metrics(plan)}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif errors:
        print("Director plan is invalid:")
        for error in errors:
            print(f"- {error}")
    else:
        print("Director plan is valid.")
        print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
