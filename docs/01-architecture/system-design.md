# System Design

## Objetivo

Definir la arquitectura TO-BE del servicio que reemplaza n8n, con foco en estabilidad, idempotencia y trazabilidad por `update_id`.

## Alcance funcional

- Polling de Telegram con `offset` persistente.
- Procesamiento de mensaje por `update_id`.
- Generacion de contenido (OpenAI) y publicacion en WordPress.
- Seleccion/subida de imagen y publicacion en LinkedIn.
- Notificacion a Telegram.
- Auditoria completa en SQLite.

## Diagrama logico

```mermaid
flowchart LR
    Cron[Scheduler: cron / task scheduler] --> CLI[Python CLI run-once]
    CLI --> Lock[Lock de ejecucion]
    CLI --> DB[(SQLite)]

    CLI --> TG[Telegram API]
    CLI --> OAI[OpenAI API]
    CLI --> WP[WordPress API]
    CLI --> PX[Pexels API]
    CLI --> LI[LinkedIn API]

    DB --> S1[state]
    DB --> S2[runs]
    DB --> S3[updates]
    DB --> S4[publications]
    DB --> S5[events]
```

## Componentes

- `app/main.py`: entrypoint CLI, argumentos y lifecycle del proceso.
- `core/pipeline.py`: orquestacion por etapas y reglas de negocio.
- `core/models.py`: contratos tipados de entrada/salida.
- `adapters/*`: clientes de proveedores externos.
- `repositories/*`: acceso a SQLite y transacciones.
- `infra/config.py`: carga y validacion de variables de entorno.
- `infra/logging.py`: logs JSON con `run_id` y `update_id`.
- `infra/retry.py`: politicas de retry/backoff por proveedor.

## Secuencia por update_id

```mermaid
sequenceDiagram
    participant Job as Cron Job
    participant App as Python Script
    participant DB as SQLite
    participant TG as Telegram
    participant AI as OpenAI
    participant WP as WordPress
    participant PX as Pexels
    participant LI as LinkedIn

    Job->>App: run-once
    App->>DB: acquire lock + create run(started)
    App->>DB: read state.telegram_offset
    App->>TG: getUpdates(offset)
    TG-->>App: updates[]

    loop for each update_id asc
      App->>DB: insert updates(update_id) if not exists
      alt already exists
        App->>DB: events(stage=dedupe,status=skipped)
      else new update
        App->>App: extract url/title
        App->>AI: generate content (JSON schema)
        AI-->>App: structured content
        App->>WP: create post
        WP-->>App: wp_post_id
        App->>PX: search image
        PX-->>App: image bytes/url
        App->>LI: upload image + create post
        LI-->>App: linkedin_post_id
        App->>TG: notify result
        App->>DB: publications + events(success)
      end
    end

    App->>DB: update telegram_offset = max(update_id)+1
    App->>DB: close run(success/error)
```

## Reglas de consistencia

- El `offset` solo avanza al final de la corrida y en transaccion.
- `update_id` es clave de idempotencia para evitar duplicados.
- Cada paso escribe `events` para auditoria y reproceso.
- Fallos transitorios: retry con backoff; permanentes: marcar y continuar.

## NFR (Non-Functional Requirements)

- **Reliability**: cero duplicados por `update_id` en destinos finales.
- **Observability**: 100% corridas con `run_id` y eventos de etapa.
- **Security**: secretos por env, sin hardcode en repositorio.
- **Operability**: runbook con troubleshooting y reproceso manual.
- **Maintainability**: coverage de pruebas unitarias e integracion DB.
