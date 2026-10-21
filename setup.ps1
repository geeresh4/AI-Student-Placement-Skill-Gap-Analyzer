$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
Set-Location $projectRoot
$setupTemp = Join-Path $projectRoot 'work\setup-temp'
$env:TEMP = $setupTemp; $env:TMP = $setupTemp
$env:npm_config_cache = Join-Path $projectRoot 'work\npm-cache'
New-Item -ItemType Directory -Force $setupTemp | Out-Null
if (!(Test-Path .venv\Scripts\python.exe)) { python -m venv .venv; if ($LASTEXITCODE -ne 0) { throw 'Could not create Python virtual environment.' } }
& .venv\Scripts\python.exe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed.' }
& .venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
New-Item -ItemType Directory -Force data\synthetic,data\exports,models | Out-Null
& .venv\Scripts\python.exe data\synthetic\generate_demo_data.py --output data\synthetic\students.csv
if ($LASTEXITCODE -ne 0) { throw "Synthetic data generation failed (Python exit code $LASTEXITCODE). Confirm data\synthetic\generate_demo_data.py is present and review the Python error printed above." }
& .venv\Scripts\python.exe scripts\train_model.py --input data\synthetic\students.csv
if ($LASTEXITCODE -ne 0) { throw 'Model training failed.' }
& .venv\Scripts\python.exe -m alembic -c backend\alembic.ini upgrade head
if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
& .venv\Scripts\python.exe scripts\seed_database.py
if ($LASTEXITCODE -ne 0) { throw 'Database seeding failed.' }
Push-Location frontend
npm install
if ($LASTEXITCODE -ne 0) { Pop-Location; throw 'Frontend dependency installation failed.' }
Pop-Location
Write-Host "Setup complete. Run .\run-dev.ps1"
