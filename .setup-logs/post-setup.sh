#!/usr/bin/env bash
set -e
ROOT="$(pwd)"
PIP_PID="$(cat .setup-logs/pip-install.pid 2>/dev/null || true)"
NPM_PID="$(cat .setup-logs/npm-install.pid 2>/dev/null || true)"
if [ -n "$PIP_PID" ]; then
  while kill -0 "$PIP_PID" 2>/dev/null; do sleep 10; done
fi
if [ -n "$NPM_PID" ]; then
  while kill -0 "$NPM_PID" 2>/dev/null; do sleep 5; done
fi
. .venv/bin/activate
python -m pip --version
python -c "import fastapi, pydantic, openai, PIL, fitz, cv2; print('backend-imports-ok')"
python main.py --check || true
cd frontend
npm run build || true
