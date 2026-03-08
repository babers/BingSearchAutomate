param(
    [switch]$SkipDependencyInstall,
    [switch]$SkipPyInstaller
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Push-Location $projectRoot

try {
    $python = 'python'

    if (-not $SkipDependencyInstall) {
        & $python -m pip install --upgrade pip
        & $python -m pip install -r requirements.txt
        & $python -m pip install pyinstaller
    }

    if (-not $SkipPyInstaller) {
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$projectRoot\build"
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$projectRoot\dist\BingSearchAutomate"

        & $python -m PyInstaller --noconfirm --clean "$projectRoot\installer\BingSearchAutomate.spec"
    }

    $versionContent = Get-Content "$projectRoot\version.py" -Raw
    if ($versionContent -notmatch '__version__\s*=\s*"([^"]+)"') {
        throw 'Could not parse __version__ from version.py'
    }
    $appVersion = $Matches[1]

    $iscc = $null
    $isccFromPath = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($isccFromPath) {
        $iscc = $isccFromPath.Source
    }

    if (-not $iscc) {
        $isccCandidates = @(
            "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
            "$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
            "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
        )
        $iscc = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    }

    if (-not $iscc) {
        throw @'
Inno Setup 6 is required to create the installer.

Install options:
  winget install JRSoftware.InnoSetup
  or download from https://jrsoftware.org/isinfo.php

After installation, re-run:
  powershell -ExecutionPolicy Bypass -File .\installer\build_installer.ps1
'@
    }

    & $iscc "/DMyAppVersion=$appVersion" "/DSourceRoot=$projectRoot" "$projectRoot\installer\BingSearchAutomate.iss"

    Write-Host "Installer created under dist\installer" -ForegroundColor Green
}
finally {
    Pop-Location
}
