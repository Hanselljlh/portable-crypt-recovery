# Build script for PCR Windows portable release
# Run from repo root:  .\packaging\windows\build.ps1
# Or with version:     .\packaging\windows\build.ps1 -Version "0.1.0"
#
# Output: dist\PCR-windows-portable\   (ready-to-zip portable folder)
#         dist\PCR-windows-portable.zip (release archive)

param(
    [string]$Version = "0.1.0",
    [string]$PyExePath = "",   # override if python.exe is not on PATH
    [switch]$SkipZip
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot  = (Get-Item $PSScriptRoot).Parent.Parent.FullName
$DistDir   = Join-Path $RepoRoot "dist"
$BuildDir  = Join-Path $DistDir  "PCR"           # PyInstaller output
$PortDir   = Join-Path $DistDir  "PCR-windows-portable"
$ZipPath   = Join-Path $DistDir  "PCR-windows-portable-$Version.zip"

# Resolve Python executable: parameter > auto-detect common locations > fallback
if ($PyExePath -ne "") {
    $PyExe = $PyExePath
} else {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
    ) | Where-Object { Test-Path $_ }
    $PyExe = if ($candidates.Count -gt 0) { $candidates[0] } else { "python" }
}

Write-Host "=== PCR Windows build v$Version ===" -ForegroundColor Cyan
Write-Host "Repo root : $RepoRoot"
Write-Host "Output    : $PortDir"

# ------------------------------------------------------------------
# 1. Verify python + pyinstaller
# ------------------------------------------------------------------
try { & $PyExe --version | Out-Null } catch {
    Write-Error "Python not found. Set `$PyExe or add to PATH."
}

& $PyExe -m PyInstaller --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    & $PyExe -m pip install pyinstaller
}

# ------------------------------------------------------------------
# 2. Install the package in editable mode so PyInstaller can find it
# ------------------------------------------------------------------
Write-Host "`nInstalling package..." -ForegroundColor Cyan
& $PyExe -m pip install -e (Join-Path $RepoRoot ".") --quiet

# ------------------------------------------------------------------
# 3. Run PyInstaller
# ------------------------------------------------------------------
Write-Host "`nRunning PyInstaller..." -ForegroundColor Cyan
$SpecFile = Join-Path $PSScriptRoot "pyinstaller-one-folder.spec"

Push-Location $RepoRoot
try {
    & $PyExe -m PyInstaller $SpecFile --distpath $DistDir --workpath (Join-Path $DistDir "build-work") --noconfirm
    if ($LASTEXITCODE -ne 0) { Write-Error "PyInstaller failed." }
} finally {
    Pop-Location
}

# ------------------------------------------------------------------
# 4. Assemble portable folder layout
# ------------------------------------------------------------------
Write-Host "`nAssembling portable layout..." -ForegroundColor Cyan

if (Test-Path $PortDir) { Remove-Item $PortDir -Recurse -Force }
New-Item -ItemType Directory -Path $PortDir | Out-Null

# Copy PyInstaller output (exe + _internal/) into portable root
Copy-Item -Path (Join-Path $BuildDir "*") -Destination $PortDir -Recurse -Force

# Create portable folder structure (mirrors PORTABLE_DIRS in startup.py)
foreach ($folder in @(
    "app",
    "tools\hashcat",
    "workspaces\default",
    "config",
    "logs",
    "docs"
)) {
    New-Item -ItemType Directory -Path (Join-Path $PortDir $folder) -Force | Out-Null
}

# Copy docs
$DocsSource = Join-Path $RepoRoot "docs"
if (Test-Path $DocsSource) {
    Copy-Item -Path (Join-Path $DocsSource "*") -Destination (Join-Path $PortDir "docs") -Recurse -Force
}

# Copy hashcat placeholder
$HashcatPlaceholder = Join-Path $RepoRoot "packaging\portable-template\PCR\tools\hashcat\README-place-hashcat-here.txt"
if (Test-Path $HashcatPlaceholder) {
    Copy-Item $HashcatPlaceholder (Join-Path $PortDir "tools\hashcat\") -Force
}

# Write a minimal README in the portable root
$ReadmePath = Join-Path $PortDir "README.txt"
@"
Portable Crypt Recovery (PCR) v$Version
=======================================

QUICK START
-----------
1. Place hashcat.exe (and its _internal/ folder) into:
       tools\hashcat\hashcat.exe

2. Double-click PCR.exe to launch.

3. On first run, go to Settings -> Workspace to open or create
   your workspace folder (default workspace is pre-created in workspaces\default\).

4. Go to Settings -> Hashcat Setup and verify Hashcat.

FOLDER LAYOUT
-------------
  PCR.exe                 - Application executable
  _internal\              - Runtime libraries (do not delete)
  workspaces\default\     - Default recovery workspace
  tools\hashcat\          - Place hashcat.exe here
  config\                 - App configuration
  logs\                   - Application logs
  docs\                   - User guide

SUPPORT
-------
https://github.com/Hanselljlh/portable-crypt-recovery
"@ | Out-File -FilePath $ReadmePath -Encoding utf8

Write-Host "Portable folder assembled at: $PortDir" -ForegroundColor Green

# ------------------------------------------------------------------
# 5. Create zip archive
# ------------------------------------------------------------------
if (-not $SkipZip) {
    Write-Host "`nCreating zip archive..." -ForegroundColor Cyan
    if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
    Compress-Archive -Path (Join-Path $PortDir "*") -DestinationPath $ZipPath
    $SizeMB = [math]::Round((Get-Item $ZipPath).Length / 1MB, 1)
    Write-Host "Archive: $ZipPath ($SizeMB MB)" -ForegroundColor Green
}

Write-Host "`n=== Build complete ===" -ForegroundColor Cyan
Write-Host "Portable folder : $PortDir"
if (-not $SkipZip) { Write-Host "Zip archive     : $ZipPath" }
