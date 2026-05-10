# Telegram-WP-LinkedIn

Automation pipeline to process Telegram updates and publish content to WordPress and LinkedIn.

## Quick start

1. Create a virtualenv and install dependencies.
2. Copy `.env.example` values into your local secret store.
3. Run a dry-run:

```bash
python -m app.main run-once --dry-run --db-path data/app.db
```

## Local gate enforcement

This repository enforces local quality/security gates on `git push` using a versioned pre-push hook.

Setup once per clone:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

The pre-push hook runs:

- `scripts/local-quality-gate.ps1`
- `scripts/local-security-scan.ps1`

## Controlled E2E

There is a controlled E2E test with real provider credentials:

```bash
python -m pytest tests/test_e2e_controlled.py -m e2e -q
```

Detailed setup and pass/fail criteria are documented in `docs/e2e-controlado.md`.
