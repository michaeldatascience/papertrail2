# Setup Repair Notes

## Purpose
This document records the issues found while bringing this repo up inside WSL under `/mnt/e/...`, the changes made to get it running, and the places where minimal/stub implementations were added to satisfy missing runtime dependencies.

---

## Environment context
- Host OS: Windows
- Dev environment: WSL + VS Code terminal
- Working directory: `/mnt/e/CODE/ADE/Agentic-Document-Extraction-PDF-main/Agentic-Document-Extraction-PDF-main`
- Target runtime used during repair:
  - Python: `3.12.3`
  - Node: `20.20.1`
  - npm: `10.8.2`
  - Backend: `http://127.0.0.1:8000`
  - Frontend: `http://127.0.0.1:3000`
  - LM Studio: `http://127.0.0.1:1234`

---

## High-level issues found

### 1. Incomplete Python environment
The repo was not installed into a working virtualenv in this terminal session. Several required runtime packages were missing, so `main.py --check` failed and the backend could not run cleanly.

### 2. Frontend dependencies not installed
`frontend/node_modules` was absent initially, so the Next.js app could not start.

### 3. Broken or WSL-unfriendly preflight checks
`main.py --check` had two practical issues:
- the npm check used a Windows-oriented subprocess style that was unreliable in WSL/Linux
- the backend dependency check tried to import `Pillow` by package name instead of importing `PIL`

### 4. Missing frontend source files
The frontend referenced modules that did not exist in the repo:
- `frontend/src/lib/api`
- `frontend/src/lib/api/provenance`
- `frontend/src/lib/utils`
- `frontend/src/lib/branding`

Without these, multiple frontend pages failed to compile or partially rendered.

### 5. Frontend/backend config drift
`frontend/.env.local` was pointing at a different backend/port family (`8055/3055`) while the active backend was launched on `8000`.

### 6. Backend CORS mismatch for dev hostnames
The frontend was opened from `127.0.0.1:3000`, while backend CORS behavior was effectively too narrow for the actual browser origin. This caused pages like `/schemas` to appear empty even though the backend endpoint itself returned valid data.

### 7. Missing backend runtime modules
The backend imported modules that were not present in the repo, causing extraction/runtime import failures. Missing areas included:
- `src.client.backends.*`
- `src.profiles.*`

### 8. Extraction pipeline runtime gaps
Even after booting the app, the extraction path still hit runtime gaps and model-behavior issues:
- missing backend abstraction pieces required by the agent stack
- missing profile registry expected by analyzer/schema overlay code
- multi-record extraction receiving malformed/truncated JSON from LM Studio
- many requests still exceeded the effective model context window in LM Studio

---

## Changes made

## A. Environment and installation changes

### Created Python virtualenv
- Path: `.venv/`

### Installed core backend dependencies
Installed enough backend dependencies to boot the API and run the pipeline far enough to test it.

### Installed frontend dependencies
- Ran `npm install` in `frontend/`

### Created/fixed frontend local env file
- File: `frontend/.env.local`
- Final API target set to:
  - `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`

### Started services
- Backend started with uvicorn
- Frontend started with Next.js dev server

---

## B. Source-code changes

### 1. `main.py`
#### Problem
Preflight checks were partially incorrect under WSL/Linux.

#### Change made
- Updated `check_npm()` to use cross-platform subprocess invocation
- Updated backend dependency check to import `PIL` instead of `Pillow`
- Updated install guidance text to point to venv-based editable install

#### Why
This made `python main.py --check` accurately reflect the real state of the local environment.

---

### 2. `src/api/app.py`
#### Problem
Dev CORS handling did not safely cover the browser origins actually being used (`127.0.0.1:3000`, `localhost:3000`, and old `3055` values).

#### Change made
Expanded dev-time CORS defaults/merge behavior to include:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:3055`
- `http://127.0.0.1:3055`

#### Why
This fixed frontend pages that loaded but could not consume backend API responses from the browser.

---

### 3. `frontend/.env.local`
#### Problem
Frontend local config pointed to an inconsistent backend target.

