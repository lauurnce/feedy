# Config File Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a TOML config file (`~/.feedy/config.toml`) that controls which sources `fetch` runs, supplies a fallback Anthropic API key, and selects the digest output format.

**Architecture:** New `feedy/config.py` with a `Config` dataclass and `load_config()` reader using stdlib `tomllib`. Wire it into `fetch` (source filtering via a call-time registry), `ai.complete` (API key fallback, env var still wins), `build_digest` (new `output_format` param), and the `digest` command. Missing file or keys fall back to defaults.

**Tech Stack:** Python 3.11+ stdlib (`tomllib`, `dataclasses`, `pathlib`), Click, pytest, unittest.mock

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `feedy/config.py` | `Config` dataclass + `load_config()` |
| Create | `tests/test_config.py` | config loading tests |
| Modify | `feedy/ai.py` | API key fallback to config |
| Modify | `tests/test_ai.py` | config fallback + env precedence tests |
| Modify | `feedy/digest.py` | `output_format` param |
| Modify | `tests/test_digest.py` | plain-format tests |
| Modify | `feedy/cli.py` | fetch source filtering + digest output format |
| Modify | `tests/test_cli.py` | fetch config tests + digest format test |
| Modify | `ROADMAP.md` | mark Day 16 complete |

---

### Task 1: `feedy/config.py` — Config dataclass + loader

**Files:**
- Create: `feedy/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_config.py`:

```python
from pathlib import Path

from feedy.config import Config, load_config


def test_missing_file_returns_defaults(tmp_path):
    cfg = load_config(tmp_path / "nope.toml")
    assert cfg.sources == ["telegram", "tiktok", "meta", "hackernews"]
    assert cfg.output_format == "markdown"
    assert cfg.api_key is None


def test_default_config_constructor():
    cfg = Config()
    assert cfg.sources == ["telegram", "tiktok", "meta", "hackernews"]
    assert cfg.output_format == "markdown"
    assert cfg.api_key is None


def test_reads_sources(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('sources = ["telegram", "hackernews"]\n', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.sources == ["telegram", "hackernews"]


def test_reads_output_format(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('output_format = "plain"\n', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.output_format == "plain"


def test_reads_api_key(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[anthropic]\napi_key = "sk-test-123"\n', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.api_key == "sk-test-123"


def test_partial_file_uses_defaults_for_missing_keys(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('output_format = "plain"\n', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.output_format == "plain"
    assert cfg.sources == ["telegram", "tiktok", "meta", "hackernews"]
    assert cfg.api_key is None


def test_empty_anthropic_table_gives_none_key(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("[anthropic]\n", encoding="utf-8")
    cfg = load_config(path)
    assert cfg.api_key is None
```

- [ ] **Step 2: Run tests to verify they fail**

```
.venv\Scripts\pytest.exe tests/test_config.py -v
```

Expected: all fail with `ModuleNotFoundError: No module named 'feedy.config'`.

- [ ] **Step 3: Write the implementation**

Create `feedy/config.py`:

```python
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_PATH = Path.home() / ".feedy" / "config.toml"

DEFAULT_SOURCES = ["telegram", "tiktok", "meta", "hackernews"]
DEFAULT_OUTPUT_FORMAT = "markdown"


@dataclass
class Config:
    sources: list[str] = field(default_factory=lambda: list(DEFAULT_SOURCES))
    output_format: str = DEFAULT_OUTPUT_FORMAT
    api_key: str | None = None


def load_config(path: Path | None = None) -> Config:
    """Load config from a TOML file. Return defaults if the file is missing."""
    if path is None:
        path = CONFIG_PATH
    if not path.exists():
        return Config()
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return Config(
        sources=data.get("sources", list(DEFAULT_SOURCES)),
        output_format=data.get("output_format", DEFAULT_OUTPUT_FORMAT),
        api_key=data.get("anthropic", {}).get("api_key"),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```
