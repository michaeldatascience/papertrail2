@echo off
REM Extract a document using CLI

setlocal

cd /d "%~dp0"

if "%~1"=="" (
    echo ========================================
    echo Document Extraction CLI
    echo ========================================
    echo.
    echo Usage: extract-document.bat [pdf-file] [options]
    echo.
    echo Examples:
    echo   extract-document.bat sample.pdf
    echo   extract-document.bat invoice.pdf --schema invoice
    echo   extract-document.bat document.pdf --output results/
    echo.
    echo Options:
    echo   --schema [name]   Use specific schema (invoice, w2, aadhaar_card, etc.)
    echo   --output [dir]    Output directory (default: ./output)
    echo   --no-excel        Skip Excel export
    echo   --no-markdown     Skip Markdown export
    echo.
    pause
    exit /b 1
)

echo ========================================
echo Extracting Document
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

echo Input file: %1
echo.

python main.py extract %*

echo.
pause

endlocal