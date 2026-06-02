# Design Decisions

- SQLite was chosen because one file, zero setup and standard tooling suit a single-user tool.
- No ORM: the queries are few and simple, and raw SQL keeps the data access obvious.
- CLI-first because the primary use is a scheduled unattended run, not an interactive session.
- Append-only storage means a bug in normalisation never destroys previously captured data.
- UTC everywhere removes an entire class of bug at the cost of one conversion at display time.
- Summarisation is optional so the tool remains fully useful with no provider configured.
- A single shared schema avoids translation layers between every pair of stages.
