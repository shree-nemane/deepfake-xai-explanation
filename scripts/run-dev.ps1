# Start forensic API + React UI (two windows)
# Usage: .\scripts\run-dev.ps1

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$BackendVenvPath = Join-Path $Root "backend\.venv\Scripts\Activate.ps1"
$RootVenvPath = Join-Path $Root ".venv\Scripts\Activate.ps1"

if (Test-Path $BackendVenvPath) {
    $ActivateScript = $BackendVenvPath
} elseif (Test-Path $RootVenvPath) {
    $ActivateScript = $RootVenvPath
} else {
    Write-Error "Create the venv first: python -m venv .venv (or backend/.venv)"
    exit 1
}

Write-Host "Starting backend on http://localhost:8000 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root'; & '$ActivateScript'; python -m backend.app"
)

Start-Sleep -Seconds 2

Write-Host "Starting frontend on http://localhost:5173 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root\frontend'; npm run dev"
)

Write-Host "Done. Verify API: curl http://localhost:8000/"
