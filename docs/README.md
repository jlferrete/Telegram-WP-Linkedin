# Documentacion del Proyecto

Este directorio centraliza la documentacion tecnica para la migracion de un workflow de n8n a codigo ejecutable como script, con persistencia en SQLite y ejecucion programada por cron.

## Estructura

- `00-context/`: analisis del estado actual (AS-IS)
- `01-architecture/`: arquitectura objetivo (TO-BE)
- `02-data/`: diseno de datos, esquema y estrategias de idempotencia
- `03-migration/`: plan de migracion por fases y checklist de rollout
- `04-operations/`: operacion diaria, cron, runbooks y observabilidad
- `05-quality/`: estrategia de testing y criterios de aceptacion
- `06-security/`: secretos, cumplimiento minimo y hardening
- `adr/`: decisiones arquitectonicas (Architecture Decision Records)

## Documentos iniciales

- `docs/00-context/workflow-analysis.md`
- `docs/00-context/workflow-analysis.sanitized.md`
- `docs/01-architecture/system-design.md`
- `docs/01-architecture/python-architecture.md`
- `docs/02-data/sqlite-schema.md`
- `docs/03-migration/enterprise-migration-plan.md`
- `docs/04-operations/runbook.md`
- `docs/04-operations/docker-cicd-strategy.md`
- `docs/04-operations/branching-governance.md`
- `docs/04-operations/ai-usage-cost-control.md`
- `docs/06-security/secrets-operating-standard.md`
- `docs/adr/ADR-0001-migrate-from-n8n-to-code.md`
- `docs/adr/ADR-0002-adopt-python-docker-github-actions.md`
- `docs/sdd/README.md`
- `docs/sdd/changes/2026-04-18-migrate-n8n-to-python/proposal.md`
- `docs/sdd/changes/2026-04-18-migrate-n8n-to-python/spec.md`
- `docs/sdd/changes/2026-04-18-migrate-n8n-to-python/design.md`
- `docs/sdd/changes/2026-04-18-migrate-n8n-to-python/tasks.md`
- `docs/sdd/changes/2026-04-18-migrate-n8n-to-python/handoff-next-session.md`

## Criterio de calidad

Toda la documentacion en este arbol sigue un enfoque enterprise grade:

- decisiones explicitas y trazables
- mitigaciones de riesgo antes de producir cambios
- rollback definido
- operabilidad (logs, alertas, runbooks)
- seguridad de credenciales y datos
