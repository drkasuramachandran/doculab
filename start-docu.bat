@echo off
title DocuLab Server
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 pause & exit /b 1
)

call ".venv\Scripts\activate.bat"

if not exist "frontend\node_modules" (
    echo Installing frontend packages...
    pushd frontend
    call npm install
    popd
)

echo Starting DocuLab...
start "DocuLab Frontend" cmd /k "cd /d %~dp0frontend && npm run dev -- --open"

python -m uvicorn backend.app.main:app --reload

pause
