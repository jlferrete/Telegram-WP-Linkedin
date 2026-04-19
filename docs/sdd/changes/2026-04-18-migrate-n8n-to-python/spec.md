# Specification - 2026-04-18-migrate-n8n-to-python

## Requirement R1 - Polling y persistencia de offset

El sistema MUST leer `telegram_offset`, consultar `getUpdates` y actualizar offset al finalizar corrida.

### Scenario R1.1 - Corrida sin mensajes

Given `telegram_offset=100`
When se ejecuta `run-once` y Telegram devuelve `result=[]`
Then la corrida termina en `success`
And `telegram_offset` no retrocede
And se registra evento de etapa `polling`.

### Scenario R1.2 - Corrida con mensajes

Given `telegram_offset=100`
When Telegram devuelve updates `[101,102]`
Then el sistema procesa en orden ascendente
And actualiza offset a `103` al final.

## Requirement R2 - Idempotencia por update_id

El sistema MUST garantizar que un mismo `update_id` no provoque publicaciones duplicadas.

### Scenario R2.1 - Update duplicado

Given `updates.update_id=101` ya existe
When llega nuevamente el `update_id=101`
Then se marca evento `dedupe/skipped`
And no se repiten publicaciones externas.

## Requirement R3 - Publicacion multi-canal

El sistema MUST generar contenido y publicar en WordPress y LinkedIn por cada update valido.

### Scenario R3.1 - Exito completo

Given update valido con URL extraible
When OpenAI y APIs externas responden OK
Then se crea post WordPress
And se crea post LinkedIn con imagen
And `publications.status='success'`.

### Scenario R3.2 - Falla parcial

Given WordPress OK y LinkedIn falla
When se agotan retries de LinkedIn
Then `publications.status='partial'`
And `last_error` contiene causa
And hay evento `failed` de etapa LinkedIn.

## Requirement R4 - Observabilidad y auditoria

El sistema MUST registrar corridas y eventos por etapa.

### Scenario R4.1 - Trazabilidad completa

Given una corrida cualquiera
When finaliza
Then existe una fila en `runs`
And existen eventos asociados en `events`
And todos incluyen `run_id`.

## Requirement R5 - Seguridad de secretos

El sistema MUST consumir secretos por variables de entorno y evitar su exposicion.

### Scenario R5.1 - Arranque sin secreto

Given falta `OPENAI_API_KEY`
When inicia el proceso
Then falla rapido con error claro
And no ejecuta llamadas externas.

### Scenario R5.2 - No leakage

Given ejecucion normal
When se generan logs
Then no aparecen valores de secretos.

## Requirement R6 - Operacion y reproceso

El sistema MUST permitir reproceso manual seguro por `update_id`.

### Scenario R6.1 - Reproceso exitoso

Given `publications.status='failed'` para `update_id=101`
When se ejecuta `reprocess --update-id 101`
Then se reintenta solo ese update
And actualiza estado y eventos en DB.
