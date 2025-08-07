# Tests

Run the full suite with `make test`, or `uv run pytest -q` directly.

## Database isolation

Storage tests use an autouse `isolated_db` fixture that monkeypatches
`storage.DB_PATH` to a `tmp_path`, so no test touches a real database.

## No network

The suite runs fully offline. Source tests stub the transport rather than
fetching, which keeps runs fast and deterministic.

## Naming

Test names describe the behaviour asserted, so a failure reads as a sentence.
One test file per module under test.
