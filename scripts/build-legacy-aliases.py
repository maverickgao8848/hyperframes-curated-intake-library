#!/usr/bin/env python3
"""Generate the checked-in legacy Video Spec Builder alias table."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from _registry import default_library


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=default_library(), help="Library containing catalog.json (default: skill assets/library)")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    library = args.library.resolve()
    catalog = json.loads((library / "catalog.json").read_text(encoding="utf-8"))
    aliases: dict[str, dict[str, str | None]] = {}
    for entry in catalog.get("entries", []):
        if entry.get("kind") != "registry-component" or entry.get("status") != "ready":
            continue
        source = entry.get("source") if isinstance(entry.get("source"), dict) else {}
        for record in source.get("files", []):
            path = library / record.get("path", "")
            if not path.is_file() or path.suffix != ".js":
                continue
            match = re.search(r"legacyAliases\s*:\s*\[(.*?)\]", path.read_text(encoding="utf-8"), re.DOTALL)
            if not match:
                continue
            for alias in re.findall(r"['\"]([^'\"]+)['\"]", match.group(1)):
                if alias in aliases and aliases[alias]["registry_id"] != entry["id"]:
                    raise SystemExit(f"Duplicate legacy alias: {alias}")
                aliases[alias] = {"registry_id": entry["id"], "result": "ready"}
    aliases["broll-abstract.placeholder"] = {"registry_id": None, "result": "no_recommendation"}
    output = {
        "schemaVersion": "video-spec-builder-legacy-aliases/v1",
        "source": "catalog.json",
        "aliases": dict(sorted(aliases.items())),
    }
    target = (args.output or (library / "legacy-component-aliases.json")).resolve()
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {target} with {len(aliases)} aliases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
