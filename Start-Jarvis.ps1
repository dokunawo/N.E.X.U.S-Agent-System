$ErrorActionPreference = "Stop"

$nexusScript = Join-Path $PSScriptRoot "Start-NEXUS.ps1"
& $nexusScript @args
exit $LASTEXITCODE
