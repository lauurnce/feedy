# Command Reference

- `fetch` — pull new items from every registered source and store them.
- Name a source to fetch just that one, which is the fastest way to isolate a failure.
- `list` — print stored entries, most recent first.
- `list --limit N` — cap the output at N rows; omit it to print everything matched.
- `stats` — show how many entries each source has contributed.
- `sources` — list every registered source name.
- `digest` — render stored entries for a window as a readable summary.
- `digest --format NAME` — choose the renderer; plain text is the default.
