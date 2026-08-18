## Objective

A distributed job processing system is broken. Services are in `/app/services/`:

- `api/` — Flask REST API on port 8000
- `worker/` — Redis queue consumer
- `scheduler/` — Periodic job submitter

## Goal

Fix all bugs so that:

1. `GET /health` returns `{"status": "healthy", "db": "ok", "redis": "ok"}`
2. `POST /jobs` queues jobs that get processed by the worker
3. Jobs with higher `priority` are listed first
4. Processed jobs have status `completed`
5. Scheduler submits jobs without errors

Start redis: `redis-server --daemonize yes`

Start API: `DATABASE_URL="sqlite:////tmp/taskdb.sqlite" REDIS_URL="redis://localhost:6379" python /app/services/api/app.py &`

Start worker: `DATABASE_URL="sqlite:////tmp/taskdb.sqlite" REDIS_URL="redis://localhost:6379" python /app/services/worker/worker.py &`

Start scheduler: `API_URL="http://localhost:8000" REDIS_URL="redis://localhost:6379" python /app/services/scheduler/scheduler.py &`
