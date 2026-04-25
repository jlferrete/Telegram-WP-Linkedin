# Tasks - 2026-04-22-cicd-minimo-costo-aware

## T1 - Workflow de PR con checks minimos

- crear `.github/workflows/pr-gates.yml`
- agregar trigger para `pull_request` hacia `main`
- definir job `quality-pr` (lint + tests)
- definir job `security-pr` (pip-audit + gitleaks)

Trace: R1, R3

## T2 - Workflow de release por tags

- crear `.github/workflows/release.yml`
- configurar trigger `push` sobre tags `v*.*.*`
- construir y publicar imagen en GHCR

Trace: R2

## T3 - Documentacion de gobernanza de checks

- actualizar `docs/04-operations/branching-governance.md` con required checks exactos
- actualizar `docs/04-operations/docker-cicd-strategy.md` para reflejar baseline implementado

Trace: R3

## T4 - Verificacion operativa

- ejecutar gate local obligatorio antes de commit
- validar sintaxis de workflows y coherencia documental
- registrar evidencia de cumplimiento por requirement

Trace: R1, R2, R3
