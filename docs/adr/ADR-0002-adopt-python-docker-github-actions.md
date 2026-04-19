# ADR-0002: Adoptar Python + Docker + GitHub Actions

- Estado: Accepted
- Fecha: 2026-04-18

## Contexto

El sistema requiere migrar desde n8n a una implementacion robusta, mantenible y con operacion confiable.

## Decision

Se adopta:

- Python 3.12+ como lenguaje principal
- Docker como estandar de empaquetado/runtime
- GitHub Actions como plataforma CI/CD

## Justificacion tecnica

- Python acelera el desarrollo de integraciones y pruebas.
- Docker garantiza paridad dev/staging/prod y reduce drift.
- GitHub Actions integra controles de calidad, seguridad y release en el mismo flujo.

## Consecuencias

Positivas:

- pipeline automatizado de calidad y seguridad
- despliegues repetibles y rollback por imagen
- onboarding mas rapido para nuevos contributors

Negativas:

- mayor inversion inicial de setup DevOps
- necesidad de disciplina en versionado y gestion de secretos

## Alternativas consideradas

1. Node.js + Docker + Actions
   - Pros: buen rendimiento IO, ecosistema amplio.
   - Contras: menor preferencia del equipo para mantenimiento actual.

2. Python sin Docker
   - Pros: setup rapido.
   - Contras: riesgo de diferencias entre entornos y menor confiabilidad operativa.

3. Python + Docker + GitHub Actions (elegida)
   - Pros: equilibrio entre productividad, gobernanza y estabilidad.
   - Contras: curva inicial DevOps moderada.
