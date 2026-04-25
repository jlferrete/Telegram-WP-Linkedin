# Proposal - 2026-04-22-cicd-minimo-costo-aware

## Contexto

El proyecto ya tiene estandares de calidad y seguridad local-first (`local-quality-gate.ps1` y `local-security-scan.ps1`) y una estrategia de CI/CD documentada.
Sin embargo, hoy no existen workflows en `.github/workflows`, por lo que la gobernanza de PR y releases no tiene enforcement automatico.

## Problema

- desalineacion entre politica documentada y ejecucion real en GitHub
- riesgo de merges sin trazabilidad minima de quality/security
- ausencia de mecanismo automatizado de release por tags

## Objetivo del cambio

Implementar un baseline de CI/CD minimo, costo-aware y alineado al enfoque local-first: validaciones livianas en PR y release automatizado solo por tags semanticos.

## Capabilities

- `cicd-minimo-pr`: checks minimos en PR (sin duplicar toda la carga local)
- `release-por-tags`: build/publish solo en tags `v*.*.*`
- `gobernanza-checks`: nombres de checks estables para branch protection

## Alcance (in)

- crear workflows de GitHub Actions para:
  - quality gate minimo en PR
  - security gate minimo en PR
  - release por tags semanticos
- estandarizar nombres de jobs/checks para usar como required checks
- documentar el flujo operativo para integrarlo con branch protection

## Fuera de alcance (out)

- despliegue automatico a entornos (staging/production)
- incremento de cobertura de tests de aplicacion
- cambios funcionales del pipeline de negocio

## Riesgos

- duplicar costo de ejecucion entre local y cloud si los gates son pesados
- falsos negativos/positivos si los checks no reflejan los scripts locales
- friccion en merges si los required checks cambian de nombre frecuentemente

## Mitigaciones

- mantener workflows minimos y consistentes con la estrategia local-first
- fijar convencion estable de nombres de jobs
- versionar runbook de gobernanza con pasos de activacion de branch protection

## Criterio de exito

- existe al menos un workflow de PR para quality y otro para security, ejecutables
- existe workflow de release disparado solo por tags `v*.*.*`
- los nombres de checks quedan documentados y listos para configurar como obligatorios en `main`
