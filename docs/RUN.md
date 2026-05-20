# RUN

## Start order
Use separate terminals.

### Terminal 1 — LM Studio
- Start LM Studio
- Load the model
- Ensure server is enabled at:
  - `http://localhost:1234/v1`

Quick check:
```bash
curl http://localhost:1234/v1/models
```

---

### Terminal 2 — Celery worker
From repo root:
```bash
source .venv/bin/activate
export PYTHONPATH=$PWD
python -m celery -A src.queue.celery_app worker \
  --loglevel INFO \
  --concurrency 4 \
  --hostname worker@%h \
  --pool prefork \
  --max-tasks-per-child 100 \
  --max-memory-per-child 512000 \
  --prefetch-multiplier 1 \
  --queues document_processing,batch_processing,reprocessing \
  --events
```

Note: Redis must already be available on `localhost:6379`. If Celery says it connected to Redis, you are good.

---

### Terminal 3 — Backend
From repo root:
```bash
source .venv/bin/activate
export PYTHONPATH=$PWD
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload --reload-dir src
```

Quick checks:
```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/schemas
```

---

### Terminal 4 — Frontend
From `frontend/`:
```bash
npm run dev -- --port 3000
```

Open:
- `http://127.0.0.1:3000`
- `http://127.0.0.1:3000/schemas`
- `http://127.0.0.1:3000/documents`
- `http://127.0.0.1:3000/tasks`

---

## Typical debugging

### Port already in use
If backend/frontend says `EADDRINUSE` or `Address already in use`, something is already running.

Check:
```bash
lsof -iTCP:8000 -sTCP:LISTEN -Pn
lsof -iTCP:3000 -sTCP:LISTEN -Pn
```

Kill if needed:
```bash
kill <PID>
```

Then restart that service.

---

### LM Studio check
This is normal and not a health check:
```bash
curl http://localhost:1234/v1
```

Use this instead:
```bash
curl http://localhost:1234/v1/models
```

---

### Redis check
If unsure whether Redis is running:
```bash
redis-cli ping
```
Expected:
```bash
PONG
```

If Celery already says it connected to `redis://localhost:6379/0`, Redis is fine.
