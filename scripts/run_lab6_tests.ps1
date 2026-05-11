$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$ReportDir = Join-Path $Root "docs/lab6"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$HtmlReport = Join-Path $ReportDir "pytest_report.html"
$LogFile = Join-Path $ReportDir "pytest_output.txt"

Write-Host "Lab 6: API tests (PostgreSQL required; app_test DB is created if missing)"
Write-Host "Repository root: $Root"
Write-Host ""

poetry run pytest tests/ -v --tb=short `
    --html=$HtmlReport `
    --self-contained-html `
    2>&1 | Tee-Object -FilePath $LogFile

$exit = $LASTEXITCODE
Write-Host ""
Write-Host "HTML report: $HtmlReport"
Write-Host "Console log: $LogFile"
exit $exit
