@echo off
REM Start Celery worker for async task processing

setlocal

cd /d "%~dp0"

echo ========================================
echo Starting Celery Worker
echo ========================================
echo.

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ".venv\Scripts\activate.bat"
) else (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Set Python path
set PYTHONPATH=%cd%

REM Check if Redis is accessible
echo Checking Redis connection...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo WARNING: Redis is not running!
    echo Celery worker requires Redis to be running on localhost:6379
    echo.
    echo Please start Redis first:
    echo   - On WSL: sudo service redis-server start
    echo   - Or run Redis in Docker
    echo   - Or install Redis for Windows
    echo.
    pause
    exit /b 1
) else (
    echo Redis is running - OK
)

echo.
echo Starting Celery worker...
echo Queues: document_processing, batch_processing, reprocessing
echo.
echo Press Ctrl+C to stop
echo.

python -m celery -A src.queue.celery_app worker ^
  --loglevel INFO ^
  --concurrency 4 ^
  --hostname worker@%%h ^
  --pool prefork ^
  --max-tasks-per-child 100 ^
  --max-memory-per-child 512000 ^
  --prefetch-multiplier 1 ^
  --queues document_processing,batch_processing,reprocessing ^
  --events

endlocal