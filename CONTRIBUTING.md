# Contributing

## Workflow

1. Branch from `main`.
2. Keep production projects under the ignored `projects/` directory.
3. Make the smallest coherent change to skills, schemas, tests, and library metadata.
4. Run `pytest -q` before opening a pull request.
5. Open a pull request with the motivation, validation evidence, and any library provenance or licensing impact.

## Library changes

A library contribution should include all applicable source files, catalog entries, registry projections, previews, provenance, hashes, and license metadata. Generated renders, snapshots, thumbnails, waveform caches, dependency directories, and private project files must not be committed.

Do not add an asset when its redistribution rights are unclear. If an asset is only a local reference, keep it outside `library/` and describe the requirement without committing the file.

## Skill and contract changes

Treat curated-intake instructions and JSON contracts as public interfaces for collaborators. Update schemas, fixtures, and tests together when changing a field or behavior. Preserve deterministic output unless the pull request explicitly documents why an output contract must change.

## Pull-request checklist

- The working tree contains no credentials or private project data.
- `pytest -q` passes, with any skips explained.
- New or changed library entries include provenance and license metadata.
- Generated output and local dependency directories remain ignored.
- README or reference documentation reflects user-visible workflow changes.
