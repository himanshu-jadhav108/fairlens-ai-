$ErrorActionPreference = "Stop"

Write-Host "FairLens AI Backend Startup" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python is not installed or not in PATH."
}

if (-not (Test-Path ".\venv")) {
  Write-Host "Creating virtual environment..." -ForegroundColor Yellow
  python -m venv venv
}

$venvPython = Join-Path $PWD "venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
  throw "venv Python executable not found at $venvPython"
}

Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host "Starting API at http://localhost:8000" -ForegroundColor Green
& $venvPython -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
