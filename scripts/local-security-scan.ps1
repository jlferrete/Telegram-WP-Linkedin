Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "[security] pip-audit"
.venv\Scripts\python -m pip_audit

if (Get-Command gitleaks -ErrorAction SilentlyContinue) {
    Write-Host "[security] gitleaks"
    gitleaks detect --source . --no-git
} else {
    Write-Host "[security] gitleaks not found, skipping"
}

if (Get-Command trivy -ErrorAction SilentlyContinue) {
    Write-Host "[security] trivy fs"
    trivy fs .
} else {
    Write-Host "[security] trivy not found, skipping"
}

Write-Host "Local security scan completed"
