#!/usr/bin/env bash
set -e
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e . --no-deps
python -m pip install \
  'fastapi>=0.115.0' 'uvicorn[standard]>=0.32.0' 'python-multipart>=0.0.17' 'starlette>=0.41.0' \
  'pydantic>=2.10.0' 'pydantic-settings>=2.6.0' \
  'langchain>=1.0.0' 'langchain-core>=0.3.25' 'langchain-community>=0.3.12' 'langchain-openai>=0.2.14' \
  'langgraph>=0.2.60' 'langgraph-checkpoint>=2.0.10' 'langgraph-checkpoint-sqlite>=2.0.0' 'langsmith>=0.1.0' \
  'openai>=1.55.0' 'tenacity>=9.0.0' 'httpx>=0.27.0' 'aiohttp>=3.11.0' \
  'PyMuPDF>=1.25.0' 'Pillow>=11.0.0' 'opencv-python>=4.10.0' 'numpy>=1.26.0' 'scikit-learn>=1.4.0' 'python-docx>=1.1.0' 'pydicom>=2.4.0' \
  'celery>=5.4.0' 'kombu>=5.4.0' 'redis>=5.2.0' \
  'cryptography>=43.0.0' 'python-jose[cryptography]>=3.3.0' 'passlib[bcrypt]>=1.7.4' 'bcrypt>=4.2.0' \
  'openpyxl>=3.1.5' 'pandas>=2.2.0' 'xlsxwriter>=3.2.0' \
  'prometheus-client>=0.21.0' 'structlog>=24.4.0' 'python-json-logger>=2.0.7' \
  'python-dotenv>=1.0.1' 'pyyaml>=6.0.0'
python - <<'PY'
mods=['fastapi','pydantic','openai','openpyxl','PIL','fitz','cv2','langgraph','langchain']
for m in mods:
    __import__(m)
print('core-imports-ok')
PY
python main.py --check
