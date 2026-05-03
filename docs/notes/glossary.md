# Glossary

- **Entry** — one normalised item from an upstream source, the atomic unit of the system.
- **Source** — an adapter for one upstream service, responsible for fetch and normalisation.
- **Fetch** — one pass over sources that pulls new items and writes them to storage.
- **Digest** — a rendered, read-only view of stored entries over a chosen time window.
- **Registry** — the name-to-class mapping that lets the CLI resolve sources at runtime.
- **Upstream id** — the stable identifier assigned by the source service, used for dedup.
- **Summary** — generated short text derived from an entry, always stored separately from it.
- **Window** — the time range a digest covers, defaulting to the most recent fetch.
- **Renderer** — the component that turns selected entries into one output format.
