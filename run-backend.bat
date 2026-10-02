@echo off
title DocuLab Backend
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo DocuLab .venv was not found.
  echo Create it with: python -m venv .venv
  pause
  exit /b 1
)
call ".venv\Scripts\activate.bat"
python -m uvicorn backend.app.main:app --reload
pause
