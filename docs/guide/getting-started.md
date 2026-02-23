# Getting Started

- feedy collects items from several feeds into one local store and renders them as periodic digests.
- You need a recent Python and the project's lockfile; no database server or external service is required.
- Install from the committed lockfile so your versions match the ones the tests run against.
- Run `sources` first. If it prints the registered source names, the install is working.
- `fetch` pulls from every registered source and writes new items into the local database.
- `list` prints what has been stored, newest first, so you can confirm the fetch did something.
- Add `--limit` to `list` when you only want to glance at the most recent handful of entries.
- `stats` shows how many entries each source has contributed, which is the quickest health check.
- `digest` renders stored entries for the current window without changing anything on disk.
- `digest --format` selects the renderer when you want something other than the plain text default.
- Everything lives in a single SQLite file, so backing up your data means copying one file.
- Configuration is optional; without a config file the defaults are enough for a first run.
- Sources needing credentials read them from the environment, so nothing secret goes into a file.
- The suite runs offline in a couple of seconds and is the fastest way to check a change.
- Schedule the same command you run by hand; there is no daemon or special unattended mode.
- Pull, reinstall from the lockfile, then run the tests before your next scheduled fetch.
- Copy the database file while no run is in progress; that is the whole backup procedure.
