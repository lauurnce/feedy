# Data Model Notes

- The entry is the atomic unit of the system; every stage reads and writes entries.
- An entry always carries a source, an upstream id, a title, a URL and a timestamp.
- Optional fields default to None so "not provided" stays distinguishable from "empty".
- An upstream id must be stable across fetches, or deduplication silently stops working.
- Timestamps are UTC at rest; local time exists only at the moment of display.
