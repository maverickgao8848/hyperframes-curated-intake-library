#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

from _capabilities import enrich


DIRECTING_FIELDS = ("family", "purpose", "useWhen", "avoidWhen", "expects", "motion")


def main() -> int:
    parser = argparse.ArgumentParser(description="Add objective capability facts without changing routing or catalog kinds.")
    parser.add_argument("catalog", type=Path, nargs="+")
    args = parser.parse_args()
    for path in args.catalog:
        value = json.loads(path.read_text(encoding="utf-8"))
        for entry in value.get("entries", []):
            if isinstance(entry, dict):
                routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else {}
                directing_before = {field: deepcopy(routing[field]) for field in DIRECTING_FIELDS if field in routing}
                enrich(entry)
                routing_after = entry.get("routing") if isinstance(entry.get("routing"), dict) else {}
                directing_after = {field: routing_after[field] for field in DIRECTING_FIELDS if field in routing_after}
                if directing_after != directing_before:
                    raise RuntimeError(f"capability enrichment changed directing metadata: {entry.get('id')}")
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Enriched {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
