@echo off
REM ============================================================
REM  PDF Document Extraction System - Local launcher
REM  Custom ports (to avoid collisions with default 8000/3000)
REM    Backend (FastAPI):  http://localhost:8055
REM    Frontend (Next.js): http://localhost:3055
REM ============================================================

setlocal

REM ---- Port configuration (override at the command line if desired) ----
if "%API_PORT%"=="" set API_PORT=8055
if "%BACKEND_PORT%"=="" set BACKEND_PORT=%API_PORT%
if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=3055
set NEXT_PUBLIC_API_URL=http://localhost:%BACKEND_PORT%
set BACKEND_URL=http://localhost:%BACKEND_PORT%

cd /d "%~dp0"

REM ---- Activate venv if present ----
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

echo.
echo ============================================================
echo  Starting PDF Document Extraction System
echo  Backend  : http://localhost:%BACKEND_PORT%
echo  Frontend : http://localhost:%FRONTEND_PORT%
echo  API Docs : http://localhost:%BACKEND_PORT%/docs
echo ============================================================
echo.

python main.py

endlocal
