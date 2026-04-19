# SDD Formal Guide

## Objetivo

Aplicar Spec-Driven Development (SDD) de forma estricta en este proyecto.

## Flujo obligatorio

1. `proposal.md` (por que existe el cambio, alcance, riesgos)
2. `spec.md` (requisitos verificables + escenarios Given/When/Then)
3. `design.md` (arquitectura y decisiones tecnicas para cumplir la spec)
4. `tasks.md` (plan de implementacion trazable a requisitos)
5. implementacion (codigo)
6. verificacion contra spec (evidencia de cumplimiento)

## Regla de oro

No se escribe codigo de produccion hasta tener `proposal`, `spec`, `design` y `tasks` aprobados.

## Estructura

```text
docs/sdd/
  README.md
  changes/
    <change-id>/
      proposal.md
      spec.md
      design.md
      tasks.md
```

## Convencion de change-id

`YYYY-MM-DD-<slug-corto>`

Ejemplo:

`2026-04-18-migrate-n8n-to-python`
