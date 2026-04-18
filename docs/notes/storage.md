# Storage Notes

- Storage owns persistence and nothing else: no fetching, no formatting, no notification.
- Re-inserting a known entry id is a no-op, which makes re-running a fetch safe.
