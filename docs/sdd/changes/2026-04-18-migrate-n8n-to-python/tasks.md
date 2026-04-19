# Tasks - 2026-04-18-migrate-n8n-to-python

## T1 - Bootstrap del proyecto Python

- crear estructura `app/`, `tests/`, `migrations/`
- configurar `pyproject.toml` con tooling de calidad
- agregar `.env.example` sin secretos

Trace: R1, R4, R5

## T2 - Infraestructura SQLite y repositorios

- implementar conexion SQLite + PRAGMA
- crear migracion inicial con DDL v1
- implementar repositorios `state/runs/updates/publications/events`

Trace: R1, R2, R4, R6

## T3 - CLI y pipeline base

- implementar `run-once`
- implementar lock de corrida
- polling Telegram + parse + update de offset

Trace: R1, R2, R4

## T4 - Integracion de negocio y publicaciones

- extraer URL/titulo
- integrar OpenAI (salida estructurada)
- publicar en WordPress
- publicar en LinkedIn con imagen Pexels
- notificar por Telegram

Trace: R3, R4

## T5 - Reintentos e idempotencia avanzada

- retries por proveedor
- control de duplicados por `update_id`
- estados `partial/failed/success`

Trace: R2, R3, R6

## T6 - Seguridad y estandar de secretos

- cargar env vars con validacion fail-fast
- sanitizar logs
- alinear docs con `secrets-operating-standard`

Trace: R5

## T7 - Dockerizacion

- crear Dockerfile multi-stage
- usuario no-root
- smoke test `run-once --dry-run`

Trace: R1, R5

## T8 - CI/CD en GitHub Actions

- quality gate (ruff, mypy, pytest)
- security gate (gitleaks, trivy, pip-audit)
- build + push GHCR por tags

Trace: R4, R5

## T9 - Verificacion SDD

- mapear evidencia de pruebas por requisito
- documentar cumplimiento final

Trace: R1, R2, R3, R4, R5, R6
