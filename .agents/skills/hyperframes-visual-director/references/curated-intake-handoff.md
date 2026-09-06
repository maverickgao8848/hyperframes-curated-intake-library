# Curated Intake handoff

A `hyperframes-visual-director/curated-request-v3` request names `parentPlanPath`, `parentPlanHash`, `clusterId`, `segmentIds`, approved scope, locked decisions, inherited visual policy/timing/assets, and remaining questions. `approvedScope.segmentSceneMap` is the stable segment-to-scene authority: its keys exactly equal requested segments, an empty list means no scenes, and a scene ID occurs under exactly one segment. `sceneLocks` may name only those mapped scene IDs.

Curated Intake verifies the parent hash and segment IDs, restates inherited decisions, and asks only missing or contradictory questions. If animation-worthy sentences inside the cluster are still unspecified, it asks for that sub-scope. It may return a `scope-change-proposal`, but it cannot change parent coverage, non-cluster segments, or locked decisions.

The result schema is `hyperframes-visual-director/curated-result-v3`. It carries the same parent hash and requested segment IDs plus bounded Storyboard v3 scene patches, catalog misses, and an optional scope-change proposal. `merge-curated-result.py` requires the originating request and rejects unknown, duplicate, or cross-segment scene patches before applying request/existing locks and returning affected segments to review; it never lets the result overwrite the parent directly.
