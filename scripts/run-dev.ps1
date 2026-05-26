# Start forensic API + React UI (two windows)
# Usage: .\scripts\run-dev.ps1

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Error "Create the venv first: python -m venv .venv"
    exit 1
}

Write-Host "Starting backend on http://localhost:8000 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root'; .\.venv\Scripts\Activate.ps1; python -m backend.app"
)

Start-Sleep -Seconds 2

Write-Host "Starting frontend on http://localhost:5173 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root\frontend'; npm run dev"
)

Write-Host "Done. Verify API: curl http://localhost:8000/"
