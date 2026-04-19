# Estrategia Docker + CI/CD (GitHub) Enterprise

## Objetivo

Garantizar entregas repetibles, seguras y observables desde commit hasta ejecucion productiva.

## Docker (runtime confiable)

- Base: `python:3.12-slim`.
- Build reproducible con lockfile de dependencias.
- Usuario no-root para ejecutar el proceso.
- Volumen para persistir SQLite y logs.
- Variables via entorno (nunca bakear secretos en imagen).

## Validacion local-first (cost-aware)

Para controlar costos operativos, el gate principal se ejecuta localmente antes de push/merge.
`gitleaks` y `trivy` son requeridos en la maquina de desarrollo.

Comandos base:

```powershell
./scripts/local-quality-gate.ps1
./scripts/local-security-scan.ps1
```

## GitHub Actions (opcional/minimo)

### 1. Quality Gate (opcional)

- `ruff check`
- `ruff format --check`
- `mypy app`
- `pytest --maxfail=1 --disable-warnings --cov=app`

### 2. Security Gate (opcional)

- `pip-audit`
- `trivy fs .`
- `gitleaks` para detectar secretos

### 3. Build & Validate (opcional)

- build de imagen Docker
- smoke test del contenedor (`run-once --dry-run`)
- tag por SHA corto

### 4. Release (solo tags)

- en tag semantico (`v*.*.*`): push a GHCR
- generar release notes automaticas

### 5. Deploy (solo cuando aplique)

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
