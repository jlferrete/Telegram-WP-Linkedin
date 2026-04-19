# Workflow Analysis (Sanitized)

Documento sanitizado del workflow original para referencia tecnica sin exponer credenciales ni tokens.

## Origen

- Fuente original (sensible, ignorada por Git): `Telegram Bot - Data Tables.json`

## Flujo funcional resumido

- Lee `telegram_offset` desde tabla de estado.
- Consulta updates en Telegram con polling.
- Extrae URL y metadatos desde el mensaje.
- Genera copy con OpenAI.
- Publica en WordPress.
- Busca imagen en Pexels.
- Publica en LinkedIn.
- Notifica por Telegram y avanza offset.

## Riesgos observados

- Acoplamiento fuerte entre nodos y proveedores.
- Riesgo de fuga de secretos si se versiona el export completo.
- Dificultad para testear idempotencia y fallas parciales.

## Regla de versionado

- Nunca commitear exports de workflows sin sanitizacion previa.
- Mantener en Git solo artefactos sanitizados y documentacion tecnica.
