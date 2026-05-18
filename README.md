# Papertrail2 / Local Document Extraction System

This is the **working-root documentation** for the repo as it exists in code after local repair and bring-up.

All pre-existing documentation files were moved under [`docs/`](./docs/). In particular:
- original top-level README → [`docs/UPSTREAM_README.md`](./docs/UPSTREAM_README.md)
- enterprise guide → [`docs/ENTERPRISE_GUIDE.md`](./docs/ENTERPRISE_GUIDE.md)
- setup repair notes → [`docs/SETUP_REPAIR_NOTES.md`](./docs/SETUP_REPAIR_NOTES.md)

This file is intentionally different: it documents **our observed understanding of the codebase**, how to set it up, how to run it, what had to be fixed to make it boot, and how to debug it.

---

## 1. What this repo is, based on the code

Observed from `main.py`, `src/api`, `src/pipeline`, `src/agents`, `src/preprocessing`, `src/export`, and the Next.js frontend:

### Core purpose
This repo is a **local-first AI document extraction system**.

It combines:
- a **Python backend**
- a **FastAPI API**
- a **CLI entry point**
- a **Next.js frontend**
- a **local VLM backend**, expected to be **LM Studio** on `http://127.0.0.1:1234` / `http://localhost:1234`

### Main runtime surfaces
From `main.py` and `src/api/routes/*`, there are three practical ways to use it:
1. **Web app** — backend + frontend
2. **CLI extraction** — `python main.py extract ...`
3. **Batch mode** — `python main.py batch ...`

### Main code areas
- `main.py` — unified runner for web, CLI, batch, config
- `src/api/` — FastAPI app and routes
- `src/agents/` — analyzer/extractor/validator/orchestrator and related agent logic
- `src/pipeline/` — pipeline orchestration and state
- `src/preprocessing/` — PDF/image/doc/document preparation
- `src/schemas/` — extraction schemas
- `src/export/` — JSON / Excel / Markdown / FHIR-related export code
- `src/security/` — auth, audit, encryption, PHI masking, path validation
- `src/queue/` — Celery/Redis optional async processing support
- `frontend/` — Next.js frontend

### Document/file formats observed in code
From `src/preprocessing/__init__.py` and `src/api/routes/documents.py`, the code is built to handle more than PDF.

Observed supported formats:
- PDF
- PNG / JPG / JPEG / TIFF / TIF / BMP
- DOCX / DOC
- XLSX / CSV
- DICOM (`.dcm`, `.dicom`)
- EDI / X12 (`.edi`, `.x12`, `.835`, `.837`)

### Schemas observed in code
From `src/schemas/`:
- bank statement
- CMS-1500
- EOB
- form 1099
- invoice
- superbill
- UB-04
- W-2
- generic fallback / enhanced generic

### Frontend features observed in code
From `frontend/src/app` and components:
- dashboard
- schemas browser
- documents list / upload / detail page
- tasks / queue monitoring
- health page
- login / signup pages
- source/provenance viewer for extracted fields

### Backend features observed in code
From routes and modules:
- auth endpoints
- health endpoints
- document upload / process / preview endpoints
- schema listing / schema inspection endpoints
- dashboard metrics endpoints
- queue / task endpoints
- webhooks
- audit/security middleware
- optional multi-tenant plumbing

---

## 2. What we had to do to make this repo work locally

This repo did **not** come up cleanly as-is in the current checkout.

The most important issues found and repaired are documented in detail in:
- [`docs/SETUP_REPAIR_NOTES.md`](./docs/SETUP_REPAIR_NOTES.md)

Short version:
- installed missing Python and frontend dependencies
- fixed WSL/Linux-unfriendly dependency checks in `main.py`
- fixed frontend/backend local config mismatch
- fixed dev CORS behavior so browser requests from `127.0.0.1:3000` can reach the backend
- added missing frontend support files under `frontend/src/lib/`
- added missing backend modules under `src/client/backends/`
- added missing profile registry modules under `src/profiles/`
- patched multi-record LM request formatting to improve JSON behavior

Important: some of these were **repairs/compatibility layers**, not necessarily the author's original intended implementation.

---

## 3. External dependencies you need

## Required

### Python
- Python **3.11+**
- tested here with **3.12.3**

### Node
- Node **18+**
- tested here with **20.20.1**

### npm
- required for frontend install and dev server

### LM Studio
Required for extraction behavior.

Observed expected API endpoint in code:
- `http://localhost:1234/v1`

In practice we used:
- `http://127.0.0.1:1234`

### Redis
Optional for queue-oriented features.
- queue/task routes degrade reasonably if Redis is unavailable
- some queue pages still expect queue endpoints to exist

## Optional / feature-specific
Depending on code path and features you use:
- Celery workers
- PHI-related extras
- observability extras
- FHIR extras

---

## 4. Local setup instructions

These instructions reflect the working repaired setup.

## A. Clone and enter repo
```bash
git clone <repo-url>
cd papertrail2
```

## B. Create virtualenv
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## C. Install Python packages
Recommended:
```bash
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
```

If that is too heavy or problematic, the repo can still be made to boot with a more targeted install set, but `.[dev]` is the cleanest intended path.

## D. Install frontend packages
```bash
cd frontend
npm install
cd ..
```

## E. Create frontend local env
Working value used here:
```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_AUTH_ENABLED=true
NEXT_PUBLIC_ENABLE_BATCH_UPLOAD=true
NEXT_PUBLIC_ENABLE_REAL_TIME_UPDATES=true
```

## F. Create/update backend `.env`
This repo currently includes a tracked `.env` in this branch. If you are recreating manually, at minimum ensure:
- LM Studio base URL points to your running instance
- backend port matches where you actually launch FastAPI
- secrets are set appropriately for your environment

