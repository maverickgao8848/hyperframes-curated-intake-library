# Verification

## Intake preflight

`scripts/verify-handoff.py` establishes that the packet is ready for HyperFrames:

- every canonical artifact exists and matches its manifest hash;
- every Storyboard scene appears in the handoff manifest, scene-contract directory, and Build Plan;
- scene identity and paths match across all intake artifacts;
- Frame provenance is current;
- required media exists inside the project and matches its hash;
- directed integrations resolve to the palette and Build Plan;
- every scene contract preserves the approved teaching classification and narrative scale;
- every required integration is represented as a scene gate;
- an `N`-scene packet contains exactly `N−1` adjacent-boundary transition contracts;
- every transition connects the correct neighboring scene IDs, resolves to the palette, appears in the Build Plan, and carries a required integration gate;
- same-background transitions are color-independent and declare a perceptual anchor that remains visible without palette contrast;
- the project contains no authored composition HTML;
- `HANDOFF.md` contains the complete copy-ready protocol.

## Later Build verification

Run `npx hyperframes check`, then `scripts/verify-curation.py --project <project>`.

The build verifier uses the manifest scene list as the expected set and confirms:

- every declared composition exists at its canonical path;
- every composition ID, sidecar stem, Build Plan scene ID, and usage scene ID matches;
- every selected item has a valid staging receipt;
- every Block has a real staged `data-composition-src` host in its declared scene;
- every Component contributes staged structural and runtime signatures to its declared scene;
- every required asset appears in the intended scene;
- every beat, text cue, and active ambient plan binds to a visible production selector;
- every required integration reaches integrated evidence;
- every planned transition reaches staged and integrated evidence with matching boundary ID, catalog ID, from/to scene IDs, implementation mode, and production controller;
- every transition controller exposes the declared boundary markers and executable shader/runtime or CSS/GSAP wiring;
- boundary snapshots cover the outgoing side, transition midpoint, and incoming side;
- catalog misses satisfy the active policy;
- coverage reports expected, built, integrated, and verified counts separately.

The verification report treats candidate and unused staged counts as facts. Completion depends on required integrations, complete scene coverage, complete adjacent-boundary coverage, and observable implementation evidence.
