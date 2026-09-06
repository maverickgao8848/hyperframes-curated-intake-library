# chart-stacked-bar

Show composition across ordered groups. The component contains no example data; callers must provide evidence and provenance.

- `data`: required chart-specific data payload.
- `title`: component parameter.
- `sourceNote`: required source and date note.
- `emptyLabel`: component parameter.
- `durationFrames`: component parameter.
- `format`: component parameter.

Empty arrays render the controlled `emptyLabel` state. Invalid values are rejected before mount.

Legacy alias: `broll-charts.stacked`.
