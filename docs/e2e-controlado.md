# E2E Controlado

Este proyecto ahora tiene una prueba E2E controlada que ejecuta `pipeline run-once` con credenciales reales y valida resultados en base de datos local.

## Camino rapido

1. Exportar variables requeridas en el entorno.
2. Preparar un mensaje nuevo en Telegram con URL valida para procesar.
3. Ejecutar `python -m pytest tests/test_e2e_controlled.py -m e2e -q`.
4. Confirmar que la prueba pasa y revisar los criterios de aceptacion.

## Variables requeridas

- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY`
- `PEXELS_API_KEY`
- `WP_BASE_URL`
- `WP_USER`
- `WP_APP_PASSWORD`
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_PERSON_URN`
- `E2E_TELEGRAM_TRIGGER_OFFSET`

`E2E_TELEGRAM_TRIGGER_OFFSET` debe ser el `update_id` minimo que esperas procesar en esa corrida.

## Criterios de pase

La prueba pasa solo si se cumple todo esto:

- El comando termina con exit code `0`.
- Se registra una corrida en `runs` con estado `success` o `partial`.
- El `state.telegram_offset` queda mayor o igual al trigger definido.
- Existe al menos un `update` con `update_id >= E2E_TELEGRAM_TRIGGER_OFFSET`.
- Existe al menos una fila en `publications` asociada a esos updates.

## Criterios de fallo

La prueba falla si se cumple cualquiera de estos casos:

- Exit code distinto de `0`.
- No hay corrida registrada.
- Offset no avanza respecto del trigger.
- No hay updates/publications para el rango esperado.

## Notas operativas

- Si faltan variables de entorno, el test se marca `skipped` para evitar falsos negativos.
- La prueba usa una base SQLite temporal propia y no pisa `data/app.db`.
- El estado `partial` se considera valido para E2E porque el pipeline trata fallos parciales como comportamiento esperado.
