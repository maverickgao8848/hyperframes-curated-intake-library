# HyperFrames Curated Intake & Shared Library

This repository packages one release-ready workspace skill and its shared production library:

- `hyperframes-curated-intake`: source-aware curation and project handoff.

## Quick start

```powershell
git clone https://github.com/maverickgao8848/hyperframes-curated-intake-library.git
cd hyperframes-curated-intake-library
python -m pip install -e .
pytest -q
```

Open the cloned folder as a Codex workspace. The release-ready skill lives at `.agents/skills/hyperframes-curated-intake/`; invoke `hyperframes-curated-intake` for approved source selection, library curation, and project handoff.

## Requirements

- Python 3.11 or newer
- Node.js for HyperFrames verification and rendering workflows

Install the Python dependency and run the test suite:

```powershell
python -m pip install -e .
pytest -q
```

## Repository layout

- `.agents/skills/hyperframes-curated-intake/` — the released skill instructions, scripts, references, and schemas.
- `library/` — the shared catalog, registry projection, components, media, frames, previews, provenance, and per-asset license metadata.
- `schemas/` — the shared library schema.
- `tests/` — curated-intake and library verification coverage.
- `docs/` — redistribution authorization and source provenance used by library metadata.

Local production work belongs under `projects/` and is intentionally ignored. Promote only maintained, redistributable examples into `examples/`.

## Library policy

The complete `library/` directory is versioned so a fresh clone has the same catalog and local assets used by the skills and tests. Do not add generated dependency directories, thumbnails, waveform caches, or render outputs. Check each asset's catalog and license metadata before redistributing it outside this repository.

The registry contains self-contained installable bundles. Some fonts and runtimes therefore appear at multiple paths so an individual block or component can be copied without reaching back into the repository. Git stores identical content as one blob, so these paths do not multiply repository transfer size in the same way ordinary file copies would.

When changing the library, keep the catalog, provenance, preview, registry projection, and license metadata consistent in the same pull request. Do not commit a local production project as a substitute for a maintained fixture.

## Verification

The expected repository-level check is:

```powershell
pytest -q
```

A test failure should be resolved before publishing changes to the shared library or curated-intake contracts.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the collaboration workflow and pull-request checklist.

## Licensing

Library entries carry their own provenance and license metadata. The repository does not currently declare a blanket project license; add one before offering broad public reuse of the source code.
