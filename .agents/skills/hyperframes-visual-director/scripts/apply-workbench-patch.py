#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from director_plan import LockConflict, PatchError, RevisionConflict, apply_patch, atomic_write_json, load_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply one bounded revision-safe workbench patch.")
    parser.add_argument("project", type=Path)
    parser.add_argument("patch", type=Path)
    parser.add_argument("--actor", default="human")
    parser.add_argument("--catalog", type=Path)
    args = parser.parse_args()
    plan_path = args.project.resolve() / "director-plan.json"
    plan = load_json(plan_path)
    patch = load_json(args.patch)
    catalog = load_json(args.catalog) if args.catalog else None
    try:
        updated = apply_patch(plan, patch, args.actor, catalog)
    except (RevisionConflict, LockConflict, PatchError) as error:
        print(json.dumps({"ok": False, "error": type(error).__name__, "message": str(error)}, ensure_ascii=False))
        return 1
    atomic_write_json(plan_path, updated)
    try:
        args.patch.resolve().unlink()
    except OSError:
        pass
    print(json.dumps({"ok": True, "revision": updated["revision"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
