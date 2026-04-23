# CLI Notes

- The CLI parses arguments and prints results. All real work lives in the library modules.
- Commands are short verbs or plain nouns: `fetch`, `list`, `stats`, `sources`, `digest`.
- Routing output through one place keeps formatting consistent and easy to snapshot in tests.
- Exit non-zero on failure so the CLI composes properly inside shell scripts and CI.
- `--limit` caps rows for readability; omitting it returns everything the query matched.
- `sources` lists registered source names, which is the quickest check that a source loaded.
