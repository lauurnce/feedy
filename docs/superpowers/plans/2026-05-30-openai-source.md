# OpenAISource Implementation Plan — Day 21

**Spec:** `docs/superpowers/specs/2026-05-30-openai-source-design.md`

## Steps

1. **Failing tests** — add `tests/test_openai.py` with fixture HTML and the
   13 tests listed in the spec. Run, confirm they fail (module missing).
2. **Implement** — add `feedy/sources/openai.py` with `OpenAISource`
   (`name`, `fetch`, `parse`, `to_dict`) and `_parse_date(el)` helper.
   - Card selector `a[href*="/index/"]`, title `h3`, date `time`.
   - `_parse_date`: use `time["datetime"]` (first 10 chars) if present,
     else parse text via `strptime("%b %d, %Y")`, `""` on failure.
3. **Register** — add `"openai": OpenAISource` to `_build_sources` in
   `feedy/cli.py`; add `"openai"` to `DEFAULT_SOURCES` in `feedy/config.py`.
4. **Verify** — run full test suite, confirm green.
5. **Roadmap** — mark Day 21 done.

## Commit sequence

- `test(openai): add failing tests for OpenAISource`
- `feat(openai): scrape openai.com/news blog posts`
- `feat(cli): register openai source`
- `chore: mark Day 21 complete`
