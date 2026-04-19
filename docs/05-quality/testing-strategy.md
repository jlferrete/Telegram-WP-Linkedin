# Testing Strategy

## Objetivo

Definir una estrategia de calidad por capas para mantener el pipeline estable ante cambios frecuentes de APIs externas.

## Piramide de pruebas

- unit tests (rapidos): reglas de dominio, parseo de mensajes, calculo de offset, dedupe
- adapter contract tests (mock HTTP): validacion de parseo de payloads por proveedor
- integration tests (SQLite real + adapters mock): corrida `run-once` end-to-end sin red

## Cobertura minima por requisito

- R1: tests de offset en corridas con y sin mensajes
- R2: tests de dedupe por `update_id` repetido
- R3: tests de success/partial/failure en publicacion multi-canal
- R4: tests de eventos por etapa y run status final
- R5: tests de fail-fast de config y sanitizacion de logs
- R6: tests de `reprocess --update-id`

## Contratos de proveedores

Cada adapter debe tener tests de contrato contra respuestas representativas:

- happy path (payload valido)
- shape drift (campo faltante/renombrado)
- errores HTTP (4xx/5xx)

Cuando cambie una API:

1. agregar fixture de respuesta nueva
2. ajustar adapter
3. mantener compatibilidad con respuesta previa cuando sea viable
4. documentar cambio y decision en ADR o changelog tecnico

## Gating en CI

- lint: `ruff check app tests`
- typing: `mypy app`
- tests: `pytest`
- security: `gitleaks`, `pip-audit`, `trivy fs`

Sin estos gates en verde, no se libera imagen ni se despliega.
