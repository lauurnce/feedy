# Security Notes

- The threat model assumes a single trusted operator on a local machine, not a public service.
- No credential is ever written into source. Config and environment are the only sources.
- Secrets are never logged, not even at debug level and not even partially masked.
