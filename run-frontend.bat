@echo off
REM Start frontend only on custom port 3055

setlocal

if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=3055
if "%BACKEND_PORT%"=="" set BACKEND_PORT=8055
set NEXT_PUBLIC_API_URL=http://localhost:%BACKEND_PORT%
set BACKEND_URL=http://localhost:%BACKEND_PORT%
set PORT=%FRONTEND_PORT%

cd /d "%~dp0frontend"

echo Starting frontend on http://localhost:%FRONTEND_PORT%
echo Proxying API to http://localhost:%BACKEND_PORT%
call npm run dev -- --port %FRONTEND_PORT%

endlocal
