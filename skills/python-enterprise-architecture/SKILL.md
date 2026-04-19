---
name: python-enterprise-architecture
description: >
  Applies maintainable Python architecture with ports/adapters, testable domain, and resilience to external API drift.
  Trigger: when implementing Python features, designing module boundaries, or integrating external providers.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

- When adding new business capabilities to the pipeline
- When integrating/changing provider APIs (Telegram, OpenAI, WP, LinkedIn, Pexels)
- When reviewing maintainability, scalability, and testability

## Critical Patterns

- Keep domain pure: business logic in `core/`, no direct HTTP/DB there.
- Use ports (`Protocol`) in `core/ports.py`; adapters implement contracts.
- Repositories own persistence concerns; pipeline orchestrates use cases.
- Validate external payload shape aggressively at adapter boundary.
- Prefer explicit failure states (`success`, `partial`, `failed`) over hidden exceptions.
- Add adapter contract tests for every API integration change.
- Delivery rule: implement in vertical slices and commit per slice (core, adapters, infra, tests, docs), never all at once.

## Module Boundaries

| Layer | Responsibility | Must Not Do |
| --- | --- | --- |
| `core` | Use cases, orchestration, domain rules | Call HTTP directly |
| `adapters` | Translate external API contracts | Encode business policy |
| `repositories` | SQL persistence and query semantics | Generate external content |
| `infra` | Config, db setup, logging, retries | Own business decisions |
| `app/main.py` | Composition root and CLI entrypoint | Hold domain logic |

## API Drift Playbook

1. Add/adjust fixture for new provider payload.
2. Update adapter parser and validation.
3. Keep backward compatibility when possible.
4. Add tests for both old/new shape when feasible.
5. Document breaking changes in docs or ADR.

## Commands

```bash
.venv\\Scripts\\python -m pytest
.venv\\Scripts\\python -m mypy app
.venv\\Scripts\\python -m ruff check app tests
```

## Resources

- **Architecture**: `docs/01-architecture/python-architecture.md`
- **SDD design**: `docs/sdd/changes/2026-04-18-migrate-n8n-to-python/design.md`
- **Quality**: `docs/05-quality/testing-strategy.md`
