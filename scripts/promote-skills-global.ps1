param(
    [string]$ProjectRoot = (Get-Location).Path,
    [string]$GlobalSkillsRoot = "$HOME/.config/opencode/skills",
    [switch]$Backup,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectSkills = Join-Path $ProjectRoot "skills"
if (-not (Test-Path $projectSkills)) {
    throw "Project skills folder not found: $projectSkills"
}

if (-not (Test-Path $GlobalSkillsRoot)) {
    New-Item -ItemType Directory -Path $GlobalSkillsRoot -Force | Out-Null
}

$skills = Get-ChildItem -Path $projectSkills -Directory
if ($skills.Count -eq 0) {
    Write-Host "No project skills found in $projectSkills"
    exit 0
}

foreach ($skill in $skills) {
    $source = $skill.FullName
    $destination = Join-Path $GlobalSkillsRoot $skill.Name

    if (-not (Test-Path (Join-Path $source "SKILL.md"))) {
        Write-Host "Skipping '$($skill.Name)' (missing SKILL.md)"
        continue
    }

    if (Test-Path $destination) {
        if ($Backup) {
            $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
            $backupPath = "${destination}.bak-${stamp}"
            if (-not $DryRun) {
                Move-Item -Path $destination -Destination $backupPath -Force
            }
            Write-Host "Backed up existing '$($skill.Name)' to: $backupPath"
        } else {
            if (-not $DryRun) {
                Remove-Item -Path $destination -Recurse -Force
            }
            Write-Host "Replaced existing global skill: $($skill.Name)"
        }
    }

    if (-not $DryRun) {
        Copy-Item -Path $source -Destination $destination -Recurse -Force
    }
    Write-Host "Promoted skill: $($skill.Name)"
}

Write-Host "Done. Global skills folder: $GlobalSkillsRoot"
Write-Host "Tip: run skill-registry after promotion to refresh compact rules cache."
