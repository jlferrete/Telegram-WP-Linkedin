# Reconectar y validar Engram MCP (paso a paso)

Este procedimiento te sirve cuando en el panel MCP del TUI no aparece `engram`, aunque el backend pueda estar bien.

## 1) Cerrar la sesion actual de OpenCode

1. Sali del TUI de OpenCode (cerrar la app/sesion actual).

## 2) Reabrir OpenCode en este workspace

1. Abri una terminal nueva en este repo: `D:\workspace-2026\Telegram-WP-Linkedin`.
2. Inicia OpenCode normalmente.

## 3) Verificar estado real de MCP (fuera del panel)

1. Ejecuta:

```powershell
opencode mcp list
```

2. Resultado esperado:
   - `context7` -> `connected`
   - `engram` -> `connected`

Si ambos salen conectados, el problema es visual del sidebar/TUI, no de conexion MCP.

## 4) Refresh fuerte (si el panel sigue sin mostrar Engram)

1. Cierra OpenCode.
2. Mata procesos viejos:

```powershell
Get-Process opencode -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process engram -ErrorAction SilentlyContinue | Stop-Process -Force
```

3. Vuelve a abrir OpenCode en el repo.
4. Ejecuta otra vez:

```powershell
opencode mcp list
```

## 5) Validacion con logs debug (si queres evidencia tecnica)

Ejecuta:

```powershell
opencode --print-logs --log-level DEBUG mcp list
```

Busca estas lineas clave:
- `service=mcp key=engram type=local found`
- `engram connected`

## 6) Confirmar que Engram esta en modo local (no cloud)

Revisa en `C:\Users\josel\.config\opencode\opencode.json`:

- `mcp.engram.type` debe ser `local`
- comando: `C:\Users\josel\go\bin\engram.exe mcp --tools=agent`

Tambien podes validar servicio local:

```powershell
Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:7437/health"
```

Respuesta esperada: JSON con `"service":"engram"` y `"status":"ok"`.

## 7) Si todo conecta pero el sidebar no lo muestra

Conclusión: es un desajuste visual del TUI.

Accion recomendada:
1. Guardar evidencia:
   - screenshot del panel MCP
   - salida de `opencode mcp list`
   - salida de `opencode --print-logs --log-level DEBUG mcp list`
2. Reportar bug de UI en el repositorio/proyecto de OpenCode.
