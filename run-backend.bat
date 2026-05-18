@echo off
REM Start backend only on custom port 8055

setlocal

if "%API_PORT%"=="" set API_PORT=8055
if "%BACKEND_PORT%"=="" set BACKEND_PORT=%API_PORT%

cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

echo Starting backend on http://localhost:%BACKEND_PORT%
python -m uvicorn src.api.app:app --host 0.0.0.0 --port %BACKEND_PORT% --reload --reload-dir src

endlocal
