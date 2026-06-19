param(
    [switch]$Background,
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$appRoot = Join-Path $projectRoot "app"
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$launcher = Join-Path $projectRoot "scripts\start_nexus_background.py"

if (-not (Test-Path $python)) {
    throw "Python was not found at $python. Create the virtual environment before starting N.E.X.U.S."
}

function Get-NexusPort {
    param([int]$StartPort)

    for ($candidate = $StartPort; $candidate -le ($StartPort + 10); $candidate++) {
        $busy = Get-NetTCPConnection -LocalPort $candidate -State Listen -ErrorAction SilentlyContinue
        if (-not $busy) {
            return $candidate
        }
    }

    throw "No open port found from $StartPort to $($StartPort + 10)."
}

if ($Background) {
    if (-not (Test-Path $launcher)) {
        throw "Background launcher was not found at $launcher."
    }

    Write-Host "Starting N.E.X.U.S Dashboard in the background..."
    & $python $launcher --port $Port
    exit $LASTEXITCODE
}

$port = Get-NexusPort -StartPort $Port

Write-Host "Starting N.E.X.U.S Dashboard..."
Write-Host "Open http://127.0.0.1:$port"

Push-Location $appRoot
try {
    & $python -m uvicorn app.main:app --host 127.0.0.1 --port $port
}
finally {
    Pop-Location
}