## G. Start LM Studio
You need LM Studio running with a model loaded.

Observed/default model references in code/config:
- `qwen/qwen3-vl-8b`

### Important LM Studio note
From actual runtime testing, the extraction path behaves poorly if the effective context is too small.

Recommended:
- context window: **8192 minimum**
- **32768 preferred** if available

If LM Studio effectively runs at around `4096`, parts of the pipeline can fail with:
- request/context overflow
- malformed or truncated JSON

---

## 5. How to run

## Preflight check
```bash
source .venv/bin/activate
python main.py --check
```

## Run backend + frontend
```bash
source .venv/bin/activate
python main.py
```

Expected:
- backend on `http://127.0.0.1:8000` or `http://localhost:8000`
- frontend on `http://127.0.0.1:3000` or `http://localhost:3000`

## Run backend only
```bash
source .venv/bin/activate
python main.py --backend
```

## Run frontend only
```bash
cd frontend
npm run dev -- --port 3000
```

## CLI extract
```bash
source .venv/bin/activate
python main.py extract path/to/file.pdf
```

Optional example:
```bash
python main.py extract path/to/file.pdf --output outdir --no-excel --no-markdown
```

## Batch mode
```bash
source .venv/bin/activate
python main.py batch path/to/folder --parallel 4
```

---

## 6. How the app behaves at runtime

## Backend
Observed launch target in code:
- FastAPI app: `src.api.app:app`

Useful backend URLs:
- health: `http://127.0.0.1:8000/api/v1/health`
- docs: `http://127.0.0.1:8000/docs`
- schemas: `http://127.0.0.1:8000/api/v1/schemas`

## Frontend
Useful pages:
- `/`
- `/dashboard`
- `/schemas`
- `/documents`
- `/documents/upload`
- `/tasks`
- `/health`

---

## 7. How to debug

## A. Start with preflight
```bash
python main.py --check
```
If this fails, fix install/config before debugging deeper runtime behavior.

## B. Test backend health directly
```bash
python3 - <<'PY'
import urllib.request
with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=10) as r:
    print(r.status)
    print(r.read().decode()[:500])
PY
```

## C. Test LM Studio directly
```bash
python3 - <<'PY'
import urllib.request
with urllib.request.urlopen('http://127.0.0.1:1234/v1/models', timeout=10) as r:
    print(r.status)
    print(r.read().decode()[:500])
PY
```

## D. Watch frontend logs
```bash
cd frontend
npm run dev -- --port 3000
```
If the page compiles but shows no data, check:
- browser devtools network tab
- backend CORS/origin config
- `frontend/.env.local`

## E. Watch backend logs
The code writes logs under `logs/` and additional local bring-up logs may exist under `.setup-logs/`.

Useful checks:
```bash
tail -f logs/extraction_*.log
```
or
```bash
tail -f .setup-logs/backend.log
```

## F. Validate a specific endpoint manually
Example:
```bash
python3 - <<'PY'
import urllib.request
with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/schemas', timeout=10) as r:
    print(r.status)
    print(r.read().decode()[:1000])
PY
```

## G. Debug extraction with a tiny test PDF
A small smoke test is useful before running on large real documents.

Observed locally, extraction can fail for two separate reasons:
1. code/runtime/import issues
2. LM Studio/model behavior issues

If the app boots but extraction quality is poor, inspect LM Studio context/model settings first.

---

## 8. Known observed problems

These are based on actual bring-up/testing of the current branch.

### 1. LM output instability
Even with runtime repairs, the model can still produce:
- malformed JSON
- truncated JSON
- low-confidence / empty extraction output

This is especially visible in multi-record mode.

### 2. Context window pressure
Several VLM requests in the pipeline exceed an effective context limit when LM Studio is configured too tightly.

### 3. Frontend/backend depth mismatch
The frontend expects a richer persisted document/task world than the backend fully guarantees in all code paths.

Result:
- some pages work well for live/static endpoints like `/schemas`
- others are only partially useful unless more persistence/state plumbing is completed

### 4. Queue/task UX is optional-path sensitive
The code degrades when Redis/Celery are unavailable, but some task/queue UI flows are much more meaningful if those services are actually running.

---

## 9. Observed feature summary

Based on code inspection and runtime tests, the repo currently contains:
- local VLM-based extraction via LM Studio
- CLI + web entry points
- FastAPI backend with multiple document-related APIs
- schema-based extraction support
- preprocessing for many input document/image formats
- export support for JSON / Excel / Markdown and FHIR-related paths
- security-related middleware and helpers
- queue/webhook plumbing
- Next.js UI with dashboards, schema browser, document flows, and provenance/source-view components

---

## 10. WSL-specific notes

This repo was brought up from a path under `/mnt/e/...`.

That works, but for better performance you may prefer moving the repo into the native WSL filesystem, e.g.:
```bash
~/code/papertrail2
```

Why:
- faster Node/Next.js file operations
- faster Python venv access
- fewer watcher/cache oddities

---

## 11. Recommended bring-up checklist

1. Start LM Studio and load the intended vision model
2. Ensure LM Studio context is sufficiently large
3. `source .venv/bin/activate`
4. `python main.py --check`
5. `python main.py`
6. open `http://127.0.0.1:3000/schemas`
7. verify `http://127.0.0.1:8000/api/v1/health`
8. only then test extraction

---

## 12. If you want the full repair history
See:
- [`docs/SETUP_REPAIR_NOTES.md`](./docs/SETUP_REPAIR_NOTES.md)

That file contains the repair-focused history: issues found, stubs added, and exact classes of changes made to get the repo working.
