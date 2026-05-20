@echo off
REM Check if environment is properly set up

setlocal

cd /d "%~dp0"

echo ========================================
echo Environment Setup Check
echo ========================================
echo.

echo Checking Python...
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python not found in PATH!
    goto :failed
) else (
    echo Python - OK
)

echo.
echo Checking Node.js...
node --version 2>nul
if errorlevel 1 (
    echo ERROR: Node.js not found in PATH!
    goto :failed
) else (
    echo Node.js - OK
)

echo.
echo Checking npm...
npm --version 2>nul
if errorlevel 1 (
    echo ERROR: npm not found in PATH!
    goto :failed
) else (
    echo npm - OK
)

echo.
echo Checking virtual environment...
if exist ".venv\Scripts\activate.bat" (
    echo Virtual environment - OK
) else (
    echo WARNING: Virtual environment not found
    echo Run: python -m venv .venv
)

echo.
echo Checking frontend dependencies...
if exist "frontend\node_modules" (
    echo Frontend node_modules - OK
) else (
    echo WARNING: Frontend dependencies not installed
    echo Run: cd frontend ^&^& npm install
)

echo.
echo Checking Redis (optional)...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo Redis - NOT RUNNING (optional for basic usage)
) else (
    echo Redis - OK
)

echo.
echo Checking .env file...
if exist ".env" (
    echo .env file - OK
    
    REM Check for OpenRouter key
    findstr /C:"OPENROUTER_API_KEY" .env >nul
    if not errorlevel 1 (
        findstr /C:"YOUR_OPENROUTER_API_KEY_HERE" .env >nul
        if not errorlevel 1 (
            echo WARNING: OpenRouter API key not set!
            echo Get your key from: https://openrouter.ai/keys
        ) else (
            echo OpenRouter API key - CONFIGURED
        )
    )
) else (
    echo WARNING: .env file not found!
)

echo.
echo ========================================
echo Setup check complete
echo ========================================
echo.

pause
exit /b 0

:failed
echo.
echo Setup check FAILED - Please install missing dependencies
echo.
pause
exit /b 1

endlocal