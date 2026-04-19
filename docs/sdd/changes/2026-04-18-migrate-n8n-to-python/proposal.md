# Proposal - 2026-04-18-migrate-n8n-to-python

## Contexto

El workflow actual en n8n presenta fragilidad operativa, dependencias acopladas y riesgos de idempotencia/seguridad.

## Problema

- dificultad para garantizar no-duplicacion por `update_id`
- trazabilidad operativa limitada
- secretos expuestos en configuracion exportada
- complejidad para testing reproducible

## Objetivo del cambio

Migrar a un servicio en Python ejecutable por cron, con SQLite para estado y auditoria, empaquetado en Docker y pipeline CI/CD en GitHub.

## Alcance (in)

- procesamiento de updates Telegram con offset persistente
- generacion y publicacion de contenido en WordPress/LinkedIn
- notificacion de resultado por Telegram
- idempotencia por `update_id`
- observabilidad en `runs/events`
- estandar de secretos sin costo adicional

## Fuera de alcance (out)

- reemplazo de SQLite por base distribuida
- dashboard visual dedicado de observabilidad
- multi-tenant

## Riesgos

- regresiones funcionales al cortar n8n
- errores de credenciales/runtime en docker
- duplicados si lock/idempotencia no se implementan bien

## Mitigaciones

- shadow run previo a cutover
- testing por capas (unit + integracion)
- tablas de auditoria y reproceso
- runbook operativo y politica de secretos

## Criterio de exito

- cero duplicados por `update_id`
- corridas trazables al 100%
- despliegue reproducible en contenedor
- CI/CD con quality y security gates
