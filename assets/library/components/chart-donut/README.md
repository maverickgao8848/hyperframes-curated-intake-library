# chart-donut

Show up to four parts of a validated whole. The component contains no example data; callers must provide evidence and provenance.

- `data`: required chart-specific data payload.
- `total`: component parameter.
- `title`: component parameter.
- `sourceNote`: required source and date note.
- `emptyLabel`: component parameter.
- `durationFrames`: component parameter.
- `format`: component parameter.

Empty arrays render the controlled `emptyLabel` state. Invalid values are rejected before mount.

Legacy alias: `broll-charts.donut`.
