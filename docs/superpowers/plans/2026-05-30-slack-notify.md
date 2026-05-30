# Slack Webhook Output Plan — Day 23

**Spec:** `docs/superpowers/specs/2026-05-30-slack-notify-design.md`

## Steps

1. **Failing tests** — `tests/test_notify.py` (3 tests), plus new `--slack`
   tests in `tests/test_cli.py` and `slack_webhook_url` tests in
   `tests/test_config.py`. Run, confirm fail.
2. **Implement notify** — `feedy/notify.py` with `send_to_slack`.
3. **Config** — add `slack_webhook_url` field + loader.
4. **CLI** — import `send_to_slack` + `os`; add `--slack` flag and send logic.
5. **Verify** — full suite green.
6. **Roadmap** — mark Day 23 done.

## Commit sequence

- `test(notify): add failing tests for Slack webhook output`
- `feat(notify): add send_to_slack webhook poster`
- `feat(config): add slack_webhook_url support`
- `feat(cli): digest --slack sends digest to Slack webhook`
- `chore: mark Day 23 complete`
