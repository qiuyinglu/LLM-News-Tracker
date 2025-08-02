#!/usr/bin/env pwsh

Write-Host "Starting LLM News Thread Web UI..." -ForegroundColor Green
Write-Host ""

# Change to the project root directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Join-Path $scriptPath ".." ".."
Set-Location $projectRoot

# Run the web UI
& "virtualenv\Scripts\python.exe" "src\webui\run.py"

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
