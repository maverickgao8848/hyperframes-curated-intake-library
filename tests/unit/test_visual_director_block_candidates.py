from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / ".agents/skills/hyperframes-curated-intake/assets/library"
BLOCKS = LIBRARY / "candidates" / "visual-director" / "blocks"
PROVENANCE = ROOT / "docs/library-provenance/source-provenance.json"


class VisualDirectorBlockCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((LIBRARY / "visual-director-block-candidates.json").read_text(encoding="utf-8"))
        cls.by_id = {entry["id"]: entry for entry in cls.catalog["entries"]}

    def test_three_candidates_are_landscape_seek_safe_and_offline(self):
        expected = {
            "wechat-desktop-exchange.html": ("wechat-desktop-exchange", "5.6"),
            "chatgpt-desktop-exchange.html": ("chatgpt-desktop-exchange", "14.9"),
            "film-credits-stagger.html": ("film-credits-stagger", "4.8"),
        }
        for filename, (composition_id, duration) in expected.items():
            text = (BLOCKS / filename).read_text(encoding="utf-8")
            self.assertIn('data-width="1920"', text)
            self.assertIn('data-height="1080"', text)
            self.assertIn('data-fps="60"', text)
            self.assertIn(f'data-duration="{duration}"', text)
            self.assertIn("gsap.timeline({ paused: true })", text)
            self.assertIn(f'window.__timelines["{composition_id}"]', text)
            self.assertNotRegex(text, r"https?://")
            self.assertNotIn("Math.random", text)
            self.assertNotIn("fetch(", text)

    def test_native_evidence_and_frame_token_rules(self):
        self.assertEqual("native-evidence", self.by_id["registry-block:wechat-desktop-exchange"]["framePolicy"])
        self.assertEqual("native-evidence", self.by_id["registry-block:chatgpt-desktop-exchange"]["framePolicy"])
        self.assertEqual("frame-governed", self.by_id["registry-block:film-credits-stagger"]["framePolicy"])
        film = (BLOCKS / "film-credits-stagger.html").read_text(encoding="utf-8")
        for variable in ("foreground", "accent", "background"):
            self.assertIn(f'&quot;id&quot;:&quot;{variable}&quot;', film)

    def test_props_cover_long_text_assets_and_compact_mode(self):
        wechat = (BLOCKS / "wechat-desktop-exchange.html").read_text(encoding="utf-8")
        chatgpt = (BLOCKS / "chatgpt-desktop-exchange.html").read_text(encoding="utf-8")
        film = (BLOCKS / "film-credits-stagger.html").read_text(encoding="utf-8")
        self.assertIn("clientAvatar", wechat)
        self.assertIn("word-break: break-word", wechat)
        self.assertIn("compactMode", chatgpt)
        self.assertIn("overflow-wrap: anywhere", chatgpt)
        self.assertIn("overflow-wrap: anywhere", film)

    def test_canonical_sources_are_promoted_evidence_not_second_ready_catalog(self):
        canonical = json.loads((LIBRARY / "catalog.json").read_text(encoding="utf-8"))
        canonical_ids = {entry["id"] for entry in canonical["entries"] if entry.get("status") == "ready"}
        for entry in self.catalog["entries"]:
            self.assertEqual("verified", entry["sourceStatus"])
            self.assertEqual("promoted", entry["status"])
            self.assertIn(entry["id"], canonical_ids)
            self.assertEqual("verified", entry["portStatus"])
            self.assertTrue(entry["canonicalSource"]["sha256"].startswith("sha256:"))
            self.assertTrue(entry["derivedSha256"].startswith("sha256:"))
            self.assertEqual("passed", entry["verification"]["libraryContractTest"])
            self.assertEqual("passed", entry["verification"]["hyperframesCheck"])
            self.assertTrue(entry["verification"]["snapshotsReviewed"])

    def test_canonical_source_paths_are_portable_and_match_external_reference(self):
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        reference_root = Path(provenance["hyperframesReferenceRepository"]["path"])
        self.assertTrue(reference_root.is_dir())
        for entry in self.catalog["entries"]:
            relative = Path(entry["canonicalSource"]["path"])
            self.assertFalse(relative.is_absolute())
            self.assertNotIn("C:/Users/", entry["canonicalSource"]["path"])
            source = reference_root / relative
            self.assertTrue(source.is_file(), source)
            expected = entry["canonicalSource"]["sha256"].removeprefix("sha256:")
            self.assertEqual(expected, hashlib.sha256(source.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
