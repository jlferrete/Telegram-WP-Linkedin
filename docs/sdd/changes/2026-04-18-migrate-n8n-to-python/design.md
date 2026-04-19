# Design - 2026-04-18-migrate-n8n-to-python

## Arquitectura

Patron hexagonal ligero:

- `core`: reglas de negocio, modelos y casos de uso
- `adapters`: integracion con APIs externas
- `repositories`: persistencia SQLite
- `infra`: config, logging, retry, locking

## Mapeo requirement -> componentes

- R1: `repositories/state_repo.py`, `adapters/telegram.py`, `core/pipeline.py`
- R2: `repositories/updates_repo.py`, `repositories/publications_repo.py`, `core/idempotency.py`
- R3: `adapters/openai.py`, `adapters/wordpress.py`, `adapters/pexels.py`, `adapters/linkedin.py`
- R4: `repositories/runs_repo.py`, `repositories/events_repo.py`, `infra/logging.py`
- R5: `infra/config.py`, `infra/logging.py`
- R6: `app/main.py` (comando reprocess), `core/pipeline.py`

## Estrategia de consistencia

- lock de corrida al inicio
- transaccion corta por update
- commit de offset solo al final
- estado parcial en `publications` para recuperacion/reproceso

## Estrategia de errores

- retries para 429/5xx con backoff exponencial y jitter
- no retry para 4xx funcionales
- persistencia de errores en `events` y `publications.last_error`

## Seguridad

- secretos via env vars
- validacion fail-fast de secretos requeridos al arranque
- redaccion de logs para evitar leakage

## Operacion

- comando principal: `run-once`
- comando soporte: `reprocess --update-id <id>`
- ejecucion por cron con contenedor Docker
