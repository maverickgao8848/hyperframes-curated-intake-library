from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/hyperframes-curated-intake/scripts/inventory-library.py"


class InventoryLibraryTests(unittest.TestCase):
    def test_reports_schema_hash_preview_status_mapping_and_frames_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            library = Path(temp) / "library"
            (library / "source").mkdir(parents=True)
            (library / "previews").mkdir()
            (library / "frames/cobalt-grid").mkdir(parents=True)
            source = library / "source/item.html"
            source.write_text('<div data-width="1" data-height="1" data-duration="1"></div>', encoding="utf-8")
            (library / "previews/item.svg").write_text("<svg/>", encoding="utf-8")
            (library / "frames/cobalt-grid/FRAME.md").write_text("# Frame\n", encoding="utf-8")
            source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            catalog = {
                "schemaVersion": "hyperframes-directed-video-library/v1", "revision": 7,
                "entries": [{
                    "id": "registry-block:item", "kind": "registry-block", "title": "Item", "description": "Item.",
                    "tags": [], "status": "ready", "preview": "previews/item.svg",
                    "source": {"type": "bundle", "name": "item", "entry": "source/item.html", "files": [
                        {"path": "source/item.html", "target": "item.html", "sha256": source_hash}]},
                }, {"id": "registry-component:off", "kind": "registry-component", "status": "disabled"}],
            }
            (library / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
            before = sorted(path.relative_to(library) for path in library.rglob("*"))
            output = Path(temp) / "report.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--library", str(library), "--output", str(output)],
                check=True, capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(result.stdout, "")
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(report["catalog"]["schemaValid"])
            self.assertEqual(report["catalog"]["revision"], 7)
            self.assertEqual(report["summary"]["statuses"], {"disabled": 1, "ready": 1})
            self.assertEqual(report["summary"]["frames"], 1)
            self.assertTrue(report["entries"][0]["sourceFiles"][0]["hashMatches"])
            self.assertTrue(report["entries"][0]["preview"]["exists"])
            self.assertEqual(report["entries"][0]["registry"]["itemPath"], "blocks/item/registry-item.json")
            after = sorted(path.relative_to(library) for path in library.rglob("*"))
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
