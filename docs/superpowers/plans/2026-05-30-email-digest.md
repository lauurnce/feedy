# Email Digest Output Plan — Day 24

**Spec:** `docs/superpowers/specs/2026-05-30-email-digest-design.md`

## Steps

1. **Failing tests** — `tests/test_notify.py` (4 email tests), `--email` tests
   in `tests/test_cli.py`, `EmailConfig` tests in `tests/test_config.py`.
   Run, confirm fail.
2. **Config** — add `EmailConfig` dataclass + `Config.email` + loader.
3. **Implement** — `send_email` in `feedy/notify.py`.
4. **CLI** — import `send_email` + `dataclasses.replace`; add `--email` flag.
5. **Verify** — full suite green.
6. **Roadmap** — mark Day 24 done.

## Commit sequence

- `test(notify): add failing tests for email digest output`
- `feat(config): add EmailConfig and [email] table support`
- `feat(notify): add send_email SMTP sender`
- `feat(cli): digest --email sends digest over SMTP`
- `chore: mark Day 24 complete`
