# chart-scatter

Show correlation and an optional size dimension. The component contains no example data; callers must provide evidence and provenance.

- `data`: required chart-specific data payload.
- `title`: component parameter.
- `sourceNote`: required source and date note.
- `emptyLabel`: component parameter.
- `durationFrames`: component parameter.
- `format`: component parameter.
- `xMin`: component parameter.
- `xMax`: component parameter.
- `yMin`: component parameter.
- `yMax`: component parameter.

Empty arrays render the controlled `emptyLabel` state. Invalid values are rejected before mount.

Legacy alias: `broll-charts.scatter`.
