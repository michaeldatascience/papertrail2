@echo off
REM Check Redis status and provide setup instructions

setlocal

echo ========================================
echo Redis Status Check
echo ========================================
echo.

REM Check if Redis is accessible
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo Redis is NOT running!
    echo.
    echo To start Redis:
    echo.
    echo Option 1 - WSL (Recommended):
    echo   1. Open WSL terminal
    echo   2. Run: sudo service redis-server start
    echo   3. Verify: redis-cli ping
    echo.
    echo Option 2 - Docker:
    echo   docker run -d -p 6379:6379 redis:latest
    echo.
    echo Option 3 - Windows Native:
    echo   Download from: https://github.com/microsoftarchive/redis/releases
    echo.
    echo Option 4 - Skip Redis (limited functionality):
    echo   The app will work without Redis but async uploads won't function
    echo.
) else (
    echo Redis is running - OK
    echo.
    echo Testing connection...
    redis-cli ping
    echo.
    echo Redis info:
    redis-cli info server | findstr redis_version
    redis-cli info server | findstr tcp_port
)

echo.
pause

endlocal