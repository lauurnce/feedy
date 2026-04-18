# Source Notes

- A source owns one upstream service: fetching raw items and normalising them into `FeedEntry`.
- Sources should stay stateless. Persistence belongs to the storage layer, never to the fetcher.
- Module name, class name and registry key should all agree, e.g. `hackernews` -> `HackerNewsSource`.
- Every entry needs a stable upstream id so re-fetching the same item does not create duplicates.
- Timestamps are stored as UTC. Convert at the source boundary, never further downstream.
- An empty fetch is a valid result, not an error. Return an empty list rather than raising.
- Let transport errors propagate. The caller decides whether one bad source aborts the run.
- Sources pass through full text. Truncation is a presentation concern handled at digest time.
