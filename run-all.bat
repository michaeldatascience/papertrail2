@echo off
REM Start all services in separate terminals

setlocal

cd /d "%~dp0"

echo ========================================
echo Starting All Services
echo ========================================
echo.

REM Check Redis first
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo WARNING: Redis is not running!
    echo Worker will fail to start without Redis.
    echo Run 'run-redis-check.bat' for setup instructions.
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i not "%CONTINUE%"=="y" exit /b 1
)

echo Starting services in separate terminals...
echo.

REM Start backend in new terminal
echo [1/3] Starting Backend API (port 8000)...
start "Backend API" cmd /k run-backend.bat

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new terminal
echo [2/3] Starting Frontend (port 3000)...
start "Frontend" cmd /k run-frontend.bat

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start worker in new terminal (optional - only if Redis is running)
redis-cli ping >nul 2>&1
if not errorlevel 1 (
    echo [3/3] Starting Celery Worker...
    start "Celery Worker" cmd /k run-worker.bat
) else (
    echo [3/3] Skipping Celery Worker (Redis not available)
)

echo.
echo ========================================
echo All services starting...
echo ========================================
echo.
echo Backend API: http://localhost:8000/docs
echo Frontend:    http://localhost:3000
echo.
echo To stop all services:
echo   Close each terminal window or press Ctrl+C in each
echo.
echo Check individual terminals for service status
echo.

pause

endlocal