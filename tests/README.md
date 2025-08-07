# Tests

Run the full suite with `make test`, or `uv run pytest -q` directly.

## Database isolation

Storage tests use an autouse `isolated_db` fixture that monkeypatches
`storage.DB_PATH` to a `tmp_path`, so no test touches a real database.
