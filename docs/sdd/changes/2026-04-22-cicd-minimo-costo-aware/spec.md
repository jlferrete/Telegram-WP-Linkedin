# Specification - 2026-04-22-cicd-minimo-costo-aware

## Requirement R1 - Checks minimos de PR

El repositorio MUST ejecutar validaciones minimas de calidad y seguridad en cada Pull Request hacia `main` usando GitHub Actions.

### Scenario R1.1 - Quality en PR

Given existe un Pull Request abierto hacia `main`
When se dispara el workflow de PR
Then se ejecuta un job de quality con nombre estable
And el job valida al menos lint y tests basicos
And el resultado queda visible como check del PR.

### Scenario R1.2 - Security en PR

Given existe un Pull Request abierto hacia `main`
When se dispara el workflow de PR
Then se ejecuta un job de security con nombre estable
And el job valida al menos auditoria de dependencias y deteccion de secretos
And el resultado queda visible como check del PR.

## Requirement R2 - Release solo por tags semanticos

El repositorio MUST construir y publicar imagen de contenedor solo cuando se crea un tag semantico `v*.*.*`.

### Scenario R2.1 - Tag semantico

Given se hace push de tag `v1.2.3`
When se dispara el workflow de release
Then se construye imagen Docker
And se publica en GHCR con tag semantico
And el workflow no depende de eventos de PR.

### Scenario R2.2 - Push de rama sin tag

Given se hace push de commits a una rama sin tag
When se evalua el trigger de release
Then el workflow de release no se ejecuta.

## Requirement R3 - Nombres de checks gobernables

El sistema MUST mantener nombres de jobs/checks estables y documentados para que puedan configurarse como required checks en branch protection.

### Scenario R3.1 - Convencion estable

Given existe configuracion de branch protection en `main`
When el repositorio agrega required checks
Then se pueden seleccionar checks con nombres deterministas
And esos nombres estan documentados en runbook o documento operativo.

### Scenario R3.2 - Trazabilidad operativa

Given un maintainer revisa la politica de merge
When consulta la documentacion operativa
Then encuentra comandos locales obligatorios y checks cloud minimos
And puede aplicar branch protection sin inferencias ad hoc.
