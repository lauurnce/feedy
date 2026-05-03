# Glossary

- **Entry** — one normalised item from an upstream source, the atomic unit of the system.
- **Source** — an adapter for one upstream service, responsible for fetch and normalisation.
- **Fetch** — one pass over sources that pulls new items and writes them to storage.
- **Digest** — a rendered, read-only view of stored entries over a chosen time window.
