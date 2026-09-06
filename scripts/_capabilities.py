"""Shared deterministic enrichment for non-decision capability facts."""

from __future__ import annotations


PRIMITIVE_CAPABILITIES = {
    "document": ["carry", "fold", "select", "split"],
    "dotted-route": ["carry", "connect", "trace"],
    "envelope": ["carry", "reveal", "send"],
    "gauge": ["compare", "measure", "reveal"],
    "key": ["select", "unlock"],
    "pulse-wave": ["connect", "pulse", "signal", "trace"],
}


def enrich(entry: dict) -> None:
    """Add only objective capability facts; routing remains the sole decision authority."""
    if entry.get("kind") != "svg" or not str(entry.get("id", "")).startswith("svg:primitive:"):
        return
    slug = str(entry["id"]).split(":")[-1]
    additions = PRIMITIVE_CAPABILITIES.get(slug, [])
    entry["capabilities"] = sorted({
        str(value) for value in [*(entry.get("capabilities") or []), *additions]
        if isinstance(value, str) and value
    })
