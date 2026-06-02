# Design Decisions

- SQLite was chosen because one file, zero setup and standard tooling suit a single-user tool.
- No ORM: the queries are few and simple, and raw SQL keeps the data access obvious.
