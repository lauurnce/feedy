# Summariser Notes

- The summarizer turns one entry's text into a short summary and does nothing else.
- Summarisation is optional. Every downstream path must work with raw entries alone.
- If summarisation fails the original text is used, so a bad response never loses content.
- Summaries are stored alongside the entry so the same text is never paid for twice.
- Summaries target a couple of sentences; longer output defeats the point of a digest.
- Prompt text lives in one place so it can be tuned without touching orchestration logic.
- Entries already shorter than the target length are passed through untouched.
- The summariser interface is provider-agnostic; swapping the backend changes one module.
- Summaries stay in the source language unless translation is explicitly requested.
- Entries are stored first, so a summarisation outage never costs a fetch.
- Batching cuts overhead but complicates error attribution; single-entry calls stay the default.
- Summariser tests stub the provider, so the suite never depends on live model output.
- Oversized inputs are trimmed before sending, and the trim point is logged.
- Generated summaries are labelled as such so they are never mistaken for upstream text.
