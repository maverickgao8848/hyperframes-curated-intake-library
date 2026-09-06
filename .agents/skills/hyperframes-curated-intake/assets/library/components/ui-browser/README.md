# ui-browser

Show project-provided page content inside an explicit mock browser.

- `data`: required project-provided semantic content.
- `mock`: required and must be `true`; the rendered DOM is marked as simulated and non-evidence.
- `title`: required teaching title.
- `sourceNote`: required source/date note.
- `durationFrames`: deterministic seek window.

Prefer a real screenshot when interface evidence exists. Legacy alias: `broll-ui.browser`.
