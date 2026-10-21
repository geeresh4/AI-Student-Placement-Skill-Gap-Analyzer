$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$listeners = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
$ownerIds = $listeners | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($ownerId in $ownerIds) {
    $owner = Get-CimInstance Win32_Process -Filter "ProcessId = $ownerId"
    if ($owner.CommandLine -match 'uvicorn\s+backend\.app\.main:app') {
        Write-Host "Stopping the previous Placement API process (PID $ownerId) so the updated API can start."
        Stop-Process -Id $ownerId -Force
    } else {
        throw "Port 8000 is used by another process (PID $ownerId, $($owner.Name)). Stop that service or choose another port before starting this API."
    }
}
if ($ownerIds) { Start-Sleep -Seconds 1 }
& .venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
