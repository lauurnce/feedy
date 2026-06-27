# Performance Notes

- Measure before optimising. Most perceived slowness here is a slow upstream, not slow code.
- Nearly all run time is network wait; local processing is negligible by comparison.
- Summarisation dominates cost when enabled, which is why results are cached with the entry.
- Keying the cache on upstream id means the same item is never summarised twice.
- Index what is filtered on. Source and timestamp cover almost every query the tool makes.
- Batch only when per-call overhead is measurable; otherwise it just obscures error attribution.
- Concurrency across sources is tempting but adds failure modes; add it only if runs get slow.
- Rendering is cheap and in-memory; it is never the bottleneck in a run.
- Unbounded reads are fine today and dangerous later; limit at the call site as a habit.
- Reads stay fast as the database grows, provided the filter columns remain indexed.
- Storing full text costs disk but removes any need to re-fetch, which is the better trade.
- A suite that runs in seconds gets run constantly; that is worth protecting.
- Time each source separately before touching code; the culprit is usually obvious.
- One transaction per fetch batch beats one per row, and it is the only batching that clearly pays.
- A run holds one fetch in memory at a time, which keeps the footprint flat as history grows.
- Add paging when a single response starts feeling slow to render, not before.
- No optimisation lands without a before-and-after number; otherwise it is just churn.
