# Storage Notes

- Storage owns persistence and nothing else: no fetching, no formatting, no notification.
- Re-inserting a known entry id is a no-op, which makes re-running a fetch safe.
- SQLite keeps the whole database in one file, which suits a single-user local tool.
- Entries are never edited in place. Corrections arrive as new rows, preserving history.
- Open a connection per operation. Long-lived connections complicate testing and cleanup.
- Index the columns used for filtering, chiefly source and published timestamp.
- Tests use a temporary database path so no run touches the developer's real data.
