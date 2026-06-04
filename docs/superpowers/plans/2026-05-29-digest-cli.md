# Digest CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire up `feedy digest` CLI command to load today's entries, summarize them via AI, persist new summaries, and print the formatted digest.

**Architecture:** Extend the existing `digest` stub in `feedy/cli.py`. Import `summarize` (from `feedy.summarizer`) and `build_digest` (from `feedy.digest`). Default `--since` to today's date. Persist new AI summaries back to DB so repeat runs skip re-summarization.

**Tech Stack:** Python 3.11+, Click, pytest, unittest.mock, `feedy.storage`, `feedy.summarizer`, `feedy.digest`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `feedy/cli.py` | Add `--since`/`--source` options to `digest`; call `summarize`, `build_digest`, `storage.update_summary` |
| Modify | `tests/test_cli.py` | Add 8 tests for `digest` command |
| Modify | `roadmap.md` | Mark Day 14 complete |

---

### Task 1: Failing tests for `digest` command

**Files:**
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add the failing tests**

First, add `from datetime import datetime` to the imports at the top of `tests/test_cli.py` (it's not there yet):

```python
from datetime import datetime
```

Then append the following to `tests/test_cli.py`:

```python
def _make_digest_entries(source_name, count):
    return [
        {"url": f"https://{source_name}.com/{i}", "title": f"Title {i}", "date": "2026-05-29", "source": source_name, "summary": ""}
        for i in range(count)
    ]


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_no_entries_prints_message(mock_storage, mock_summarize, mock_build_digest):
    mock_storage.get_entries.return_value = []
    runner = CliRunner()
    result = runner.invoke(cli, ["digest"])
    assert result.exit_code == 0
    assert "No entries found." in result.output
    mock_summarize.assert_not_called()
    mock_build_digest.assert_not_called()


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_calls_summarize_with_entries(mock_storage, mock_summarize, mock_build_digest):
    entries = _make_digest_entries("hackernews", 2)
    mock_storage.get_entries.return_value = entries
    mock_summarize.return_value = entries
    mock_build_digest.return_value = ""
    runner = CliRunner()
    runner.invoke(cli, ["digest"])
    mock_summarize.assert_called_once_with(entries)


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_calls_build_digest_with_summarized(mock_storage, mock_summarize, mock_build_digest):
    entries = _make_digest_entries("hackernews", 1)
    summarized = [{**entries[0], "summary": "A great summary."}]
    mock_storage.get_entries.return_value = entries
    mock_summarize.return_value = summarized
    mock_build_digest.return_value = "## Hackernews\n• Title 0 — A great summary."
    runner = CliRunner()
    runner.invoke(cli, ["digest"])
    mock_build_digest.assert_called_once_with(summarized)


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_prints_build_digest_output(mock_storage, mock_summarize, mock_build_digest):
    entries = _make_digest_entries("hackernews", 1)
    mock_storage.get_entries.return_value = entries
    mock_summarize.return_value = entries
    mock_build_digest.return_value = "## Hackernews\n• Title 0"
    runner = CliRunner()
    result = runner.invoke(cli, ["digest"])
    assert result.exit_code == 0
    assert "## Hackernews" in result.output
    assert "Title 0" in result.output


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_defaults_since_to_today(mock_storage, mock_summarize, mock_build_digest):
    mock_storage.get_entries.return_value = []
    runner = CliRunner()
    runner.invoke(cli, ["digest"])
    today = datetime.now().strftime("%Y-%m-%d")
    mock_storage.get_entries.assert_called_once_with(source=None, since=today)


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_since_option_passed_to_storage(mock_storage, mock_summarize, mock_build_digest):
    mock_storage.get_entries.return_value = []
    runner = CliRunner()
    runner.invoke(cli, ["digest", "--since", "2026-05-01"])
    mock_storage.get_entries.assert_called_once_with(source=None, since="2026-05-01")


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_source_option_passed_to_storage(mock_storage, mock_summarize, mock_build_digest):
    mock_storage.get_entries.return_value = []
    runner = CliRunner()
    runner.invoke(cli, ["digest", "--source", "hackernews"])
    kwargs = mock_storage.get_entries.call_args[1]
    assert kwargs["source"] == "hackernews"


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_persists_new_summaries(mock_storage, mock_summarize, mock_build_digest):
    entries = [
        {"url": "https://hn.com/1", "title": "Post A", "date": "2026-05-29", "source": "hackernews", "summary": ""},
        {"url": "https://hn.com/2", "title": "Post B", "date": "2026-05-29", "source": "hackernews", "summary": "Already summarized."},
    ]
    summarized = [
        {"url": "https://hn.com/1", "title": "Post A", "date": "2026-05-29", "source": "hackernews", "summary": "New AI summary."},
        {"url": "https://hn.com/2", "title": "Post B", "date": "2026-05-29", "source": "hackernews", "summary": "Already summarized."},
    ]
    mock_storage.get_entries.return_value = entries
    mock_summarize.return_value = summarized
    mock_build_digest.return_value = ""
    runner = CliRunner()
    runner.invoke(cli, ["digest"])
    mock_storage.update_summary.assert_called_once_with("https://hn.com/1", "New AI summary.")
```

- [ ] **Step 2: Run tests to verify they fail**

```
.venv\Scripts\pytest.exe tests/test_cli.py -k "digest" -v
```

Expected: all 8 fail — `ImportError` for `summarize`/`build_digest` not imported in `cli.py`, or assertion errors against the stub.

- [ ] **Step 3: Commit**

```
git add tests/test_cli.py
git commit -m "test(cli): add failing tests for digest command"
```

---

### Task 2: Implement `digest` command in `feedy/cli.py`

**Files:**
- Modify: `feedy/cli.py`

- [ ] **Step 1: Add imports**

At the top of `feedy/cli.py`, after the existing imports, add:

```python
from feedy.digest import build_digest
from feedy.summarizer import summarize
```

- [ ] **Step 2: Replace the digest stub**

Replace the existing digest stub:

```python
@cli.command()
def digest():
    """Generate and print today's AI digest."""
    click.echo("digest: not yet implemented")
```

with:

```python
@cli.command()
@click.option("--since", default=None, help="Filter entries on or after date (YYYY-MM-DD). Defaults to today.")
@click.option("--source", default=None, help="Filter by source name.")
def digest(since, source):
    """Generate and print today's AI digest."""
    if since is None:
        since = datetime.now().strftime("%Y-%m-%d")

    entries = storage.get_entries(source=source, since=since)
    if not entries:
        click.echo("No entries found.")
        return

    summarized = summarize(entries)

    for original, updated in zip(entries, summarized):
        if updated["summary"] and updated["summary"] != original["summary"]:
            storage.update_summary(updated["url"], updated["summary"])

    click.echo(build_digest(summarized))
```

- [ ] **Step 3: Run digest tests to verify all 8 pass**

```
.venv\Scripts\pytest.exe tests/test_cli.py -k "digest" -v
```

Expected:
```
tests/test_cli.py::test_digest_no_entries_prints_message PASSED
tests/test_cli.py::test_digest_calls_summarize_with_entries PASSED
tests/test_cli.py::test_digest_calls_build_digest_with_summarized PASSED
tests/test_cli.py::test_digest_prints_build_digest_output PASSED
tests/test_cli.py::test_digest_defaults_since_to_today PASSED
tests/test_cli.py::test_digest_since_option_passed_to_storage PASSED
tests/test_cli.py::test_digest_source_option_passed_to_storage PASSED
tests/test_cli.py::test_digest_persists_new_summaries PASSED

8 passed
```

- [ ] **Step 4: Run full test suite to check for regressions**

```
.venv\Scripts\pytest.exe -v
```

Expected: all existing tests pass plus the 8 new digest tests.

- [ ] **Step 5: Commit**

```
git add feedy/cli.py
git commit -m "feat(cli): implement digest command with AI summarization"
```

---

### Task 3: Mark Day 14 complete

**Files:**
- Modify: `roadmap.md`

- [ ] **Step 1: Update roadmap**

In `roadmap.md`, change:

```
- [ ] Day 14 — CLI: `feedwise digest` — run summarizer and print today's digest
```

to:

```
- [x] Day 14 — CLI: `feedwise digest` — run summarizer and print today's digest
```

- [ ] **Step 2: Commit**

```
git add roadmap.md
git commit -m "chore: mark Day 14 complete"
```
