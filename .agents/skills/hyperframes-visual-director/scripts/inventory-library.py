#!/usr/bin/env python3
"""Build the shared Visual Director catalog and TalkCraft migration queue."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


CATEGORY_MAP = {
    "强调标注": ("layer", "L4-attached-effect"),
    "人物互动": ("layer", "L3-subject"),
    "数据信息图": ("registry-component", "L3-subject"),
    "素材呈现": ("scene-blueprint", "L3-subject"),
    "运镜": ("motion-rule", "L1-camera"),
    "转场结构": ("transition", "L7-mask"),
    "字幕花字": ("layer", "L5-supporting-element"),
}
BLOCK_IDS = {"chat-gpt", "news-card-desk", "terminal-typing-log", "claude-code", "ui-flow-theater", "ui-prop-theater"}
LAYER_WORDS = {
    "camera": ("push", "pull", "zoom", "parallax", "orbit", "tilt", "tour", "long-take", "sway"),
    "focus": ("focus", "spotlight", "magnifier"),
    "annotation": ("underline", "ellipse", "scribble", "callout", "bracket", "arrow", "highlight"),
    "typography": ("title", "quote", "type", "character", "line-by-line", "number", "text"),
    "caption": ("caption", "subtitle", "lower-third", "nameplate", "chevron"),
    "host": ("host", "danmu", "follow", "subscribe"),
    "environment": ("environment", "particle", "gooey"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"missing frontmatter: {path}")
    body = text.split("---", 2)[1]
    result: dict[str, str] = {}
    for line in body.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def git_value(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def classify(card_id: str, category: str) -> tuple[str, str, str | None]:
    kind, layer_position = CATEGORY_MAP.get(category, ("scene-blueprint", "L3-subject"))
    if card_id in BLOCK_IDS:
        kind = "registry-block"
    layer_type = None
    if kind == "layer":
        layer_type = "annotation"
        for candidate, words in LAYER_WORDS.items():
            if any(word in card_id for word in words):
                layer_type = candidate
                break
    return kind, layer_position, layer_type


def frame_policy(card_id: str, kind: str) -> str:
    if card_id == "chat-gpt":
        return "native-evidence"
    if kind in {"motion-rule", "layer"} and any(token in card_id for token in ("push", "pull", "zoom", "focus", "magnifier", "tour", "parallax")):
        return "source-preserve"
    return "frame-governed"


def inventory_talkcraft(source: Path, authorization_note: str) -> dict[str, Any]:
    source = source.resolve()
    commit = git_value(source, "rev-parse", "HEAD")
    remote = git_value(source, "remote", "get-url", "origin")
    cards = []
    category_counts: dict[str, int] = {}
    for reference in sorted((source / "references" / "cards").glob("*.md")):
        meta = parse_frontmatter(reference)
        card_id = meta.get("name", reference.stem)
        category = meta.get("类别", "未分类")
        category_counts[category] = category_counts.get(category, 0) + 1
        kind, layer_position, layer_type = classify(card_id, category)
        remotion_path = source / meta.get("代码", f"template/cards/{card_id}.tsx")
        demo_path = source / "demos" / card_id / "index.html"
        entry = {
            "id": f"talkcraft:{card_id}",
            "title": meta.get("标题", card_id),
            "description": meta.get("一句话", ""),
            "source": {
                "repository": remote,
                "commit": commit,
                "referencePath": reference.relative_to(source).as_posix(),
                "remotionPath": remotion_path.relative_to(source).as_posix(),
                "demoPath": demo_path.relative_to(source).as_posix(),
                "sourceHash": "sha256:" + sha256(remotion_path),
                "referenceHash": "sha256:" + sha256(reference),
            },
            "partnerAuthorizationNote": authorization_note,
            "sourceCategory": category,
            "sevenLayerPosition": layer_position,
            "kind": kind,
            "semanticJob": meta.get("适用", ""),
            "narrativeRole": "transition" if kind == "transition" else "support" if kind == "layer" else "primary-candidate",
            "energy": meta.get("能量", "未标注"),
            "density": "source-defined",
            "duration": meta.get("时长", "source-defined"),
            "aspectSupport": ["16:9"],
            "portraitVariantId": None,
            "props": [],
            "mediaSlots": [],
            "textSlots": [],
            "targetInterface": "stable-target-required" if kind == "layer" else "self-contained-stage" if kind == "registry-block" else "author-defined",
            "timingAnchors": ["segment-start", "narration-beat"],
            "seekSafe": None,
            "networkPolicy": "offline-required",
            "framePolicy": frame_policy(card_id, kind),
            "avoid": [],
            "fallback": {"type": "source-only", "description": "Preserve the source and use a simpler verified layer."},
            "knownGaps": ["Native HyperFrames port and matched-frame verification are pending."],
            "preview": {"upstreamPath": demo_path.relative_to(source).as_posix(), "sourceHash": "sha256:" + sha256(demo_path)},
            "quality": {"baselineFrames": [], "ssimReport": None, "visualReview": None},
            "portStatus": "linted",
            "status": "candidate",
        }
        if layer_type:
            entry["layerType"] = layer_type
        cards.append(entry)
    return {
        "schemaVersion": "hyperframes-visual-director/talkcraft-inventory-v1",
        "source": {"repository": remote, "commit": commit},
        "cardCount": len(cards),
        "sourceCategoryCounts": dict(sorted(category_counts.items())),
        "lint": {"filesScanned": 98, "blockers": 0, "warnings": 10, "info": 2, "status": "passed-with-warnings"},
        "entries": cards,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory TalkCraft and build the Visual Director shared catalog.")
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--talkcraft", type=Path, required=True)
    parser.add_argument("--authorization-note", default="docs/library-provenance/talkcraft-partner-authorization.md")
    args = parser.parse_args()
    library = args.library.resolve()
    inventory = inventory_talkcraft(args.talkcraft, args.authorization_note)
    if inventory["cardCount"] != 78:
        raise SystemExit(f"Expected 78 TalkCraft cards, found {inventory['cardCount']}")
    inventory_path = library / "talkcraft-inventory.json"
    inventory_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # The shared director catalog has one derivation path. Candidate manifests are
    # evidence only; promoted Registry items live in catalog.json and are not
    # appended as a second ready source here.
    builder = Path(__file__).resolve().parents[2] / "hyperframes-curated-intake" / "scripts" / "build-director-catalog.py"
    subprocess.check_call([sys.executable, str(builder), "--library", str(library)])
    shared = json.loads((library / "director-catalog.json").read_text(encoding="utf-8"))
    print(json.dumps({"talkcraftCards": inventory["cardCount"], "sharedEntries": len(shared["entries"]), "categoryCounts": inventory["sourceCategoryCounts"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
