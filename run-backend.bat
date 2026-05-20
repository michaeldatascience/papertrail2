@echo off
REM Start backend API server

setlocal

REM Default to port 8000 (matching current setup)
if "%API_PORT%"=="" set API_PORT=8000
if "%BACKEND_PORT%"=="" set BACKEND_PORT=%API_PORT%

cd /d "%~dp0"

echo ========================================
echo Starting Backend API Server
echo ========================================
echo.

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ".venv\Scripts\activate.bat"
) else (
    echo WARNING: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then install dependencies: pip install -e ".[dev]"
    pause
    exit /b 1
)

REM Set Python path
set PYTHONPATH=%cd%

echo Starting backend on http://localhost:%BACKEND_PORT%
echo.
echo API docs will be available at:
echo   http://localhost:%BACKEND_PORT%/docs
echo   http://localhost:%BACKEND_PORT%/api/v1/health
echo.
echo Press Ctrl+C to stop
echo.

python -m uvicorn src.api.app:app --host 0.0.0.0 --port %BACKEND_PORT% --reload --reload-dir src

endlocal
