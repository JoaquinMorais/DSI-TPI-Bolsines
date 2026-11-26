$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$BackendPort = if ($env:BACKEND_PORT) { $env:BACKEND_PORT } else { "8000" }
$FrontendPort = if ($env:FRONTEND_PORT) { $env:FRONTEND_PORT } else { "5173" }
$PythonBin = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { "python" }
$VenvDir = Join-Path $Root ".venv"
$RootUnix = $Root -replace '\\', '/'
$DatabaseUrl = if ($env:DATABASE_URL) { $env:DATABASE_URL } else { "sqlite+aiosqlite:///$RootUnix/backend/data/bolsines.db" }
$env:CORS_ORIGINS = if ($env:CORS_ORIGINS) { $env:CORS_ORIGINS } else { "http://localhost:$FrontendPort" }
$env:VITE_API_URL = if ($env:VITE_API_URL) { $env:VITE_API_URL } else { "http://localhost:$BackendPort" }

Write-Host "Bolsines - entorno de desarrollo"

& $PythonBin -c "import sys; raise SystemExit(0 if sys.version_info[:2] >= (3, 12) else 1)"
if ($LASTEXITCODE -ne 0) { throw "Se requiere Python 3.12 o superior." }

if (-not (Test-Path $VenvDir)) {
  Write-Host "Creando entorno virtual en .venv..."
  & $PythonBin -m venv $VenvDir
}
$VenvPython = Join-Path $VenvDir "Scripts/python.exe"
& $VenvPython -m pip install --quiet --upgrade pip
& $VenvPython -m pip install --quiet -r backend/requirements.txt

$NodeMajor = [int](& node -e "process.stdout.write(process.versions.node.split('.')[0])")
if ($NodeMajor -lt 18) { throw "Se requiere Node 18 o superior." }
if (-not (Test-Path (Join-Path $Root "frontend/node_modules"))) {
  Write-Host "Instalando dependencias del frontend..."
  Push-Location frontend
  & npm install --no-audit --no-fund
  Pop-Location
}

$EnvFile = Join-Path $Root "backend\.env"
if (-not (Test-Path $EnvFile)) {
  Write-Host "Creando backend\.env desde backend\.env.example..."
  Copy-Item (Join-Path $Root "backend\.env.example") $EnvFile
}

Write-Host "Sembrando datos..."
$env:DATABASE_URL = $DatabaseUrl
& $VenvPython -m backend.data.seed --reset

Write-Host "Backend:  http://localhost:$BackendPort/docs"
Write-Host "Frontend: http://localhost:$FrontendPort"

$backend = Start-Process -FilePath $VenvPython `
  -ArgumentList @("-m", "uvicorn", "main:app", "--app-dir", "backend", "--port", $BackendPort, "--reload") `
  -PassThru -NoNewWindow

Push-Location frontend
$frontend = Start-Process -FilePath "node" `
  -ArgumentList @("node_modules/vite/bin/vite.js", "--host", "0.0.0.0", "--port", $FrontendPort) `
  -PassThru -NoNewWindow
Pop-Location

try {
  Wait-Process -Id $backend.Id, $frontend.Id
} finally {
  Write-Host "Deteniendo servicios..."
  Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
  Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
}
