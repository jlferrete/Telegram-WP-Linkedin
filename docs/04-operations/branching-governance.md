# Branching & Governance Policy

## Objetivo

Asegurar trazabilidad, calidad y seguridad en un flujo enterprise grade con cambios frecuentes.

## Politica

- `main` es rama protegida y estable.
- Prohibido commitear directo a `main`.
- Todo cambio entra por PR desde ramas cortas.

## Convencion de ramas

- `feat/<scope>-<short-desc>`
- `fix/<scope>-<short-desc>`
- `chore/<scope>-<short-desc>`
- `docs/<scope>-<short-desc>`

Ejemplos:

- `feat/adapters-openai-linkedin`
- `fix/pipeline-offset-commit`
- `docs/quality-testing-strategy`

## Reglas de PR

- PR chica (ideal <= 300 lineas netas).
- Commits atomicos por unidad semantica.
- Checks obligatorios en verde: `quality-pr` y `security-pr`.
- Minimo 1 aprobacion antes de merge.
- Merge squash permitido solo si conserva mensaje semantico claro.

## Required checks en branch protection (`main`)

Configurar en GitHub -> Settings -> Branches -> Branch protection rule sobre `main`:

- `quality-pr`
- `security-pr`

Estos nombres deben mantenerse estables para evitar drift entre governance y CI.

## Commits (conventional commits)

- `feat:` nueva capacidad funcional
- `fix:` correccion de bug
- `refactor:` mejora interna sin cambiar comportamiento
- `test:` pruebas
- `docs:` documentacion
- `chore:` mantenimiento/herramientas

## Hotfix

- Solo para incidentes productivos.
- Se crea rama `fix/hotfix-...` desde `main`.
- PR con prioridad alta y evidencia del incidente.

## Relacion con SDD

- Un cambio SDD puede abarcar multiples PRs.
- Cada PR debe referenciar requisito(s) de `spec.md` que cubre.
