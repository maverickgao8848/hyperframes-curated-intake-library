# Artifact contract

Each decision has one narrow authority.

| Artifact | Authority |
| --- | --- |
| `BRIEF.md` | intent, audience, delivery, confirmed Frame, asset policy, curation policy, run boundary |
| `frame.md` | visual system, composition language, typography, color, material, density, camera and motion character |
| `STORYBOARD.md` | scene order, stable identity, canonical composition path, purpose, source relation, timing, narrative beats and the complete adjacent-scene transition map |
| `scene-contracts/<id>.json` | approved teaching classification, concrete construction, layers, incoming transition, asset bindings, directed integrations, text plan, motion phases and evidence targets |
| `hyperframes.json` | Registry endpoint and project installation paths |
| `.hyperframes/curation.json` | bounded candidate palette, provenance, policy and catalog misses |
| `.hyperframes/build-plan.json` | exact selected scene integrations and adjacent-boundary transitions with expected staging/integration methods |
| `.hyperframes/intake-handoff.json` | complete expected scene set, canonical paths, timing, artifact hashes and next-stage state |
| `.media/manifest.jsonl` | adopted media path, source, hash and required status |
| `.hyperframes/usage.json` | later Build evidence for integrated scene elements |
| `*.motion.json` | later Build evidence for ordering, text appearance and ambient liveness |
| `.hyperframes/curated-intake-request.json` | optional routed-mode parent hash, cluster scope, inherited decisions, locks, assets, timing, and open questions |
| `.hyperframes/curated-intake-result.json` | routed-mode teaching result returned for bounded upstream merge; never authority over the parent plan |

## Identity

Every scene carries one stable value across:

```text
sceneId
= STORYBOARD src stem
= scene-contract filename stem
= composition data-composition-id
= motion-sidecar stem
= build-plan sceneId
= usage scene id
```

The handoff manifest lists the complete expected scene set. Preflight and build verification use that set as their denominator.

In routed mode, the parent `director-plan.json` remains the sole whole-film machine authority. Curated files may refer to it by path/hash but never replace it. Only the Visual Director's bounded merge accepts result fields and returns affected segments to review.

## Paths and provenance

Project runtime dependencies use project-relative paths. Shared Frame and media sources are copied into the project with SHA-256 provenance. The copy-ready prompt may name the absolute project root for discovery; generated runtime files resolve dependencies within that root.

## State model

Registry items and selected transition Blocks advance through observable states:

```text
candidate → selected-for-build → staged → integrated → verified
```

Each state has its own file and evidence. A later state includes evidence beyond the earlier state.
