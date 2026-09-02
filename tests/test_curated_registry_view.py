from __future__ import annotations

import hashlib
import http.server
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/hyperframes-curated-intake/scripts/build-registry-view.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RegistryViewTests(unittest.TestCase):
    def fixture(self, root: Path) -> Path:
        library = root / "library"
        (library / "source").mkdir(parents=True)
        block = library / "source/block.html"
        component = library / "source/component.js"
        block.write_text('<div data-width="1920" data-height="1080" data-duration="6"></div>', encoding="utf-8")
        component.write_text("export function mount() {}\n", encoding="utf-8")
        entries = [
            {
                "id": "registry-block:good-block", "kind": "registry-block", "title": "Good Block",
                "description": "Shows a deterministic relationship.", "tags": ["flow", "flow"], "status": "ready",
                "source": {"type": "bundle", "name": "good-block", "entry": "source/block.html", "files": [
                    {"path": "source/block.html", "target": "good-block.html", "sha256": digest(block)}]},
            },
            {
                "id": "registry-component:good-component", "kind": "registry-component", "title": "Good Component",
                "description": "Adds a reusable deterministic component.", "tags": ["support"], "status": "ready",
                "source": {"type": "bundle", "name": "good-component", "entry": "source/component.js", "files": [
                    {"path": "source/component.js", "target": "components/good-component/component.js", "sha256": digest(component)}]},
            },
            {
                "id": "logo:not-registry", "kind": "logo", "title": "Logo", "status": "ready",
                "source": {"type": "file", "path": "source/component.js"},
            },
            {
                "id": "registry-block:disabled", "kind": "registry-block", "title": "Disabled",
                "description": "Must not be registered.", "tags": [], "status": "disabled",
                "source": {"type": "bundle", "name": "disabled", "entry": "source/block.html", "files": [
                    {"path": "source/block.html", "target": "disabled.html", "sha256": digest(block)}]},
            },
        ]
        (library / "catalog.json").write_text(json.dumps({"schemaVersion": "hyperframes-directed-video-library/v1", "revision": 1, "entries": entries}), encoding="utf-8")
        return library

    def run_build(self, library: Path, output: Path) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--library", str(library), "--output", str(output)],
            check=True, capture_output=True, text=True, encoding="utf-8",
        )
        return json.loads(result.stdout)

    def test_builds_official_layout_and_cli_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library = self.fixture(root)
            output = root / "view"
            report = self.run_build(library, output)
            manifest = json.loads((output / "registry.json").read_text(encoding="utf-8"))
            self.assertEqual(list(manifest), ["$schema", "name", "homepage", "items"])
            self.assertEqual(
                manifest["items"],
                [{"name": "good-block", "type": "hyperframes:block"}, {"name": "good-component", "type": "hyperframes:component"}],
            )
            block_item = json.loads((output / "blocks/good-block/registry-item.json").read_text(encoding="utf-8"))
            self.assertEqual(block_item["dimensions"], {"width": 1920, "height": 1080})
            self.assertEqual(block_item["duration"], 6)
            self.assertEqual(block_item["tags"], ["flow"])
            self.assertTrue((output / "blocks/good-block/good-block.html").is_file())
            component_item = json.loads((output / "components/good-component/registry-item.json").read_text(encoding="utf-8"))
            self.assertNotIn("dimensions", component_item)
            self.assertTrue((output / "components/good-component/good-component/component.js").is_file())
            self.assertEqual(report["summary"], {"mapped": 2, "unmapped": 1, "ignored": 1})

    def test_repeat_is_byte_deterministic_and_source_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library = self.fixture(root)
            output = root / "view"
            before = {path.relative_to(library): path.read_bytes() for path in library.rglob("*") if path.is_file()}
            self.run_build(library, output)
            first = {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
            self.run_build(library, output)
            second = {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
            after = {path.relative_to(library): path.read_bytes() for path in library.rglob("*") if path.is_file()}
            self.assertEqual(first, second)
            self.assertEqual(before, after)

    def test_hyperframes_cli_catalogs_and_installs_block_and_component(self) -> None:
        npx = shutil.which("npx.cmd") or shutil.which("npx")
        if npx is None:
            self.skipTest("npx is unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library = self.fixture(root)
            registry = root / "registry"
            project = root / "project"
            project.mkdir()
            self.run_build(library, registry)

            handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(  # noqa: E731
                *args, directory=str(registry), **kwargs
            )
            server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base_url = f"http://127.0.0.1:{server.server_port}"
                (project / "hyperframes.json").write_text(
                    json.dumps({
                        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                        "registry": base_url,
                        "paths": {
                            "blocks": "compositions/library",
                            "components": "compositions/components/library",
                            "assets": "assets/library",
                        },
                    }),
                    encoding="utf-8",
                )
                catalog = subprocess.run(
                    [npx, "hyperframes", "catalog", "--json"], cwd=project,
                    check=True, capture_output=True, text=True, encoding="utf-8",
                )
                catalog_data = json.loads(catalog.stdout)
                items = catalog_data if isinstance(catalog_data, list) else catalog_data["items"]
                names = {item["name"] for item in items}
                self.assertEqual(names, {"good-block", "good-component"})
                subprocess.run(
                    [npx, "hyperframes", "add", "good-block", "--no-clipboard", "--json"], cwd=project,
                    check=True, capture_output=True, text=True, encoding="utf-8",
                )
                subprocess.run(
                    [npx, "hyperframes", "add", "good-component", "--no-clipboard", "--json"], cwd=project,
                    check=True, capture_output=True, text=True, encoding="utf-8",
                )
                self.assertTrue((project / "compositions/library/good-block.html").is_file())
                self.assertTrue((project / "compositions/components/library/good-component/component.js").is_file())
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
