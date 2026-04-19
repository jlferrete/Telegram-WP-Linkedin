# Analisis del Workflow n8n Actual

## Objetivo funcional detectado

Automatizar, cada hora, el procesamiento de mensajes de Telegram para:

1. leer nuevos mensajes (`getUpdates`) usando `offset`
2. extraer URL y titulo desde el texto
3. generar contenido con OpenAI
4. publicar en WordPress
5. seleccionar una imagen desde Pexels
6. subir imagen y publicar en LinkedIn (API REST)
7. notificar por Telegram
8. persistir el nuevo `offset`

## Flujo principal observado (AS-IS)

1. `Cada hora` dispara la ejecucion.
2. `Get row(s)` obtiene estado desde Data Table (`bot_state`).
3. `Parsear offset` calcula offset numerico.
4. `Obtener mensajes` llama a Telegram `getUpdates`.
5. `¿Hay mensajes?` filtra cuando hay resultados.
6. `Separar mensajes` itera por cada update.
7. `Extraer datos` obtiene campos base (`update_id`, `text`, `chat_id`).
8. `Information Extractor` intenta extraer `Title` y `Url`.
9. `OpenAI` genera payload editorial estructurado.
10. `Edit Fields` normaliza campos para downstream.
11. Paralelo:
   - `Post in Wordpress`
   - `Images List from Pexels` -> seleccion aleatoria -> descarga binario
   - `Init Upload` (LinkedIn images)
12. `Merge` combina init upload + binario.
13. `Upload Image` sube binario a LinkedIn.
14. `HTTP Request` crea post de LinkedIn con articulo + thumbnail.
15. `Telegram` envia notificacion de resultado.
16. `Agregar IDs` -> `Calcular offset` -> `Update row(s)` persiste nuevo offset.

## Hallazgos criticos (riesgo alto)

- **Secretos hardcodeados en JSON**:
  - token de bot de Telegram en URL
  - API key de Pexels en headers
  - referencias a credenciales de OpenAI/LinkedIn/WordPress
- **Acoplamiento fuerte de pasos**: un fallo en proveedor externo puede dejar corrida inconsistente.
- **Idempotencia parcial**: solo se persiste `offset`; no hay ledger de publicaciones por `update_id`.
- **Sin control de concurrencia**: si hay overlap de ejecuciones por cron, puede haber duplicados.
- **Observabilidad limitada**: no hay trazabilidad persistente de cada intento por canal.
- **Orden de commit de estado sensible**: si se actualiza offset pero falla publicacion, hay riesgo de perdida o duplicacion segun punto de fallo.

## Riesgos funcionales detectados

- Duplicado de publicaciones en WordPress/LinkedIn ante retries no idempotentes.
- Perdida de mensajes si offset avanza antes de completar operaciones criticas.
- Fallos no recuperables por parseo libre de IA (sin validacion fuerte de schema).
- Variabilidad por seleccion aleatoria de imagen sin estrategia de fallback.

## Oportunidades al migrar a codigo

- Control transaccional de estado en SQLite.
- Contratos tipados y validaciones deterministas.
- Retries por proveedor con politica diferenciada.
- Runbooks y metricas operativas reales.
- Testing automatizable sin dependencia del editor visual de n8n.