.venv\Scripts\pytest.exe tests/test_config.py -v
```

Expected: all 7 pass.

- [ ] **Step 5: Commit**

```
git add feedy/config.py tests/test_config.py
git commit -m "feat(config): add Config dataclass and load_config() TOML reader"
```

---

### Task 2: API key fallback in `feedy/ai.py`

**Files:**
- Modify: `feedy/ai.py`
- Modify: `tests/test_ai.py`

- [ ] **Step 1: Update the two existing key tests and add fallback/precedence tests**

In `tests/test_ai.py`, add `Config` import. The current imports are:

```python
import os
from unittest.mock import MagicMock, patch

import anthropic
import pytest

from feedy.ai import complete
```

Add this line after `from feedy.ai import complete`:

```python
from feedy.config import Config
```

Replace the existing `test_complete_missing_key`:

```python
def test_complete_missing_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = complete("say hello")
    assert result is None
```

with:

```python
def test_complete_missing_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("feedy.ai.load_config", return_value=Config(api_key=None)):
        result = complete("say hello")
    assert result is None
```

Replace the existing `test_complete_empty_key`:

```python
def test_complete_empty_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    result = complete("say hello")
    assert result is None
```

with:

```python
def test_complete_empty_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    with patch("feedy.ai.load_config", return_value=Config(api_key=None)):
        result = complete("say hello")
    assert result is None
```

Then append two new tests to the end of `tests/test_ai.py`:

```python
def test_complete_falls_back_to_config_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    mock_client = _mock_client("from config")
    with patch("feedy.ai.load_config", return_value=Config(api_key="cfg-key")), \
         patch("feedy.ai.anthropic.Anthropic", return_value=mock_client) as mock_anthropic:
        result = complete("say hello")
    assert result == "from config"
    mock_anthropic.assert_called_once_with(api_key="cfg-key")


