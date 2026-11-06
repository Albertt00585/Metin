# Construieste installer-ul Organizare Metin: dist\OrganizareMetinSetup.exe
# Folosire:  powershell -ExecutionPolicy Bypass -File build.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$source = "Organizare Metin.pyw"

$version = [regex]::Match((Get-Content -LiteralPath $source -Raw), 'APP_VERSION = "([^"]+)"').Groups[1].Value
if (-not $version) { throw "Nu gasesc APP_VERSION in $source" }
Write-Host "Construiesc Organizare Metin $version" -ForegroundColor Magenta

# 1. Aplicatia -> dist\Organizare Metin\Organizare Metin.exe
python -m PyInstaller $source --name "Organizare Metin" --windowed --noconfirm --clean `
    --icon assets\metin.ico --add-data "assets\metin.ico;assets" --collect-data customtkinter
if ($LASTEXITCODE) { throw "PyInstaller a esuat" }

# 2. Installer-ul -> dist\OrganizareMetinSetup.exe
$iscc = @("$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe", "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe") |
    Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) { throw "Inno Setup 6 nu este instalat (winget install JRSoftware.InnoSetup)" }
& $iscc /Qp "/DAppVersion=$version" installer.iss
if ($LASTEXITCODE) { throw "Inno Setup a esuat" }

Write-Host "Gata: dist\OrganizareMetinSetup.exe (versiunea $version)" -ForegroundColor Green
