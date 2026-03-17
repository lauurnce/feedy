# Configuration Guide

- The config path comes from the working directory, so different projects can keep separate setups.
- Configuration is a single flat, readable file; there is no nested structure to learn.
- Every setting has a built-in default, so a missing config file still produces a working run.
- Precedence runs flags first, then the config file, then defaults.
- Environment variables override file values, which suits containers and scheduled jobs.
- Supply secrets through the environment; never write a token into the config file.
- Point the database path wherever you like; the CLI and tests can use different files.
- Source settings are prefixed with the source name, so one flat file has no collisions.
- Enable a source in config rather than editing code; registration and activation are separate.
- Summarisation is off until a provider is configured, and the tool works fully without it.
- Configure zero or more delivery channels; with none configured a run simply delivers nothing.
