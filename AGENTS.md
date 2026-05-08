# AGENTS.md

## What matters here

- Python 3.12 project with strict typing/linting gates (`ruff`, `mypy --strict`, `pytest`, `pip-audit`, `gitleaks`).
- Architecture is hexagonal-ish: `app/core` (domain/use cases), `app/adapters` (external APIs), `app/repositories` (SQLite persistence), `app/infra` (config/db/retry wiring).
- Main CLI entrypoint is `pipeline` (`app.main:main`) with `run-once` and `reprocess` (currently stubbed, prints not implemented).

## Fast local workflow

- Install: `python -m pip install -e .[dev]`
- Run once dry-run: `python -m app.main run-once --dry-run --db-path data/app.db`
- Focused test: `python -m pytest tests/test_pipeline.py -q`
- Full quality check: `python -m ruff check app tests && python -m mypy app tests && python -m pytest -q`
- CI security check includes: `python -m pip_audit --ignore-vuln CVE-2026-3219` and `gitleaks git --redact --no-banner`

## Git hooks and gates

- Repo uses versioned hooks via `core.hooksPath=.githooks`; pre-push runs both `scripts/local-quality-gate.ps1` and `scripts/local-security-scan.ps1`.
- Local PowerShell gates use `.venv\Scripts\python`; if you do not use `.venv`, either adapt commands locally or expect hook failures.
- `scripts/local-security-scan.ps1` also requires `trivy` in addition to `gitleaks`.

## Pipeline invariants (do not break)

- Keep core boundaries: `app/core` must depend on ports/contracts, not concrete adapters.
- Dedupe happens before external side effects (`updates_repo.exists(update_id)` short-circuits processing).
- Dry-run must not call external providers and must not advance `state.telegram_offset`.
- Non-dry-run advances offset to `max(update_id) + 1` only after processing batch.
- Partial failure is first-class: WordPress success + later LinkedIn failure persists publication `status="partial"`.
- Retries are bounded and retryable-only (see `app/infra/retry.py` and usage in `app/core/pipeline.py`).

## Data and migrations

- DB is SQLite; startup calls `init_database()` which executes every `migrations/*.sql` file in sorted order on every run.
- Migration files must be idempotent (`IF NOT EXISTS`, safe re-run semantics) because they are re-applied at startup.
- Core tables and status enums are defined in `migrations/0001_init.sql`; repository changes must stay compatible.

## Testing conventions

- Unit tests use in-process doubles and `httpx.MockTransport`; keep tests deterministic and offline by default.
- For behavior changes in pipeline/adapters/repositories, update or add targeted tests in `tests/`.

## CI/release facts

- PR gates workflow (`.github/workflows/pr-gates.yml`) currently runs on `workflow_dispatch`.
- Release image workflow triggers only on tags matching `v*.*.*` and pushes to GHCR.

## Change/review expectations

- Use conventional commits: `feat|fix|refactor|test|docs|chore`.
- Never commit secrets or raw sensitive payloads; redact tokens/credentials in logs and errors.
- If asked to review staged changes, use this exact output format:
  1. `VERDICT: PASS | FAIL`
  2. `BLOCKERS:`
  3. `WARNINGS:`
  4. `PATCH SUGGESTIONS:`
  5. `RISK LEVEL: low | medium | high`
