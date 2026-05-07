# Configuration Notes

- Configuration is one flat, readable file; nested structure is added only when it earns it.
- Precedence runs flags, then config file, then built-in defaults, highest first.
- Defaults live in code so a missing config file still yields a working run.
- Secrets are referenced from the environment rather than written into the config file.
- Config is validated at startup, so a typo fails immediately instead of mid-run.
- An unknown key is a warning, not an error, so old configs keep working after upgrades.
- Source settings are namespaced by source name, keeping one flat file collision-free.
- Printing the resolved config is the fastest way to settle a precedence question.
- Config is read once at startup; re-reading mid-run would make behaviour hard to reason about.
- A missing config file is fine. Every setting has a default that produces a sane run.
- Relative paths resolve against the working directory, which keeps test setups simple.
- Values are coerced to their expected type on load, so downstream code never parses strings.
- Environment variables override file values, which suits containerised and scheduled runs.
- Every new setting gets a default and a one-line description in the same commit.
- Booleans default to false, so new behaviour is always opt-in for existing users.
