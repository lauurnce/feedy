# Configuration Guide

- The config path comes from the working directory, so different projects can keep separate setups.
- Configuration is a single flat, readable file; there is no nested structure to learn.
- Every setting has a built-in default, so a missing config file still produces a working run.
- Precedence runs flags first, then the config file, then defaults.
- Environment variables override file values, which suits containers and scheduled jobs.
