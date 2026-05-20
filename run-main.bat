@echo off
REM Run main.py unified launcher

setlocal

cd /d "%~dp0"

echo ========================================
echo Papertrail2 Main Launcher
echo ========================================
echo.

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ".venv\Scripts\activate.bat"
) else (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then install: pip install -e ".[dev]"
    pause
    exit /b 1
)

REM Set Python path
set PYTHONPATH=%cd%

if "%~1"=="" (
    echo Starting web app (backend + frontend)...
    echo.
    echo Note: This uses ports 8055 (backend) and 3055 (frontend)
    echo For ports 8000/3000, use run-all.bat instead
    echo.
    python main.py
) else (
    python main.py %*
)

pause

endlocal