#### Change made
Rewrote it to:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_AUTH_ENABLED=true
NEXT_PUBLIC_ENABLE_BATCH_UPLOAD=true
NEXT_PUBLIC_ENABLE_REAL_TIME_UPDATES=true
```

#### Why
This aligned browser-side API requests with the actually running backend.

---

### 4. Added `frontend/src/lib/branding.ts`
#### Problem
Frontend imported `BRANDING`, but the file did not exist.

#### Change made
Added a minimal branding module exposing:
- `productName`
- `companyName`
- `versionLabel`
- `metaDescription`
- `docsUrl`

#### Why
Required for layout/header/source-view pages to compile.

#### Note
This is a minimal replacement, not necessarily the repo author's final intended branding system.

---

### 5. Added `frontend/src/lib/utils.ts`
#### Problem
Many frontend components imported `@/lib/utils`, but the file was missing.

#### Change made
Added utility helpers used by existing code, including:
- `cn`
- `generateId`
- `truncate`
- `formatFileSize`
- `formatDuration`
- `formatPercentage`
- `formatConfidence`
- `formatDateTime`
- `formatRelativeTime`
- `getConfidenceLevel`
- `getConfidenceColor`
- `getStatusText`
- `copyToClipboard`

#### Why
Required to unblock UI compilation across multiple pages/components.

#### Note
This is a practical compatibility implementation matching the existing frontend’s expectations.

---

### 6. Added `frontend/src/lib/api/index.ts`
#### Problem
Frontend imported `@/lib/api`, but no API client existed in the checked-out repo.

#### Change made
Added a lightweight browser API layer with:
- token helpers
- `ApiError`
- generic `apiFetch()` / blob download helpers
- `authApi`
- `healthApi`
- `dashboardApi`
- `tasksApi`
- `queueApi`
- `schemaApi`
- `documentsApi`
- `previewApi`
- `exportApi`

#### Why
Needed so pages such as `/schemas`, `/tasks`, `/documents`, `/login` could call backend endpoints.

#### Note
This is effectively a compatibility client. Some methods are intentionally lightweight/fallback-oriented because the backend does not yet persist all data needed by the frontend UX.

---

### 7. Added `frontend/src/lib/api/provenance.ts`
#### Problem
Document/source-view components imported provenance helpers that were missing.

#### Change made
Added:
- provenance types
- provenance fetch helper
- page/PDF URL builders
- empty-state helper

#### Why
Required by source-view related frontend components.

#### Note
This is a minimal support layer around backend provenance endpoints.

---

### 8. Added missing backend abstraction files under `src/client/backends/`
Files added:
- `src/client/backends/protocol.py`
- `src/client/backends/lm_studio_backend.py`
- `src/client/backends/factory.py`
- `src/client/backends/queue_depth.py`

#### Problem
The backend imported these modules but they were absent, causing extraction/runtime import errors.

#### Change made
Added minimal implementations for:
- VLM backend protocol/types
- LM Studio backend adapter
- backend factory selector
- process-local queue-depth semaphore helper

#### Why
These pieces were required by the current agent/client code path to import and run.

#### Note
These are **repair implementations** based on how the surrounding code already expected them to behave. They should be reviewed against the intended upstream design if a canonical source exists elsewhere.

---

### 9. Added missing profile files under `src/profiles/`
Files added:
- `src/profiles/__init__.py`
- `src/profiles/descriptor.py`

#### Problem
Analyzer and schema overlay code expected a profile system that was not present.

#### Change made
Added a minimal profile registry/detector supporting:
- `generic-document`
- `medical-rcm`
- `detect_profile()`
- `get_profile()`
- `ProfileDescriptor`
- `ProfileDetectionResult`

#### Why
Needed for analyzer/profile-overlay code to run without import failure.

#### Note
This is a **stub/minimal implementation**, not a full productized profile system.

---

### 10. `src/extraction/multi_record.py`
#### Problem
Multi-record extraction path was especially sensitive to malformed LM output. It retried, but still frequently received invalid/truncated JSON.

#### Change made
Updated `_send_vision_json()` to send a schema-style `response_format` payload when calling the LM client.

#### Why
Attempted to improve JSON stability for multi-record calls against LM Studio.

#### Result
This was only a partial mitigation. The model still returned malformed/truncated output in practice.

---

## Stub / minimal compatibility implementations added
These are the main places where the repo appeared incomplete and a minimal implementation was added so the system could run:

### Frontend compatibility layer
- `frontend/src/lib/branding.ts`
- `frontend/src/lib/utils.ts`
- `frontend/src/lib/api/index.ts`
- `frontend/src/lib/api/provenance.ts`

### Backend compatibility layer
- `src/client/backends/protocol.py`
- `src/client/backends/lm_studio_backend.py`
- `src/client/backends/factory.py`
- `src/client/backends/queue_depth.py`
- `src/profiles/__init__.py`
- `src/profiles/descriptor.py`

These were added because the checked-out code already depended on them, but they were missing from the repo snapshot being worked on.

---

## Behavior after repairs

### Working
- `python main.py --check` passes
- backend boots on `8000`
- frontend boots on `3000`
- `/api/v1/health` works
- `/api/v1/schemas` works
- `/schemas` frontend page loads after CORS/env alignment
- extraction stack now runs far enough to perform smoke tests

### Still limited / not fully fixed
- LM Studio output is still unstable for some extraction calls
- many requests appear to hit an effective context limit around `4096`
- multi-record extraction still fails due to malformed JSON from the model
- single-record path can complete, but may end in low-confidence / human-review output with poor extraction results
- some frontend/backend features remain shallow because backend persistence/state management is incomplete for the full UX

---

## Smoke-test artifacts created during repair
Temporary/local files created for testing:
- `tmp_smoke_test.py`
- `smoke_test.pdf`
- `smoke_test_output/`
- `smoke_test_output_single/`
- `.setup-logs/`

These are local repair/test artifacts, not core project files.

---

## Recommended next cleanup steps
1. Review the added compatibility files against the intended upstream architecture.
2. Move the repo out of `/mnt/e/...` into the WSL filesystem for better dev performance.
3. Normalize frontend env/port conventions across docs and runtime.
4. Review LM Studio model/context settings; current extraction is bottlenecked by model/runtime behavior, not just code wiring.
5. Decide whether the added profile/backend abstraction files should become permanent project code or be replaced with canonical versions.
6. Remove or formalize smoke-test artifacts and setup logs.

---

## Summary
The repo did not fail for a single reason. It was a combination of:
- incomplete environment setup
- frontend/backend config drift
- browser CORS mismatch
- missing frontend support files
- missing backend runtime modules
- LM Studio runtime/model limitations

The changes made here were aimed at one goal: **make the repo boot, serve pages, pass preflight checks, and run far enough to test the extraction path**.
