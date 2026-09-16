@echo off
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
  echo Please install Python 3 first. See README.md.
  pause
  exit /b 1
)
py -3 scripts\build.py
if errorlevel 1 (
  pause
  exit /b 1
)
py -3 scripts\serve.py
pause
