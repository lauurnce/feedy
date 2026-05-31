# Data Model Notes

- The entry is the atomic unit of the system; every stage reads and writes entries.
- An entry always carries a source, an upstream id, a title, a URL and a timestamp.
- Optional fields default to None so "not provided" stays distinguishable from "empty".
- An upstream id must be stable across fetches, or deduplication silently stops working.
- Timestamps are UTC at rest; local time exists only at the moment of display.
- The source field holds the registry name, tying an entry back to the adapter that produced it.
- Titles are plain text. Markup in a title is stripped at the source boundary.
- Bodies are stored exactly as fetched, so a rendering change never needs a re-fetch.
- The URL field holds the canonical permalink, not a share, tracking or redirect link.
- Author holds a display name where available and falls back to the upstream handle.
- Summaries live in their own field so generated text is never confused with upstream text.
- Derived values are computed on read; storing them invites the two copies to disagree.
- Schema changes are forward-only and additive wherever a default can be supplied.
- Tags are deliberately absent until there is a second consumer that actually needs them.
