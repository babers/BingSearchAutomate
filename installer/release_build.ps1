param(
    [string]$Version,
    [ValidateSet('major', 'minor', 'patch')]
    [string]$Bump = 'patch',
    [switch]$SkipDependencyInstall,
    [switch]$SkipSanityCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$versionFile = Join-Path $projectRoot 'version.py'

function Get-NextVersion {
    param(
        [int]$Major,
        [int]$Minor,
        [int]$Patch,
        [string]$BumpType
    )

    switch ($BumpType) {
        'major' { return "{0}.0.0" -f ($Major + 1) }
        'minor' { return "{0}.{1}.0" -f $Major, ($Minor + 1) }
        default { return "{0}.{1}.{2}" -f $Major, $Minor, ($Patch + 1) }
    }
}

Push-Location $projectRoot

try {
    if (-not (Test-Path $versionFile)) {
        throw "version.py not found at: $versionFile"
    }

    $versionContent = Get-Content $versionFile -Raw
    if ($versionContent -notmatch '__version__\s*=\s*"(\d+)\.(\d+)\.(\d+)"') {
        throw 'Could not parse current __version__ from version.py'
    }

    $currentVersion = $Matches[0] -replace '.*"', '' -replace '"$', ''
    $major = [int]$Matches[1]
    $minor = [int]$Matches[2]
    $patch = [int]$Matches[3]

    $targetVersion = $Version
    if (-not $targetVersion) {
        $targetVersion = Get-NextVersion -Major $major -Minor $minor -Patch $patch -BumpType $Bump
    }

    if ($targetVersion -notmatch '^\d+\.\d+\.\d+$') {
        throw "Invalid version format '$targetVersion'. Use semantic version format like 2.1.0"
    }

    $parts = $targetVersion.Split('.')
    $newMajor = [int]$parts[0]
    $newMinor = [int]$parts[1]
    $newPatch = [int]$parts[2]

    $updatedContent = $versionContent
    $updatedContent = [regex]::Replace(
        $updatedContent,
        '__version__\s*=\s*"[^"]+"',
        ('__version__ = "{0}"' -f $targetVersion)
    )
    $updatedContent = [regex]::Replace(
        $updatedContent,
        '__version_info__\s*=\s*\([^\)]*\)',
        ('__version_info__ = ({0}, {1}, {2})' -f $newMajor, $newMinor, $newPatch)
    )

    if ($updatedContent -ne $versionContent) {
        Set-Content -Path $versionFile -Value $updatedContent -NoNewline
    }

    Write-Host "Version updated: $currentVersion -> $targetVersion" -ForegroundColor Cyan

    if (-not $SkipSanityCheck) {
        Write-Host 'Running sanity compile check...' -ForegroundColor Yellow
        python -m py_compile main.py config.py browser_controller.py
    }

    $buildArgs = @(
        '-ExecutionPolicy', 'Bypass',
        '-File', (Join-Path $scriptDir 'build_installer.ps1')
    )
    if ($SkipDependencyInstall) {
        $buildArgs += '-SkipDependencyInstall'
    }

    Write-Host 'Building installer...' -ForegroundColor Yellow
    powershell @buildArgs

    $today = Get-Date -Format 'yyyy-MM-dd'
    $releaseNotesDir = Join-Path $projectRoot 'dist\release-notes'
    New-Item -ItemType Directory -Path $releaseNotesDir -Force | Out-Null

    $latestTag = $null
    try {
        $latestTag = (git describe --tags --abbrev=0 2>$null)
    } catch {
        $latestTag = $null
    }

    $changes = @()
    if ($latestTag) {
        $changes = @(git log "$latestTag..HEAD" --pretty=format:"- %h %s" 2>$null)
    }
    if (-not $changes -or $changes.Count -eq 0) {
        $changes = @(git log -n 20 --pretty=format:"- %h %s" 2>$null)
    }
    if (-not $changes -or $changes.Count -eq 0) {
        $changes = @('- No commit history available')
    }

    $installerFile = "dist\\installer\\BingSearchAutomate-Setup-$targetVersion.exe"
    $notesPath = Join-Path $releaseNotesDir "RELEASE_NOTES_v$targetVersion.md"

    $releaseNotes = @"
# BingSearchAutomate v$targetVersion Release Notes

Date: $today
Version: $targetVersion
Installer: $installerFile

## Highlights
- Add key release highlights here.

## Included Changes
$($changes -join "`r`n")

## Validation Checklist
- [ ] Installer launches successfully on a clean Windows user account
- [ ] App starts from Start Menu shortcut
- [ ] Runtime files are created under `%APPDATA%\\BingSearchAutomate-Headless`
- [ ] Basic search workflow verified

## Known Issues
- Add known issues or write `None`.
"@

    Set-Content -Path $notesPath -Value $releaseNotes -NoNewline

    Write-Host "Release notes template created: $notesPath" -ForegroundColor Green
    Write-Host "Release build complete: dist\\installer\\BingSearchAutomate-Setup-$targetVersion.exe" -ForegroundColor Green
}
finally {
    Pop-Location
}
