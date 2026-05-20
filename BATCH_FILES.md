# Batch Files Guide

This directory contains Windows batch files for easy terminal-based startup of all services.

## Quick Start

1. **Check Setup**: `check-setup.bat` - Verify environment is ready
2. **Run Everything**: `run-all.bat` - Start all services in separate terminals
3. **Test OpenRouter**: `test-openrouter.bat` - Verify cloud VLM integration

## Individual Services

### Core Services
- `run-backend.bat` - Start backend API only (port 8000)
- `run-frontend.bat` - Start frontend only (port 3000)
- `run-worker.bat` - Start Celery worker (requires Redis)

### Utilities
- `run-redis-check.bat` - Check Redis status and setup help
- `check-setup.bat` - Verify Python, Node, dependencies
- `test-openrouter.bat` - Test OpenRouter/cloud VLM connection

### Document Processing
- `extract-document.bat` - CLI document extraction
  ```
  extract-document.bat invoice.pdf --schema invoice
  ```

### Alternative Launcher
- `run-main.bat` - Use original main.py launcher (ports 8055/3055)

## Typical Usage

### First Time Setup
```batch
check-setup.bat
```

### Development (Recommended)
```batch
run-all.bat
```
This opens 3 terminals:
- Backend API (http://localhost:8000)
- Frontend (http://localhost:3000)
- Celery Worker (if Redis is running)

### Backend Only
```batch
run-backend.bat
```

### Frontend Only
```batch
run-frontend.bat
```

### Test Document Extraction
```batch
extract-document.bat sample.pdf --schema invoice
```

## Port Configuration

Default ports:
- Backend: 8000
- Frontend: 3000

To use different ports:
```batch
set API_PORT=8080
set FRONTEND_PORT=3001
run-all.bat
```

## Troubleshooting

### "Virtual environment not found"
Run:
```batch
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

### "Redis is not running"
- Option 1: Use WSL - `wsl sudo service redis-server start`
- Option 2: Install Redis for Windows
- Option 3: Run without Redis (limited functionality)

### "npm not found"
Install Node.js from https://nodejs.org/

### Port already in use
Check what's using the port:
```batch
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

## Notes

- All batch files change to the repo directory automatically
- Each service runs in its own terminal window
- Press Ctrl+C in any terminal to stop that service
- Close terminal windows to fully stop services