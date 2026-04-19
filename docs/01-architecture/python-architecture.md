# Arquitectura Python Enterprise

## Decisión

Se adopta Python como stack principal para la migracion del workflow.

## Por que es acertado para este caso

- Ecosistema maduro para integraciones HTTP y automatizacion.
- Excelente productividad para pipelines IO-bound como este.
- Buen soporte para tipado progresivo, testing y tooling de calidad.
- Curva de mantenimiento favorable para scripts de operacion.

## Estructura recomendada del proyecto

```text
app/
  main.py
  core/
    pipeline.py
    services.py
    models.py
  adapters/
    telegram.py
    openai.py
    wordpress.py
    linkedin.py
    pexels.py
  infra/
    config.py
    db.py
    logging.py
    retry.py
  repositories/
    state_repo.py
    runs_repo.py
    updates_repo.py
    publications_repo.py
    events_repo.py
tests/
  unit/
  integration/
migrations/
docs/
```

## Principios de diseño

- Arquitectura hexagonal ligera (puertos y adaptadores).
- Dependencias hacia adentro (adapters -> core, nunca al reves).
- Lado externo aislado por cliente/proveedor.
- Dominio testeable sin red ni filesystem real.

## Stack tecnico sugerido

- Python 3.12+
- `httpx` para clientes HTTP
- `pydantic` para validacion de contratos
- `sqlalchemy` + `alembic` para SQLite y migraciones
- `tenacity` para retries
- `structlog` para logging JSON
- `pytest` para tests
- `ruff` + `mypy` para calidad estatica

## Tradeoffs

- Python no es ideal para CPU heavy, pero este workflow es IO-bound.
- SQLite limita concurrencia horizontal extrema; para esta carga es suficiente.
- Si escala fuerte, migrar repositorios a PostgreSQL sin tocar el core.
