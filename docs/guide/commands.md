# Command Reference

- `fetch` — pull new items from every registered source and store them.
- Name a source to fetch just that one, which is the fastest way to isolate a failure.
- `list` — print stored entries, most recent first.
- `list --limit N` — cap the output at N rows; omit it to print everything matched.
- `stats` — show how many entries each source has contributed.
- `sources` — list every registered source name.
- `digest` — render stored entries for a window as a readable summary.
- `digest --format NAME` — choose the renderer; plain text is the default.
- Commands exit non-zero on failure so they compose properly inside shell scripts.
- Every command supports `--help`, which prints its options and a one-line description.
- Output stays readable when piped or redirected; no command requires a terminal.
- A successful run prints results only, which keeps scheduled job logs short.
- No command prompts for input, so every one of them is safe to run unattended.
- An explicit flag always wins over the config file, which in turn beats the built-in default.
- A scheduled job usually runs `fetch` then `digest`, in that order, as two separate commands.
