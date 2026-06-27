# Performance Notes

- Measure before optimising. Most perceived slowness here is a slow upstream, not slow code.
- Nearly all run time is network wait; local processing is negligible by comparison.
- Summarisation dominates cost when enabled, which is why results are cached with the entry.
- Keying the cache on upstream id means the same item is never summarised twice.
- Index what is filtered on. Source and timestamp cover almost every query the tool makes.
- Batch only when per-call overhead is measurable; otherwise it just obscures error attribution.
- Concurrency across sources is tempting but adds failure modes; add it only if runs get slow.
