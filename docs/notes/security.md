# Security Notes

- The threat model assumes a single trusted operator on a local machine, not a public service.
- No credential is ever written into source. Config and environment are the only sources.
- Secrets are never logged, not even at debug level and not even partially masked.
- Everything fetched from upstream is untrusted input and is treated as such downstream.
- Any format that can execute markup escapes entry content before rendering it.
- The web layer assumes a trusted network; exposing it publicly requires a proxy with auth.
- Dependencies are updated deliberately, with the lockfile committed so builds stay reproducible.
- Upstream data is never evaluated, templated or interpolated into anything executable.
- The database holds fetched content and credentials-adjacent metadata; keep it user-readable only.
