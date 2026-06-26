# Operations Notes

- Scheduled runs invoke the same CLI a human would, with no special code path.
- Unattended operation means no prompts, no interactive auth and a meaningful exit code.
- Scheduled runs log what was fetched and what failed, and nothing else at default level.
- A non-zero exit lets the scheduler surface failures without parsing log output.
- A routine run should finish in seconds; anything longer suggests an upstream problem.
- A missed run needs no recovery step; the next fetch picks up whatever is still available.
