# Secrets Operating Standard (Zero-Cost)

## Objetivo

Definir un estandar operativo sin costo adicional para gestionar secretos de forma robusta, escalable y confiable en CI/CD y runtime.

## Alcance

- aplica a desarrollo local, CI/CD en GitHub Actions y runtime Docker en host propio
- obligatorio para todo secret nuevo o rotado

## Principios obligatorios

- nunca commitear secretos en repo
- nunca hornear secretos dentro de imagen Docker
- separar secretos de CI y secretos de runtime
- minimo privilegio y menor exposicion posible
- rotacion periodica y trazabilidad de cambios

## Modelo operativo (fuente de verdad por entorno)

- `local`: archivo `.env.local` fuera de git (solo desarrollo)
- `ci`: GitHub Environments Secrets (`staging` y `production`)
- `runtime`: archivo protegido en host (`/opt/telegram-wp-linkedin/secrets.env`)

## Variables estandar

- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY`
- `PEXELS_API_KEY`
- `WP_BASE_URL`
- `WP_USER`
- `WP_APP_PASSWORD`
- `LINKEDIN_ACCESS_TOKEN`

## Provisioning inicial

### 1) Crear secretos en GitHub (CI/CD)

- crear environments: `staging`, `production`
- cargar secretos por environment (nunca en repositorio)
- activar protection rules en `production` (approval manual)

### 2) Crear secretos en host (runtime)

```bash
sudo mkdir -p /opt/telegram-wp-linkedin
sudo touch /opt/telegram-wp-linkedin/secrets.env
sudo chown root:root /opt/telegram-wp-linkedin/secrets.env
sudo chmod 600 /opt/telegram-wp-linkedin/secrets.env
```

Contenido esperado de `secrets.env`:

```dotenv
TELEGRAM_BOT_TOKEN=***
OPENAI_API_KEY=***
PEXELS_API_KEY=***
WP_BASE_URL=***
WP_USER=***
WP_APP_PASSWORD=***
LINKEDIN_ACCESS_TOKEN=***
```

### 3) Ejecutar contenedor sin exponer secretos

```bash
docker run --rm \
  --env-file /opt/telegram-wp-linkedin/secrets.env \
  -v /opt/telegram-wp-linkedin/data:/data \
  ghcr.io/<org>/telegram-wp-linkedin:<tag> \
  python -m app.main run-once --db-path /data/app.db
```

## Politica local (desarrollo)

- usar `.env.local` en maquina del desarrollador
- incluir `.env*` en `.gitignore` (excepto `.env.example`)
- no compartir secretos por chat/email

## Rotacion de secretos

- frecuencia minima: cada 90 dias
- rotacion inmediata ante sospecha de fuga
- orden de rotacion:
  1. generar nueva credencial en proveedor
  2. actualizar GitHub Secrets (`staging` -> validar -> `production`)
  3. actualizar `/opt/telegram-wp-linkedin/secrets.env`
  4. ejecutar corrida de verificacion (`run-once --dry-run`)
  5. revocar credencial anterior

## Deteccion y prevencion

- `gitleaks` obligatorio en CI
- `trivy fs` y `pip-audit` obligatorios en CI
- redaccion de secretos en logs (nunca imprimir valores)

## Respuesta a incidente de fuga

1. pausar cron/job inmediatamente
2. rotar secretos comprometidos
3. revocar tokens previos
4. revisar logs y alcance temporal
5. documentar incidente y acciones correctivas
6. reanudar ejecucion

## Checklist de cumplimiento

- no hay secretos en git history reciente
- no hay secretos en imagen Docker
- secretos runtime con `chmod 600`
- environments separados en GitHub
- rotacion registrada en runbook
- pruebas CI/security en verde

## Escalabilidad futura (sin cambio de codigo)

Cuando el volumen o compliance crezcan, migrar a secret manager dedicado (Vault/Key Vault/etc.) manteniendo la misma interfaz de variables de entorno.
