# Tasks - 2026-04-22-cicd-minimo-costo-aware

## T1 - Workflow de PR con checks minimos

- [x] crear `.github/workflows/pr-gates.yml`
- [x] agregar trigger para `pull_request` hacia `main`
- [x] definir job `quality-pr` (lint + tests)
- [x] definir job `security-pr` (pip-audit + gitleaks)

Trace: R1, R3

## T2 - Workflow de release por tags

- [x] crear `.github/workflows/release.yml`
- [x] configurar trigger `push` sobre tags `v*.*.*`
- [x] construir y publicar imagen en GHCR

Trace: R2

## T3 - Documentacion de gobernanza de checks

- [x] actualizar `docs/04-operations/branching-governance.md` con required checks exactos
- [x] actualizar `docs/04-operations/docker-cicd-strategy.md` para reflejar baseline implementado

Trace: R3

## T4 - Verificacion operativa

- [x] ejecutar gate local obligatorio antes de commit
- [x] validar sintaxis de workflows y coherencia documental
- [x] registrar evidencia de cumplimiento por requirement

Evidencia: `docs/sdd/changes/2026-04-22-cicd-minimo-costo-aware/verification.md`

Trace: R1, R2, R3
