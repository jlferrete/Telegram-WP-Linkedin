# Handoff - Next Session

## Estado actual

- SDD formal completo para el cambio `2026-04-18-migrate-n8n-to-python`.
- Documentacion base enterprise completada (arquitectura, datos, operaciones, seguridad, ADRs).
- Sin codigo de aplicacion implementado aun (por decision metodologica SDD).

## Punto exacto para retomar

Iniciar implementacion por `tasks.md` en orden:

1. `T1 - Bootstrap del proyecto Python`
2. `T2 - Infraestructura SQLite y repositorios`
3. `T3 - CLI y pipeline base`

## Definicion de listo para arrancar (pre-implementacion)

- revisar y confirmar `spec.md` (R1..R6)
- revisar `design.md` (mapeo requirement -> componentes)
- validar estandar de secretos (`docs/06-security/secrets-operating-standard.md`)

## Checklist de la primera sesion de implementacion

- crear estructura `app/`, `tests/`, `migrations/`
- crear `pyproject.toml` con tooling (ruff, mypy, pytest)
- crear `.env.example` sin secretos
- crear migracion SQLite v1 desde `docs/02-data/sqlite-schema.md`
- implementar comando `run-once --dry-run`

## Riesgos a vigilar desde el inicio

- no romper idempotencia por `update_id`
- no loguear secretos
- evitar overlap de corridas sin lock
- no avanzar `telegram_offset` antes de tiempo
