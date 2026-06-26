# Operations Notes

- Scheduled runs invoke the same CLI a human would, with no special code path.
- Unattended operation means no prompts, no interactive auth and a meaningful exit code.
- Scheduled runs log what was fetched and what failed, and nothing else at default level.
- A non-zero exit lets the scheduler surface failures without parsing log output.
- A routine run should finish in seconds; anything longer suggests an upstream problem.
- A missed run needs no recovery step; the next fetch picks up whatever is still available.
- A routine run never migrates schema or deletes data; both are explicit manual actions.
- Rotating a credential means updating the environment; no code or database change is needed.
- Storage grows monotonically. Check the file size occasionally rather than assuming it is small.
- Writes key on upstream id, so running fetch twice in a row changes nothing.
- An upstream outage is reported and skipped; it is not a reason to fail the whole run.
- Each run ends with a one-line summary of entries added per source.
- Text entries are small; the database stays modest until backfill is used aggressively.
- No daemon. The tool starts, does its work and exits, which suits cron and CI alike.
- After a failure, check which source reported it before looking anywhere else.
