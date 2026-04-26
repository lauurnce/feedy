# Digest Notes

- A digest is a rendered view of stored entries over a window, not a second copy of the data.
- Building a digest is a read-only operation and can be repeated without side effects.
- The default window covers the most recent run. Wider windows are requested explicitly.
- Grouping by source keeps related items together and makes a long digest scannable.
- Within a group, entries run newest first so the freshest item is read first.
- An empty digest still renders, with a short line saying nothing new arrived.
- Selecting entries and rendering them are separate steps, so formats share one selection.
- Plain text is the baseline format and must stay readable in a terminal without wrapping.
- HTML output escapes entry content, since upstream bodies are untrusted markup.
- Bodies are trimmed at a sentence boundary where possible, never mid-word.
- Every entry links back to its canonical URL so the digest stays a jumping-off point.
- Digests stay text-only, which keeps them small and readable in any mail client.
