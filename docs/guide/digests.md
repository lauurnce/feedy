# Working with Digests

- A digest is a rendered view of what you already stored; building one never fetches anything.
- By default a digest covers the most recent run, which suits a fetch-then-digest schedule.
- Widen the window explicitly when you want a weekly roundup rather than a per-run summary.
- Formats are selected by name, so adding one never changes how the command is invoked.
- Plain text is the default and stays readable in a terminal or a plain-text email.
- HTML output escapes entry content, since upstream bodies are untrusted markup.
- Entries are grouped by source, with a heading showing the source name and its item count.
