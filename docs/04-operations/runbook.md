# Runbook Operativo

## Objetivo

Operar el servicio de forma estable, diagnosticar incidentes y ejecutar reprocesos sin comprometer idempotencia.

## Ejecucion programada

## Linux cron (recomendado)

```bash
*/15 * * * * /usr/bin/docker run --rm \
  --env-file /opt/telegram-wp-linkedin/.env \
  -v /opt/telegram-wp-linkedin/data:/data \
  ghcr.io/<org>/telegram-wp-linkedin:latest \
  python -m app.main run-once --db-path /data/app.db
```

Notas:
- Ajustar frecuencia segun volumen de mensajes.
- Si se mantiene polling cada hora, usar `0 * * * *`.

## Windows Task Scheduler (alternativa)

- Trigger: cada 15 minutos (o cada hora).
- Action: ejecutar `docker run --rm ... python -m app.main run-once`.
- Configurar reintentos de tarea por fallo.

## Checklist pre-produccion

- `.env` cargado con todas las credenciales.
- base SQLite inicializada y con `telegram_offset`.
- lock de proceso validado.
- logs JSON redirigidos a archivo/collector.
- gate local en verde (`local-quality-gate.ps1` + `local-security-scan.ps1`, ambos obligatorios).
- cumplimiento de `docs/06-security/secrets-operating-standard.md`.

## Politica de uso minimo de GitHub Actions (cost control)

Objetivo: minimizar minutos cloud manteniendo gobernanza enterprise.

Reglas operativas:

- `PR Gates` desactivado por defecto para evitar costo recurrente por cada PR.
- validacion obligatoria ocurre localmente antes de abrir/mergear PR:
  - `./scripts/local-quality-gate.ps1`
  - `./scripts/local-security-scan.ps1`
- `Release Image` se usa solo para releases reales por tag semantico (`v*.*.*`).
- evitar tags de prueba frecuentes; agrupar cambios y releasear en lotes razonables.

Cuando SI correr Actions:

- release candidate que realmente podria promoverse a produccion
- cambio de Dockerfile/base image o cadena de build de contenedor
- cambio de permisos/policies en environments o publish a GHCR

Cuando NO correr Actions:

- PRs de documentacion
- refactors internos sin impacto en imagen/release
- pruebas exploratorias que pueden validarse completamente en local

Ejecucion recomendada del gate local:

```powershell
./scripts/local-quality-gate.ps1
./scripts/local-security-scan.ps1
```

## Troubleshooting

### 1) Cron ejecuta pero no hay publicaciones

Verificar:
- tabla `runs` (status de corridas)
- tabla `events` (etapa donde falla)
- `state.telegram_offset` (si avanza o no)

SQL util:

```sql
SELECT run_id, started_at, finished_at, status, error
FROM runs
ORDER BY started_at DESC
LIMIT 20;
```

### 2) Duplicados en destino

Verificar:
- si hubo concurrencia sin lock
- si se ignoro control por `update_id`
- si proveedor externo no respeta idempotency-key

Accion:
- pausar cron
- inspeccionar `updates` y `publications`
- corregir bug y reprocesar solo failed/partial

### 3) Error SQLite busy/locked

Verificar:
- overlap de tareas cron
- `busy_timeout` configurado
- transacciones demasiado largas

Accion:
- aumentar intervalo de cron
- acortar secciones transaccionales
- asegurar lock unico por corrida

### 4) Fallo OAuth / credenciales caducadas

Accion:
- rotar credencial afectada
- validar variable de entorno
- ejecutar `run-once --dry-run` para verificar arranque

## Reproceso manual (seguro)

### Candidatos a reproceso

```sql
SELECT u.update_id, p.status, p.last_error
FROM updates u
JOIN publications p ON p.update_id = u.update_id
WHERE p.status IN ('failed','partial')
ORDER BY u.update_id ASC;
```

### Procedimiento

1. pausar cron
2. elegir `update_id` a reprocesar
3. ejecutar comando de reproceso por id
4. validar `publications.status='success'`
5. reanudar cron

Comando esperado (objetivo del CLI):

```bash
python -m app.main reprocess --update-id 123456789 --db-path /data/app.db
```

## SLOs operativos sugeridos

- disponibilidad de job >= 99.5%
- duplicados por semana = 0
- MTTR < 30 minutos
- corridas con trazabilidad (`runs` + `events`) = 100%

## Escalamiento de incidentes

- Sev1: duplicacion masiva/publicaciones incorrectas en produccion
- Sev2: falla sostenida de un proveedor externo
- Sev3: errores intermitentes con recovery automatico

En Sev1/Sev2:
- pausar cron inmediatamente
- preservar evidencia (`runs/events` y logs)
- aplicar rollback a imagen anterior si corresponde
