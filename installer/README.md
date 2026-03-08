# Windows Installer Build

This folder contains packaging assets to build a distributable Windows installer.

## Prerequisites

- Windows 10/11
- Python 3.8+
- Inno Setup 6 (provides `ISCC.exe`)

Install Inno Setup with winget:

```powershell
winget install JRSoftware.InnoSetup --accept-package-agreements --accept-source-agreements
```

## Build Command

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\installer\build_installer.ps1
```

Fast rebuild options:

```powershell
# Reuse installed deps
powershell -ExecutionPolicy Bypass -File .\installer\build_installer.ps1 -SkipDependencyInstall

# Only rebuild setup.exe from existing dist\BingSearchAutomate bundle
powershell -ExecutionPolicy Bypass -File .\installer\build_installer.ps1 -SkipDependencyInstall -SkipPyInstaller
```

## Output

- App bundle: `dist\BingSearchAutomate\`
- Installer: `dist\installer\BingSearchAutomate-Setup-<version>.exe`

## Notes

- The installer is per-user (`%LOCALAPPDATA%\Programs\BingSearchAutomate`) and does not require admin rights.
- Runtime data (database, logs, storage state) is written to `%APPDATA%\BingSearchAutomate-Headless`.
- Playwright launches the installed Microsoft Edge channel by default (`browser.channel: msedge` in `config.yaml`).
