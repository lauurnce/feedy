# Performance Notes

- Measure before optimising. Most perceived slowness here is a slow upstream, not slow code.
- Nearly all run time is network wait; local processing is negligible by comparison.
- Summarisation dominates cost when enabled, which is why results are cached with the entry.
