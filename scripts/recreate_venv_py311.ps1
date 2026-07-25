# Recreate venv on Python 3.11 (avoids Windows blocking regex on Python 3.14)
# Run from project root in PowerShell:
#
#   .\scripts\recreate_venv_py311.ps1
#
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$py311 = "C:\Users\saira\AppData\Local\Programs\Python\Python311\python.exe"
if (-not (Test-Path $py311)) {
  Write-Host "Python 3.11 not found at $py311"
  Write-Host "Install Python 3.11, then re-run."
  exit 1
}

Write-Host "Removing old venv..."
if (Test-Path ".\venv") { Remove-Item -Recurse -Force ".\venv" }

Write-Host "Creating venv with Python 3.11..."
& $py311 -m venv venv

Write-Host "Installing requirements (this takes several minutes)..."
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\pip.exe install -r requirements.txt

Write-Host "Done. Activate with: .\venv\Scripts\Activate.ps1"
Write-Host "Then: python run_api.py"
