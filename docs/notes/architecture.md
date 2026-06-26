# Architecture Notes

- The pipeline is linear: fetch, store, optionally summarise, render, deliver.
- Each stage runs on its own, so a failure in one never forces the others to re-run.
