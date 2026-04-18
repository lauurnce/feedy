# Source Notes

- A source owns one upstream service: fetching raw items and normalising them into `FeedEntry`.
- Sources should stay stateless. Persistence belongs to the storage layer, never to the fetcher.
- Module name, class name and registry key should all agree, e.g. `hackernews` -> `HackerNewsSource`.
