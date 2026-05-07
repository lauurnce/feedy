# Configuration Notes

- Configuration is one flat, readable file; nested structure is added only when it earns it.
- Precedence runs flags, then config file, then built-in defaults, highest first.
- Defaults live in code so a missing config file still yields a working run.
- Secrets are referenced from the environment rather than written into the config file.
