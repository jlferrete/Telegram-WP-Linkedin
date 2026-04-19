Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "[quality] ruff check"
.venv\Scripts\python -m ruff check app tests

Write-Host "[quality] mypy"
.venv\Scripts\python -m mypy app tests

Write-Host "[quality] pytest"
.venv\Scripts\python -m pytest

Write-Host "[security] pip-audit"
.venv\Scripts\python -m pip_audit

if (Get-Command gitleaks -ErrorAction SilentlyContinue) {
    Write-Host "[security] gitleaks"
    gitleaks git --redact --no-banner
} else {
    throw "gitleaks is required but not installed"
}

Write-Host "Local quality gate passed"
