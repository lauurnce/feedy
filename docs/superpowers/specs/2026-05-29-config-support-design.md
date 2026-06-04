# Design: Config File Support (Day 16)

**Date:** 2026-05-29
**Feature:** Day 16 — Config file support: sources to track, API key, output format (TOML)

---

## Decision Summary

- **Format:** TOML, read via stdlib `tomllib` (Python 3.11+) — zero new dependencies
- **Location:** `~/.feedy/config.toml` (sits beside existing `~/.feedy/feedy.db`)
- **Scope:** sources to track, Anthropic API key fallback, digest output format

## Config Schema

```toml
sources = ["telegram", "hackernews"]
output_format = "plain"

[anthropic]
api_key = "sk-ant-..."
```

All keys optional. Missing file or missing keys → defaults.

| Key | Default | Effect |
|-----|---------|--------|
| `sources` | `["telegram", "tiktok", "meta", "hackernews"]` | Which sources `fetch` runs |
| `output_format` | `"markdown"` | Digest rendering style: `markdown` or `plain` |
| `anthropic.api_key` | `None` | Used by `complete()` only when `ANTHROPIC_API_KEY` env unset |

## New Module: `feedy/config.py`

```python
@dataclass
class Config:
    sources: list[str]          # default: all four
    output_format: str          # default: "markdown"
    api_key: str | None         # default: None

def load_config(path: Path | None = None) -> Config:
    ...  # reads ~/.feedy/config.toml; returns Config() defaults if file absent
```

## Wiring

### `fetch` (cli.py)

Replace the hardcoded source list with a name→class registry built at call time, filtered by `config.sources`:

```python
def _build_sources(names):
    registry = {"telegram": TelegramSource, "tiktok": TikTokSource,
                "meta": MetaSource, "hackernews": HackerNewsSource}
    return [registry[n]() for n in names if n in registry]
```

Registry is built inside the function (not module-level) so test patches on the source classes resolve at call time.

### `complete` (ai.py)

```python
key = os.environ.get("ANTHROPIC_API_KEY") or (load_config().api_key or "")
if not key:
    return None
```

Env var keeps precedence; config is fallback only. `load_config()` is only reached when env is empty/unset (short-circuit).

### `build_digest` (digest.py)

Add `output_format` param (default `"markdown"`, backward compatible):

| Format | Header | Bullet |
|--------|--------|--------|
| `markdown` | `## Telegram` | `• ` |
| `plain` | `TELEGRAM` | `- ` |

### `digest` (cli.py)

Loads config after the empty-entries check, passes format to digest:

```python
config = load_config()
...
click.echo(build_digest(summarized, config.output_format))
```

## Error Handling

| Case | Behaviour |
|------|-----------|
| Config file missing | `load_config()` returns `Config()` defaults |
| Key missing in file | That field uses its default |
| Source name in config not in registry | Silently skipped (no crash) |
| `output_format` not "plain" | Treated as markdown (default branch) |

## Out of Scope

- Writing/initializing a config file (`feedy init`) — not required
- Validating unknown keys / strict schema errors
- Per-source config (URLs, limits)
- Env var for config path override

## Testing

| File | New/changed tests |
|------|-------------------|
| `tests/test_config.py` (new) | defaults, reads sources/format/api_key, partial file, missing file |
| `tests/test_ai.py` | config fallback, env precedence; update missing/empty-key tests to patch `load_config` |
| `tests/test_digest.py` | plain format (no `##`, `- ` bullet), markdown default |
| `tests/test_cli.py` | fetch filters by config sources; update 3 existing fetch tests + 1 digest test to patch `load_config`; digest passes output_format |
