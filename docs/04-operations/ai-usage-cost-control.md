# AI Usage Cost Control Playbook

## Objetivo

Reducir consumo de requests premium sin perder calidad tecnica ni disciplina enterprise.

## Reglas operativas

- definir alcance claro antes de ejecutar cambios (evitar exploracion abierta innecesaria)
- trabajar por lotes pequenos y semanticos (una capacidad por iteracion)
- reutilizar skills y reglas compactas del registry antes de investigar desde cero
- evitar re-ejecutar tests pesados si no hubo cambios relevantes
- priorizar diffs pequenos y commits atomicos para limitar revalidaciones

## Checklist antes de pedir trabajo al agente

1. objetivo puntual (que queres que cambie)
2. limites del cambio (archivos/modulos)
3. criterio de listo (que prueba/documentacion valida)

## Checklist del agente antes de ejecutar

1. confirmar skill aplicable (si existe)
2. confirmar archivos exactos a tocar
3. evitar tool calls redundantes y lecturas repetidas
4. ejecutar solo verificaciones necesarias para ese cambio

## Anti-patrones (evitar)

- "revisa todo el repo" sin objetivo concreto
- rehacer analisis ya documentado en `docs/`
- mezclar multiples iniciativas no relacionadas en una sola iteracion
- abrir ciclos largos de prueba/error sin hipotesis explicita

## Politica de actualizacion

- actualizar este playbook cuando cambie el flujo de trabajo
- revisar mensualmente si los controles siguen siendo utiles

## Skills globales (estandar compartido)

- promover skills project-level a globales con `scripts/promote-skills-global.ps1`
- ejecutar en modo seguro primero:

```powershell
./scripts/promote-skills-global.ps1 -DryRun
```

- promover con backup de skills existentes:

```powershell
./scripts/promote-skills-global.ps1 -Backup
```

- luego refrescar registry de skills para usar reglas compactas actualizadas
