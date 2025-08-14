# Working with Digests

- A digest is a rendered view of what you already stored; building one never fetches anything.
- By default a digest covers the most recent run, which suits a fetch-then-digest schedule.
- Widen the window explicitly when you want a weekly roundup rather than a per-run summary.
- Formats are selected by name, so adding one never changes how the command is invoked.
- Markdown is the default output format; `plain` is the alternative.
- HTML output escapes entry content, since upstream bodies are untrusted markup.
- Entries are grouped by source, with a heading showing the source name and its item count.
- Within each group entries run newest first, so the freshest item is read first.
- If nothing new arrived, the digest still renders with a short line saying so.
- Delivery is separate from rendering, so you can print a digest without sending it anywhere.
- The same entries always render identically, which makes digests easy to diff or test.
- Digests write to standard output, so redirecting to a file needs no special option.
