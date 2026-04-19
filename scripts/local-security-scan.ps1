Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "[security] pip-audit"
.venv\Scripts\python -m pip_audit

if (Get-Command gitleaks -ErrorAction SilentlyContinue) {
    Write-Host "[security] gitleaks"
    gitleaks git --redact --no-banner
} else {
    throw "gitleaks is required but not installed"
}

if (Get-Command trivy -ErrorAction SilentlyContinue) {
    Write-Host "[security] trivy fs"
    trivy fs .
} else {
    throw "trivy is required but not installed"
}

Write-Host "Local security scan completed"
