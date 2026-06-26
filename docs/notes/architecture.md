# Architecture Notes

- The pipeline is linear: fetch, store, optionally summarise, render, deliver.
- Each stage runs on its own, so a failure in one never forces the others to re-run.
- Dependencies point inward toward storage; nothing in storage knows about sources or output.
- One entry point means one place where arguments, config and errors are handled.
- No module-level mutable state. State lives in storage or is passed explicitly.
