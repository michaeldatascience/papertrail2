@echo off
REM Start Next.js frontend development server

setlocal

REM Default to port 3000
if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=3000

cd /d "%~dp0"

echo ========================================
echo Starting Frontend Development Server
echo ========================================
echo.

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo ERROR: frontend/node_modules not found!
    echo Please run: cd frontend ^&^& npm install
    pause
    exit /b 1
)

cd frontend

echo Starting frontend on http://localhost:%FRONTEND_PORT%
echo.
echo Pages available:
echo   http://localhost:%FRONTEND_PORT%          - Dashboard
echo   http://localhost:%FRONTEND_PORT%/schemas  - Schema Browser
echo   http://localhost:%FRONTEND_PORT%/documents - Documents
echo   http://localhost:%FRONTEND_PORT%/tasks    - Task Queue
echo.
echo Press Ctrl+C to stop
echo.

npm run dev -- --port %FRONTEND_PORT%

endlocal