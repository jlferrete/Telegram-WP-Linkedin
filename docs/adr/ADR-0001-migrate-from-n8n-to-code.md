# ADR-0001: Migrar workflow de n8n a script con SQLite

- Estado: Accepted
- Fecha: 2026-04-18

## Contexto

El workflow actual en n8n presenta problemas operativos y depende de multiples integraciones externas. El flujo es lo suficientemente acotado como para implementar su logica en codigo mantenible.

## Decision

Migrar el flujo a una aplicacion scriptable con:

- ejecucion periodica por cron
- persistencia de estado y auditoria en SQLite
- adaptadores por proveedor externo
- observabilidad con logs estructurados y tablas de eventos

## Consecuencias

Positivas:

- mayor control de errores e idempotencia
- facilidad para testing y versionado
- menor dependencia de plataforma visual

Negativas:

- mayor responsabilidad de mantenimiento del codigo
- necesidad de operar credenciales y scheduler fuera de n8n

## Alternativas consideradas

1. Mantener n8n y solo refactorizar nodos.
   - Pros: menor esfuerzo inicial.
   - Contras: no resuelve fondo (idempotencia, trazabilidad, control de retries).

2. Migrar a otro orquestador visual.
   - Pros: UX similar para flujos.
   - Contras: se mantiene acoplamiento de plataforma y complejidad operacional.

3. Script en codigo + SQLite (elegida).
   - Pros: control total, testabilidad, observabilidad fine-grained.
   - Contras: requiere disciplina de ingenieria y runbooks.
