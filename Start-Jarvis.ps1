$ErrorActionPreference = "Stop"

$ramboScript = Join-Path $PSScriptRoot "Start-RAMBO.ps1"
& $ramboScript @args
exit $LASTEXITCODE
