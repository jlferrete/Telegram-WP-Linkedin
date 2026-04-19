# Plan de Migracion Enterprise Grade (n8n -> Script)

## 1) Principios de migracion

- **Seguridad primero**: eliminar secretos del workflow y moverlos a variables de entorno.
- **Idempotencia por defecto**: ninguna accion externa se ejecuta dos veces para el mismo `update_id` sin control.
- **Atomicidad de estado**: persistir progreso en SQLite con modelo de corrida + eventos.
- **Observabilidad operativa**: logs estructurados y trazabilidad por `run_id` y `update_id`.
- **Rollback simple**: poder desactivar cron y volver a n8n sin perdida de datos.

## 2) Arquitectura objetivo (TO-BE)

- Stack base: Python 3.12+
- Proceso CLI ejecutable: `python -m app.main run-once`
- Scheduler externo:
  - Linux: cron
  - Windows: Task Scheduler (si aplica)
- SQLite como store local con WAL.
- Contenedor Docker para ejecucion consistente entre entornos.
- Modulos desacoplados:
  - `adapters/telegram.py`
  - `adapters/openai.py`
  - `adapters/wordpress.py`
  - `adapters/linkedin.py`
  - `adapters/pexels.py`
  - `core/pipeline.py`
  - `core/idempotency.py`
  - `infra/db.py`, `infra/logging.py`, `infra/config.py`

## 3) Modelo de datos SQLite (minimo recomendado)

- `state(key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL)`
  - ejemplo: `telegram_offset`
- `runs(run_id TEXT PRIMARY KEY, started_at TEXT, finished_at TEXT, status TEXT, error TEXT)`
- `updates(update_id INTEGER PRIMARY KEY, chat_id INTEGER, text TEXT, received_at TEXT, run_id TEXT)`
- `publications(update_id INTEGER PRIMARY KEY, wp_post_id TEXT, linkedin_post_id TEXT, status TEXT, last_error TEXT, updated_at TEXT)`
- `events(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, update_id INTEGER, stage TEXT, status TEXT, detail TEXT, created_at TEXT)`

Notas:
- `update_id` como clave natural de idempotencia.
- transacciones cortas por update para evitar bloqueos largos.

## 4) Estrategia de ejecucion

1. `acquire_lock` (lock de proceso por DB o file lock).
2. abrir `run_id` y registrar `started`.
3. leer `telegram_offset`.
4. pedir updates a Telegram con timeout corto.
5. si no hay updates: cerrar `run` en success y salir.
6. para cada update (orden ascendente):
   - validar payload minimo (`update_id`, `text`, `chat_id`).
   - upsert en `updates` (si existe, marcar como duplicado y seguir).
   - extraer URL/titulo (heuristica + fallback IA opcional).
   - generar contenido (OpenAI con schema JSON estricto).
   - publicar WordPress (idempotency-key propia).
   - resolver imagen (Pexels + fallback).
   - publicar LinkedIn con imagen.
   - notificar por Telegram resultado.
   - persistir resultado en `publications` + `events`.
7. calcular `new_offset = max(update_id)+1` solo sobre updates procesados/registrados.
8. actualizar `state.telegram_offset` en transaccion.
9. cerrar `run` como success/error.
10. liberar lock.

## 5) Politica de retries y errores

- Retries con backoff exponencial y jitter para HTTP 429/5xx.
- Sin retry para errores 4xx funcionales (payload invalido, auth invalida salvo expiracion token).
- Timeouts por llamada (conexion/lectura) para evitar cuelgues.
- Dead-letter logico en `events` para reprocesar manualmente por `update_id`.

## 6) Seguridad

- Variables de entorno obligatorias:
  - `TELEGRAM_BOT_TOKEN`
  - `OPENAI_API_KEY`
  - `PEXELS_API_KEY`
  - `WP_BASE_URL`, `WP_USER`, `WP_APP_PASSWORD`
  - `LINKEDIN_ACCESS_TOKEN` (o flujo OAuth refrescable)
- Nunca loguear secretos ni payload completo sensible.
- Rotacion de claves y validacion de presencia al iniciar.

## 7) Plan por fases

### Fase 0 - Preparacion (1 dia)
- crear esqueleto del proyecto
- definir `.env.example`
- crear schema SQLite y migracion inicial

### Fase 1 - Paridad base Telegram + estado (1-2 dias)
- leer offset desde SQLite
- obtener updates y persistir offset nuevo
- logs estructurados + tabla `runs/events`

### Fase 2 - Paridad de negocio (2-4 dias)
- extraccion URL/titulo
- generacion OpenAI con schema validado
- publicacion WordPress

### Fase 3 - Paridad social media completa (2-4 dias)
- Pexels + seleccion de imagen + descarga
- init upload + upload + post LinkedIn
- notificacion Telegram final

### Fase 4 - Hardening enterprise (2 dias)
- retries finos + circuit breaker simple
- idempotencia fuerte en tablas de publicaciones
- runbook de incidentes + scripts de reproceso

### Fase 5 - Cutover (1-2 dias)
- shadow run (solo lectura/validacion)
- ejecucion paralela controlada
- switch definitivo y apagado de n8n

## 8) Criterios de aceptacion

- 0 duplicados para mismo `update_id` en WordPress/LinkedIn.
- 100% de corridas con `run_id` y eventos trazables.
- recuperacion automatica ante fallos transitorios.
- recuperacion manual documentada para fallos permanentes.
- sin secretos en repo ni en archivos JSON.

## 10) Contenerizacion y CI/CD (GitHub)

- Imagen Docker minimal basada en `python:3.12-slim`.
- Multi-stage build para reducir superficie y tamano final.
- `HEALTHCHECK` y usuario no-root en runtime.
- Pipeline GitHub Actions:
  - `lint-test`: ruff + mypy + pytest
  - `security`: pip-audit + trivy (filesystem/image)
  - `build`: build de imagen + smoke test
  - `release`: tag semantico y push a GitHub Container Registry
  - `deploy`: ambiente `staging` -> `production` con approvals
- Estrategia de ramas recomendada: trunk-based con protecciones en `main`.
- Gates minimos: tests passing, coverage threshold, escaneo sin criticos.

## 9) Rollback

- desactivar cron del script.
- reactivar workflow n8n con ultimo offset consistente.
- conservar SQLite para auditoria del incidente.
