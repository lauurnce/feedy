# AnthropicSource Implementation Plan — Day 22

**Spec:** `docs/superpowers/specs/2026-05-30-anthropic-source-design.md`

## Steps

1. **Failing tests** — add `tests/test_anthropic.py` (mirror `test_openai.py`).
   Run, confirm fail (module missing).
2. **Implement** — add `feedy/sources/anthropic.py` with `AnthropicSource`
   and `_parse_date(el)` helper. Card `a[href*="/news/"]`, title `h3`, date `time`.
3. **Register** — `"anthropic": AnthropicSource` in `_build_sources`; add
   `"anthropic"` to `DEFAULT_SOURCES`; update `test_config.py` default assertions.
4. **Verify** — run full suite, confirm green.
5. **Roadmap** — mark Day 22 done.

## Commit sequence

- `test(anthropic): add failing tests for AnthropicSource`
- `feat(anthropic): scrape anthropic.com/news blog posts`
- `feat(cli): register anthropic source`
- `chore: mark Day 22 complete`
