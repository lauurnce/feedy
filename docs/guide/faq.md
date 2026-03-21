# Frequently Asked Questions

- **Nothing was fetched.** Check the source is enabled, then credentials, then the upstream itself.
- **Where is my data?** In one SQLite file, at the path your config resolves to.
- **Is re-running safe?** Yes. Writes key on upstream id, so a repeated fetch adds nothing new.
