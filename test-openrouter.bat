@echo off
REM Test OpenRouter integration

setlocal

cd /d "%~dp0"

echo ========================================
echo Testing OpenRouter Integration
echo ========================================
echo.

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ".venv\Scripts\activate.bat"
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

REM Set Python path
set PYTHONPATH=%cd%

echo Running OpenRouter test...
echo.

python test_openrouter.py

echo.
pause

endlocal