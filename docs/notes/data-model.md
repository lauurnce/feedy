# Data Model Notes

- The entry is the atomic unit of the system; every stage reads and writes entries.
- An entry always carries a source, an upstream id, a title, a URL and a timestamp.
- Optional fields default to None so "not provided" stays distinguishable from "empty".
