# Design Decisions

- SQLite was chosen because one file, zero setup and standard tooling suit a single-user tool.
- No ORM: the queries are few and simple, and raw SQL keeps the data access obvious.
- CLI-first because the primary use is a scheduled unattended run, not an interactive session.
- Append-only storage means a bug in normalisation never destroys previously captured data.
- UTC everywhere removes an entire class of bug at the cost of one conversion at display time.
- Summarisation is optional so the tool remains fully useful with no provider configured.
- A single shared schema avoids translation layers between every pair of stages.
- Flat config is easier to read and diff; nesting is added only when a group genuinely exists.
- No daemon, because cron and CI already solve scheduling better than a bespoke loop would.
- Single-user scope keeps auth, permissions and concurrency entirely out of the design.
- Plain text is the default because it is readable everywhere and never needs escaping.
- Offline tests are fast and deterministic, which matters more here than end-to-end realism.
- Forward-only migrations halve the work and match how the tool is actually upgraded.
