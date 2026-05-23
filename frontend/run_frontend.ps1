$ErrorActionPreference = "Stop"

Write-Host "FairLens AI Frontend Startup" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  throw "npm is not installed or not in PATH."
}

if (-not (Test-Path ".\node_modules")) {
  Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
  npm install
}

Write-Host "Starting frontend at http://localhost:5173" -ForegroundColor Green
npm run dev
