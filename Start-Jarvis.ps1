$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$appRoot = Join-Path $projectRoot "app"
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$port = 8000

$busy = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($busy) {
    $port = 8001
}

Write-Host "Starting N.E.X.U.S Dashboard..."
Write-Host "Open http://127.0.0.1:$port"

Push-Location $appRoot
try {
    & $python -m uvicorn app.main:app --host 127.0.0.1 --port $port
}
finally {
    Pop-Location
}
