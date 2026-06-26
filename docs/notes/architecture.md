# Architecture Notes

- The pipeline is linear: fetch, store, optionally summarise, render, deliver.
- Each stage runs on its own, so a failure in one never forces the others to re-run.
- Dependencies point inward toward storage; nothing in storage knows about sources or output.
- One entry point means one place where arguments, config and errors are handled.
- No module-level mutable state. State lives in storage or is passed explicitly.
- Library modules return data; the CLI and web layer decide how to present it.
- Normalising at the source boundary means every later stage sees one uniform shape.
- One entry schema is shared end to end, so no stage needs a translation layer.
- Network and disk access sit at the edges, leaving the middle pure and easy to test.
