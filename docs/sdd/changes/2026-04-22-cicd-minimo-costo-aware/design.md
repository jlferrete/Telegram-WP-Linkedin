# Design - 2026-04-22-cicd-minimo-costo-aware

## Arquitectura de workflows

Se definen dos pipelines desacoplados:

- `pr-gates.yml`: validaciones minimas para PR hacia `main`
- `release.yml`: build y publish de contenedor solo por tags `v*.*.*`

La estrategia mantiene local-first como fuente principal de rigor, y usa cloud checks como red de seguridad y trazabilidad de merge.

## Mapeo requirement -> componentes

- R1: `.github/workflows/pr-gates.yml`
- R2: `.github/workflows/release.yml`
- R3: `.github/workflows/pr-gates.yml`, `docs/04-operations/branching-governance.md`, `docs/04-operations/docker-cicd-strategy.md`

## Decisiones tecnicas

1. **Workflow unico de PR con dos jobs estables**
   - Jobs: `quality-pr` y `security-pr`.
   - Motivo: simplifica required checks y evita dispersion de nombres.

2. **Cobertura minima en cloud para controlar costo**
   - Quality: lint + pytest (sin matrix extensa).
   - Security: `pip-audit` + `gitleaks`.
   - Motivo: el gate pesado ya corre localmente.

3. **Release solo por tags semanticos**
   - Trigger exclusivo `push.tags: v*.*.*`.
   - Motivo: impedir builds/publicaciones accidentales por pushes ordinarios.

4. **Publicacion en GHCR con `GITHUB_TOKEN`**
   - Uso de `docker/login-action` contra `ghcr.io`.
   - Motivo: evitar secretos extras para autenticacion basica de repo package.

## Tradeoffs

- **Pro**: menor costo cloud, menos ruido, required checks claros.
- **Contra**: menor profundidad de validacion remota; se compensa con disciplina local obligatoria.

## Riesgos y mitigaciones

- Riesgo: drift entre scripts locales y checks de PR.
  - Mitigacion: documentar alcance de cada uno y mantener comandos homogeneos.

- Riesgo: fallas de permisos en publish a GHCR.
  - Mitigacion: declarar permisos explicitos (`packages: write`) y validar en tag de prueba.

## Criterios de verificacion tecnica

- PR abre checks `quality-pr` y `security-pr` en GitHub.
- Tag `vX.Y.Z` ejecuta build y publish de imagen.
- Documentacion operativa lista los nombres de checks para branch protection.