def test_complete_env_key_takes_precedence_over_config(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
    mock_client = _mock_client("from env")
    with patch("feedy.ai.load_config", return_value=Config(api_key="cfg-key")), \
         patch("feedy.ai.anthropic.Anthropic", return_value=mock_client) as mock_anthropic:
        result = complete("say hello")
    assert result == "from env"
    mock_anthropic.assert_called_once_with(api_key="env-key")
```

- [ ] **Step 2: Run the ai tests to verify the two new tests fail**

```
.venv\Scripts\pytest.exe tests/test_ai.py -v
```

Expected: `test_complete_falls_back_to_config_key` and `test_complete_env_key_takes_precedence_over_config` FAIL (`feedy.ai` has no `load_config` to patch → `AttributeError`). The two edited tests also fail for the same patch-target reason.

- [ ] **Step 3: Update `feedy/ai.py`**

Current `feedy/ai.py`:

```python
from __future__ import annotations

import os

import anthropic

_MODEL = "claude-haiku-4-5-20251001"
_MAX_TOKENS = 300


def complete(prompt: str) -> str | None:
    """Call the Anthropic API with prompt; return text or None on any failure."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return None
    client = anthropic.Anthropic(api_key=key)
    try:
        message = client.messages.create(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError:
        return None
    if not message.content or not hasattr(message.content[0], "text"):
        return None
    return message.content[0].text.strip()
```

Change the imports block and the key-resolution line. Add the import:

```python
from feedy.config import load_config
```

so the top of the file reads:

```python
from __future__ import annotations

import os

import anthropic

from feedy.config import load_config

_MODEL = "claude-haiku-4-5-20251001"
_MAX_TOKENS = 300
```

Then replace:

```python
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return None
```

with:

```python
    key = os.environ.get("ANTHROPIC_API_KEY") or (load_config().api_key or "")
    if not key:
        return None
```

- [ ] **Step 4: Run the ai tests to verify all pass**

```
.venv\Scripts\pytest.exe tests/test_ai.py -v
```

Expected: all 8 tests pass (6 original + 2 new).

- [ ] **Step 5: Commit**

```
git add feedy/ai.py tests/test_ai.py
git commit -m "feat(ai): fall back to config api_key when env var unset"
```

---

### Task 3: `output_format` param in `feedy/digest.py`

**Files:**
- Modify: `feedy/digest.py`
- Modify: `tests/test_digest.py`

- [ ] **Step 1: Add failing tests for plain format**

Append to `tests/test_digest.py`:

```python
def test_plain_format_has_no_markdown_header():
    entries = [{"url": "https://ex.com", "title": "My Post", "date": "2026-05-29", "source": "telegram", "summary": "Sum."}]
    result = build_digest(entries, output_format="plain")
    assert "## " not in result
    assert "TELEGRAM" in result


def test_plain_format_uses_dash_bullet():
    entries = [{"url": "https://ex.com", "title": "My Post", "date": "2026-05-29", "source": "telegram", "summary": "Sum."}]
    result = build_digest(entries, output_format="plain")
    assert "- My Post — Sum." in result
    assert "•" not in result


def test_markdown_is_default():
    entries = [{"url": "https://ex.com", "title": "My Post", "date": "2026-05-29", "source": "telegram", "summary": "Sum."}]
    result = build_digest(entries)
    assert "## Telegram" in result
    assert "• My Post — Sum." in result
```

- [ ] **Step 2: Run digest tests to verify the new ones fail**

```
.venv\Scripts\pytest.exe tests/test_digest.py -v
```

Expected: `test_plain_format_has_no_markdown_header` and `test_plain_format_uses_dash_bullet` FAIL (`build_digest()` takes no `output_format` arg → `TypeError`). `test_markdown_is_default` passes already.

- [ ] **Step 3: Update `feedy/digest.py`**

Current `feedy/digest.py`:

```python
from __future__ import annotations

from collections import defaultdict

from feedy.sources.base import FeedEntry


def build_digest(entries: list[FeedEntry]) -> str:
    """Group entries by source and format as a readable digest string."""
    if not entries:
        return ""

    groups: dict[str, list[FeedEntry]] = defaultdict(list)
    for entry in entries:
        groups[entry["source"]].append(entry)

    sections = []
    for source in sorted(groups):
        lines = [f"## {source.title()}"]
        for entry in groups[source]:
            if entry["summary"]:
                lines.append(f"• {entry['title']} — {entry['summary']}")
            else:
                lines.append(f"• {entry['title']}")
        sections.append("\n".join(lines))

    return "\n\n".join(sections)
```

Replace the whole function with:

```python
def build_digest(entries: list[FeedEntry], output_format: str = "markdown") -> str:
    """Group entries by source and format as a readable digest string."""
    if not entries:
        return ""

    groups: dict[str, list[FeedEntry]] = defaultdict(list)
    for entry in entries:
        groups[entry["source"]].append(entry)

    sections = []
    for source in sorted(groups):
        if output_format == "plain":
            header = source.upper()
            bullet = "- "
        else:
            header = f"## {source.title()}"
            bullet = "• "
        lines = [header]
        for entry in groups[source]:
            if entry["summary"]:
                lines.append(f"{bullet}{entry['title']} — {entry['summary']}")
            else:
                lines.append(f"{bullet}{entry['title']}")
        sections.append("\n".join(lines))

    return "\n\n".join(sections)
```

- [ ] **Step 4: Run digest tests to verify all pass**

```
.venv\Scripts\pytest.exe tests/test_digest.py -v
```

Expected: all pass (6 original + 3 new).

- [ ] **Step 5: Commit**

```
git add feedy/digest.py tests/test_digest.py
git commit -m "feat(digest): add output_format param for plain-text rendering"
```

---

### Task 4: `fetch` reads sources from config

**Files:**
- Modify: `feedy/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Update the three existing fetch tests and add a filtering test**

In `tests/test_cli.py`, add the `Config` import. Current import block:

```python
from datetime import datetime
from unittest.mock import patch
from click.testing import CliRunner
from feedy.cli import cli
```

Add after the last import:

```python
from feedy.config import Config
```

The three existing fetch tests each need an added `@patch("feedy.cli.load_config")` decorator (outermost, so its mock is the LAST positional arg) and a line setting the returned config's sources to all four. Apply these edits:

**`test_fetch_prints_per_source_summary`** — change the decorator stack and signature, and add the config line. Replace:

```python
@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_prints_per_source_summary(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage
):
    mock_telegram_cls.return_value.name = "telegram"
```

with:

```python
@patch("feedy.cli.load_config")
@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_prints_per_source_summary(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage, mock_load_config
):
    mock_load_config.return_value = Config(sources=["telegram", "tiktok", "meta", "hackernews"])
    mock_telegram_cls.return_value.name = "telegram"
```

**`test_fetch_total_counts_only_saved`** — replace:

```python
@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_total_counts_only_saved(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage
):
    for cls, name in [
```

with:

```python
@patch("feedy.cli.load_config")
@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_total_counts_only_saved(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage, mock_load_config
):
    mock_load_config.return_value = Config(sources=["telegram", "tiktok", "meta", "hackernews"])
    for cls, name in [
```

**`test_fetch_continues_after_source_error`** — replace:

```python
@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_continues_after_source_error(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage
):
    mock_telegram_cls.return_value.name = "telegram"
    mock_telegram_cls.return_value.run.side_effect = RuntimeError("network down")
```

with:

```python
@patch("feedy.cli.load_config")
@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_continues_after_source_error(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage, mock_load_config
):
    mock_load_config.return_value = Config(sources=["telegram", "tiktok", "meta", "hackernews"])
    mock_telegram_cls.return_value.name = "telegram"
    mock_telegram_cls.return_value.run.side_effect = RuntimeError("network down")
```

Then add a new filtering test. Insert it directly after `test_fetch_continues_after_source_error` (before the `_make_list_entry` helper):

```python
@patch("feedy.cli.load_config")
@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_only_runs_configured_sources(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage, mock_load_config
):
    mock_load_config.return_value = Config(sources=["telegram", "hackernews"])
    mock_telegram_cls.return_value.name = "telegram"
    mock_telegram_cls.return_value.run.return_value = []
    mock_hn_cls.return_value.name = "hackernews"
    mock_hn_cls.return_value.run.return_value = []
    mock_storage.save_many.return_value = (0, 0)

    runner = CliRunner()
    result = runner.invoke(cli, ["fetch"])

    mock_telegram_cls.return_value.run.assert_called_once()
    mock_hn_cls.return_value.run.assert_called_once()
    mock_tiktok_cls.return_value.run.assert_not_called()
    mock_meta_cls.return_value.run.assert_not_called()
    assert result.exit_code == 0
    assert "[telegram]" in result.output
    assert "[hackernews]" in result.output
```

- [ ] **Step 2: Run the fetch tests to verify they fail**

```
.venv\Scripts\pytest.exe tests/test_cli.py -k "fetch" -v
```

Expected: all four fetch tests FAIL — `feedy.cli` has no `load_config` attribute to patch yet (`AttributeError`).

- [ ] **Step 3: Update `feedy/cli.py`**

Add the config import. Current top of `feedy/cli.py`:

```python
import click
from datetime import datetime

import feedy.storage as storage
from feedy.digest import build_digest
from feedy.summarizer import summarize
from feedy.sources.hackernews import HackerNewsSource
from feedy.sources.meta import MetaSource
from feedy.sources.telegram import TelegramSource
from feedy.sources.tiktok import TikTokSource
```

Add the config import after the `summarize` import so it reads:

```python
import click
from datetime import datetime

import feedy.storage as storage
from feedy.config import load_config
from feedy.digest import build_digest
from feedy.summarizer import summarize
from feedy.sources.hackernews import HackerNewsSource
from feedy.sources.meta import MetaSource
from feedy.sources.telegram import TelegramSource
from feedy.sources.tiktok import TikTokSource
```

Add a `_build_sources` helper directly after the `cli` group definition (before the `fetch` command):

```python
def _build_sources(names):
    registry = {
        "telegram": TelegramSource,
        "tiktok": TikTokSource,
        "meta": MetaSource,
        "hackernews": HackerNewsSource,
    }
    return [registry[name]() for name in names if name in registry]
```

Replace the current `fetch` body:

```python
@cli.command()
def fetch():
    """Fetch latest entries from all configured sources."""
    sources = [
        TelegramSource(),
        TikTokSource(),
        MetaSource(),
        HackerNewsSource(),
    ]
    total_saved = 0
```

with:

```python
@cli.command()
def fetch():
    """Fetch latest entries from all configured sources."""
    config = load_config()
    sources = _build_sources(config.sources)
    total_saved = 0
```

- [ ] **Step 4: Run the fetch tests to verify all pass**

```
.venv\Scripts\pytest.exe tests/test_cli.py -k "fetch" -v
```

Expected: all four fetch tests pass.

- [ ] **Step 5: Commit**

```
git add feedy/cli.py tests/test_cli.py
git commit -m "feat(cli): fetch runs only sources enabled in config"
```

---

### Task 5: `digest` uses config output format

**Files:**
- Modify: `feedy/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Update the build_digest-args test and add a format test**

In `tests/test_cli.py`, replace the existing `test_digest_calls_build_digest_with_summarized`:

```python
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
```

with:

```python
@patch("feedy.cli.load_config")
@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_calls_build_digest_with_summarized(mock_storage, mock_summarize, mock_build_digest, mock_load_config):
    mock_load_config.return_value = Config(output_format="markdown")
    entries = _make_digest_entries("hackernews", 1)
    summarized = [{**entries[0], "summary": "A great summary."}]
    mock_storage.get_entries.return_value = entries
    mock_summarize.return_value = summarized
    mock_build_digest.return_value = "## Hackernews\n• Title 0 — A great summary."
    runner = CliRunner()
    runner.invoke(cli, ["digest"])
    mock_build_digest.assert_called_once_with(summarized, "markdown")
```

Then append a new test to the end of `tests/test_cli.py`:

```python
@patch("feedy.cli.load_config")
@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_uses_config_output_format(mock_storage, mock_summarize, mock_build_digest, mock_load_config):
    mock_load_config.return_value = Config(output_format="plain")
    entries = _make_digest_entries("hackernews", 1)
    mock_storage.get_entries.return_value = entries
    mock_summarize.return_value = entries
    mock_build_digest.return_value = ""
    runner = CliRunner()
    runner.invoke(cli, ["digest"])
    mock_build_digest.assert_called_once_with(entries, "plain")
```

- [ ] **Step 2: Run the digest tests to verify the changed/new ones fail**

```
.venv\Scripts\pytest.exe tests/test_cli.py -k "digest" -v
```

Expected: `test_digest_calls_build_digest_with_summarized` and `test_digest_uses_config_output_format` FAIL — the current `digest` command calls `build_digest(summarized)` with one arg, not two.

- [ ] **Step 3: Update the `digest` command in `feedy/cli.py`**

Current `digest` command:

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

Replace with:

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

    config = load_config()
    summarized = summarize(entries)

    for original, updated in zip(entries, summarized):
        if updated["summary"] and updated["summary"] != original["summary"]:
            storage.update_summary(updated["url"], updated["summary"])

    click.echo(build_digest(summarized, config.output_format))
```

- [ ] **Step 4: Run the digest tests to verify all pass**

```
.venv\Scripts\pytest.exe tests/test_cli.py -k "digest" -v
```

Expected: all digest tests pass (8 existing + 1 new = 9).

- [ ] **Step 5: Run the full test suite to confirm no regressions**

```
.venv\Scripts\pytest.exe -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```
git add feedy/cli.py tests/test_cli.py
git commit -m "feat(cli): digest renders using config output_format"
```

---

### Task 6: Mark Day 16 complete

**Files:**
- Modify: `ROADMAP.md`

- [ ] **Step 1: Update roadmap**

In `ROADMAP.md`, change:

```
- [ ] Day 16 — Config file support: sources to track, API key, output format (YAML/TOML)
```

to:

```
- [x] Day 16 — Config file support: sources to track, API key, output format (YAML/TOML)
```

- [ ] **Step 2: Commit**

```
git add ROADMAP.md
git commit -m "chore: mark Day 16 complete"
```
