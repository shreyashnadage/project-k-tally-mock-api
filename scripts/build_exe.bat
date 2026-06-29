@echo off
setlocal enabledelayedexpansion
title Tally Simulator - Build Exe

echo ============================================================
echo  Tally Data Simulator - Windows Installer Build
echo ============================================================
echo.

cd /d "%~dp0.."
set ROOT=%CD%

:: ── 1. Build React frontend ───────────────────────────────────────────────
echo [1/4] Building React frontend...
cd "%ROOT%\frontend"
call npm install --silent
call npm run build
if %ERRORLEVEL% neq 0 (
    echo ERROR: Frontend build failed
    exit /b 1
)
echo       Done: frontend\dist\ ready
echo.

cd "%ROOT%"

:: ── 2. PyInstaller ────────────────────────────────────────────────────────
echo [2/4] Bundling with PyInstaller...
if exist "dist\TallySimulator" rmdir /s /q "dist\TallySimulator"
.venv\Scripts\pyinstaller tally_simulator.spec --clean --noconfirm
if %ERRORLEVEL% neq 0 (
    echo ERROR: PyInstaller failed
    exit /b 1
)
echo       Done: dist\TallySimulator\ ready
echo.

:: ── 3. Quick smoke test ───────────────────────────────────────────────────
echo [3/4] Smoke testing the exe...
start /B "" "dist\TallySimulator\TallySimulator.exe" > nul 2>&1
timeout /t 6 /nobreak > nul
curl -s --max-time 5 http://localhost:9001/api/health > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo WARNING: Smoke test failed - exe may not start correctly
    echo          Check dist\TallySimulator\TallySimulator.exe manually
) else (
    echo       OK: http://localhost:9001/api/health responded
)
taskkill /F /IM TallySimulator.exe > nul 2>&1
timeout /t 2 /nobreak > nul
echo.

:: ── 4. Inno Setup installer ───────────────────────────────────────────────
echo [4/4] Creating installer with Inno Setup...
set ISCC=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if exist "C:\Program Files\Inno Setup 6\ISCC.exe"       set ISCC=C:\Program Files\Inno Setup 6\ISCC.exe

if "!ISCC!"=="" (
    echo       Inno Setup not found - skipping installer step
    echo       The portable bundle is at: dist\TallySimulator\
) else (
    "%ISCC%" installer\setup.iss
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Inno Setup failed
        exit /b 1
    )
    echo       Done: dist\TallySimulator-Setup.exe ready
)

echo.
echo ============================================================
echo  Build complete!
echo.
echo  Portable bundle : dist\TallySimulator\TallySimulator.exe
if not "!ISCC!"=="" (
echo  Installer       : dist\TallySimulator-Setup.exe
)
echo ============================================================
