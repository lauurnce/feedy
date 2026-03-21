# Frequently Asked Questions

- **Nothing was fetched.** Check the source is enabled, then credentials, then the upstream itself.
- **Where is my data?** In one SQLite file, at the path your config resolves to.
- **Is re-running safe?** Yes. Writes key on upstream id, so a repeated fetch adds nothing new.
- **Entries seem missing.** Usually the database path changed, not the data disappearing.
- **Do I need an AI provider?** No. Summarisation is optional and everything works without it.
- **How big does it get?** Text entries are small; growth is slow unless you backfill heavily.
- **Are old entries pruned?** No. Storage is append-only and nothing is removed automatically.
- **Empty digest with data stored?** The window is probably wrong, not the data.
- **Can it run unattended?** Yes. It never prompts and exits non-zero on failure.
- **One source is down.** It is reported and skipped; the rest of the run continues.
- **Duplicate stories?** The same item from two sources is kept twice, deliberately.
- **Which sources exist?** Run `sources`; anything missing there is a registration problem.
- **Can the API add entries?** No. It is read-only; fetch is the only way data enters.
