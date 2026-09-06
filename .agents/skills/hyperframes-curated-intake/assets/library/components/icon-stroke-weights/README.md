# icon-stroke-weights

Compare or select a controlled semantic stroke hierarchy.

- `iconId`: required ID from the frozen 24-icon local allowlist.
- `strokeWeight`: controlled weight; allowed runtime values are 1.5, 2, 2.5, or 3.
- `title`: teaching title.
- `label`: semantic explanation.
- `durationFrames`: deterministic seek window.

The component reads only frozen repository SVGs recorded in
`assets/svg/lucide-teaching-core/manifest.json`. Do not mix unapproved line weights in one scene.
