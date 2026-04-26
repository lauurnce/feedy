# Digest Notes

- A digest is a rendered view of stored entries over a window, not a second copy of the data.
- Building a digest is a read-only operation and can be repeated without side effects.
- The default window covers the most recent run. Wider windows are requested explicitly.
- Grouping by source keeps related items together and makes a long digest scannable.
- Within a group, entries run newest first so the freshest item is read first.
- An empty digest still renders, with a short line saying nothing new arrived.
