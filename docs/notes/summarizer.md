# Summariser Notes

- The summarizer turns one entry's text into a short summary and does nothing else.
- Summarisation is optional. Every downstream path must work with raw entries alone.
- If summarisation fails the original text is used, so a bad response never loses content.
- Summaries are stored alongside the entry so the same text is never paid for twice.
- Summaries target a couple of sentences; longer output defeats the point of a digest.
- Prompt text lives in one place so it can be tuned without touching orchestration logic.
- Entries already shorter than the target length are passed through untouched.
- The summariser interface is provider-agnostic; swapping the backend changes one module.
