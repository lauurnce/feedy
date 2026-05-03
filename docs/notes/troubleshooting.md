# Troubleshooting Notes

- Empty fetch: check the source is registered, then check credentials, then check the upstream.
- Run `sources` first. If a source is missing there, the problem is registration, not network.
- If an entry seems missing, confirm it was fetched before assuming storage dropped it.
- Pointing at an old database path is a common cause of "my entries disappeared".
- Duplicates usually mean the upstream id changed, not that dedup is broken.
- For a failed scheduled run, reproduce locally with the same config before changing code.
- Print the resolved config first; most "ignored setting" reports are precedence surprises.
- An order-dependent test almost always points at shared state left over between runs.
- If timestamps look shifted, check where local time entered the pipeline instead of UTC.
- Fetch one source at a time to isolate which upstream is actually failing.
- A malformed payload should fail loudly for that source only, not abort the whole run.
