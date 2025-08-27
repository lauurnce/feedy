# Data Model Notes

- The entry is the atomic unit of the system; every stage reads and writes entries.
- A FeedEntry carries exactly five keys: url, title, date, source and summary.
- Optional fields default to None so "not provided" stays distinguishable from "empty".
- The url must be stable across fetches, or deduplication silently stops working.
- The date field is an ISO 8601 calendar date string, not a full UTC timestamp.
- The source field holds the registry name, tying an entry back to the adapter that produced it.
- Titles are plain text. Markup in a title is stripped at the source boundary.
- Bodies are stored exactly as fetched, so a rendering change never needs a re-fetch.
- The URL field holds the canonical permalink, not a share, tracking or redirect link.
- Author holds a display name where available and falls back to the upstream handle.
- Summaries live in their own field so generated text is never confused with upstream text.
- Derived values are computed on read; storing them invites the two copies to disagree.
- Schema changes are forward-only and additive wherever a default can be supplied.
- Tags are deliberately absent until there is a second consumer that actually needs them.
- Stored entries are not edited. New information arrives as a new row, preserving history.
- Urls are unique globally, not per source, enforced by the UNIQUE constraint on entries.url.
- Adding a field means a migration, a default, a test and a line in these notes.
