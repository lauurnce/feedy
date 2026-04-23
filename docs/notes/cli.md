# CLI Notes

- The CLI parses arguments and prints results. All real work lives in the library modules.
- Commands are short verbs or plain nouns: `fetch`, `list`, `stats`, `sources`, `digest`.
- Routing output through one place keeps formatting consistent and easy to snapshot in tests.
- Exit non-zero on failure so the CLI composes properly inside shell scripts and CI.
- `--limit` caps rows for readability; omitting it returns everything the query matched.
- `sources` lists registered source names, which is the quickest check that a source loaded.
- Successful runs print results only. Progress chatter belongs behind a verbose flag.
- Validate arguments before doing any work so bad input fails fast and cheaply.
- Boolean flags default to off. Turning a feature on is always the explicit choice.
- User-facing errors are one readable line. Tracebacks stay behind a debug flag.
- Command tests invoke the CLI entry point directly and assert on captured output.
- No interactive prompts: the CLI must run unattended in scheduled jobs.
