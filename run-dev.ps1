Start-Process powershell -WorkingDirectory $PSScriptRoot -ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File','run-backend.ps1' -WindowStyle Hidden
Start-Sleep -Seconds 2
Push-Location frontend
npm run dev -- --host 127.0.0.1
Pop-Location
