"""Shared, dependency-free helpers for the curated Registry scripts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


CATALOG_SCHEMA = "hyperframes-directed-video-library/v1"
REGISTRY_SCHEMA = "https://hyperframes.heygen.com/schema/registry.json"
REGISTRY_ITEM_SCHEMA = "https://hyperframes.heygen.com/schema/registry-item.json"
REGISTRY_KINDS = {
    "registry-block": ("blocks", "hyperframes:block"),
    "registry-component": ("components", "hyperframes:component"),
}


def default_library() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "library"


def load_catalog(library: Path) -> tuple[Path, dict[str, Any]]:
    path = library.resolve() / "catalog.json"
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("catalog.json must contain a JSON object")
    return path, value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative(value: str, label: str) -> PurePosixPath:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if not normalized or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label} must be a safe relative path: {value!r}")
    return path


def source_files(entry: dict[str, Any]) -> list[dict[str, Any]]:
    source = entry.get("source")
    if not isinstance(source, dict):
        return []
    if source.get("type") == "bundle":
        files = source.get("files")
        return files if isinstance(files, list) else []
    if source.get("type") == "file" and isinstance(source.get("path"), str):
        return [{"path": source["path"], "target": source["path"], "sha256": entry.get("sha256")}]
    return []


def entry_name(entry: dict[str, Any]) -> str | None:
    source = entry.get("source")
    name = source.get("name") if isinstance(source, dict) else None
    if not name and isinstance(entry.get("id"), str) and ":" in entry["id"]:
        name = entry["id"].split(":", 1)[1]
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        return None
    return name


_ATTR = r"{name}\s*=\s*['\"](?P<value>\d+(?:\.\d+)?)['\"]"


def block_geometry(
    html: str,
    *,
    aspect_fit: list[str] | None = None,
    duration_hint: float | int | None = None,
) -> tuple[dict[str, int] | None, float | int | None, list[str]]:
    reasons: list[str] = []

    def attr(name: str) -> float | None:
        match = re.search(_ATTR.format(name=re.escape(name)), html, flags=re.IGNORECASE)
        return float(match.group("value")) if match else None

    width, height, duration = attr("data-width"), attr("data-height"), attr("data-duration")
    duration = duration or attr("data-composition-duration")
    if width is None or height is None:
        viewport = re.search(
            r"<meta[^>]+name\s*=\s*['\"]viewport['\"][^>]+content\s*=\s*['\"][^'\"]*"
            r"width\s*=\s*(\d+)[^'\"]*height\s*=\s*(\d+)",
            html,
            flags=re.IGNORECASE,
        )
        if viewport:
            width = width or float(viewport.group(1))
            height = height or float(viewport.group(2))
    dimensions = None
    if width is None or height is None:
        aspect_defaults = {
            "16:9": (1920.0, 1080.0),
            "9:16": (1080.0, 1920.0),
            "1:1": (1080.0, 1080.0),
        }
        for aspect in aspect_fit or []:
            if aspect in aspect_defaults:
                width, height = aspect_defaults[aspect]
                break
    if width is None or height is None:
        reasons.append("block dimensions are not declared in data-width/data-height or viewport metadata")
    elif not width.is_integer() or not height.is_integer() or width <= 0 or height <= 0:
        reasons.append("block dimensions must be positive integers")
    else:
        dimensions = {"width": int(width), "height": int(height)}
    if duration is None and isinstance(duration_hint, (int, float)):
        duration = float(duration_hint)
    if duration is None:
        reasons.append("block duration is not declared in data-duration")
        normalized_duration = None
    elif duration <= 0:
        reasons.append("block duration must be positive")
        normalized_duration = None
    else:
        normalized_duration = int(duration) if duration.is_integer() else duration
    return dimensions, normalized_duration, reasons


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json_bytes(value)
    if path.exists() and path.read_bytes() == data:
        return
    path.write_bytes(data)
