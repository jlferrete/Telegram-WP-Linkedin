# Estrategia Docker + CI/CD (GitHub) Enterprise

## Objetivo

Garantizar entregas repetibles, seguras y observables desde commit hasta ejecucion productiva.

## Docker (runtime confiable)

- Base: `python:3.12-slim`.
- Build reproducible con lockfile de dependencias.
- Usuario no-root para ejecutar el proceso.
- Volumen para persistir SQLite y logs.
- Variables via entorno (nunca bakear secretos en imagen).

## GitHub Actions (pipeline por etapas)

### 1. Quality Gate

- `ruff check`
- `ruff format --check`
- `mypy app`
- `pytest --maxfail=1 --disable-warnings --cov=app`

### 2. Security Gate

- `pip-audit`
- `trivy fs .`
- `gitleaks` para detectar secretos

### 3. Build & Validate

- build de imagen Docker
- smoke test del contenedor (`run-once --dry-run`)
- tag por SHA corto

### 4. Release

- en tag semantico (`v*.*.*`): push a GHCR
- generar release notes automaticas

### 5. Deploy

- `staging` automatico al merge en `main`
- `production` con environment protection + approval manual

## Branching y gobernanza

- Trunk-based development con PRs cortas.
- Protecciones en `main`:
  - checks obligatorios
  - 1 o 2 approvals
  - no direct pushes

## Estrategia de despliegue

- Inicial: un solo contenedor con cron host.
- Evolutivo: `cron + docker run --rm` por job.
- Rollback: redeploy de imagen tag previa.

## Definicion de estabilidad operativa

- Error rate menor al 2% semanal por corridas.
- Mean Time To Recovery menor a 30 minutos.
- Cero secretos filtrados en repositorio y logs.
