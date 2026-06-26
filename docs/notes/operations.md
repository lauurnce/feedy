# Operations Notes

- Scheduled runs invoke the same CLI a human would, with no special code path.
- Unattended operation means no prompts, no interactive auth and a meaningful exit code.
- Scheduled runs log what was fetched and what failed, and nothing else at default level.
