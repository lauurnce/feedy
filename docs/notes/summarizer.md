# Summariser Notes

- The summarizer turns one entry's text into a short summary and does nothing else.
- Summarisation is optional. Every downstream path must work with raw entries alone.
- If summarisation fails the original text is used, so a bad response never loses content.
