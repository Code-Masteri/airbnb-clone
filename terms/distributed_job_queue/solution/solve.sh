#!/bin/bash
set -e

pip install --quiet flask==3.0.3 redis==5.0.1 sqlalchemy==2.0.23 requests==2.31.0 schedule==1.2.1

# Fix 1: DB_URL -> DATABASE_URL (but we'll use SQLite so override it)
sed -i 's/os.environ.get("DB_URL"/os.environ.get("DATABASE_URL"/' /app/services/api/app.py

# Fix 2: wrong redis queue name
sed -i 's/redis_client.lpush("jobs",/redis_client.lpush("job_queue",/' /app/services/api/app.py

# Fix 3: priority ASC -> DESC
sed -i 's/ORDER BY priority ASC/ORDER BY priority DESC/' /app/services/api/app.py

# Fix 4: wrong status value
sed -i "s/status = 'done'/status = 'completed'/" /app/services/worker/worker.py

# Fix 5: priority str -> int
sed -i 's/"priority": str(i)/"priority": int(i)/' /app/services/scheduler/scheduler.py

# Fix 6: queue depth str -> int
sed -i 's/redis_client.set("queue_depth", str(depth))/redis_client.set("queue_depth", depth)/' /app/services/scheduler/scheduler.py

# Start redis in background
redis-server --daemonize yes
sleep 2

# Start API with SQLite
cd /app/services/api
DATABASE_URL="sqlite:////tmp/taskdb.sqlite" \
REDIS_URL="redis://localhost:6379" \
python app.py &
sleep 5

# Start worker
cd /app/services/worker
DATABASE_URL="sqlite:////tmp/taskdb.sqlite" \
REDIS_URL="redis://localhost:6379" \
python worker.py &
sleep 2

# Start scheduler
cd /app/services/scheduler
API_URL="http://localhost:8000" \
REDIS_URL="redis://localhost:6379" \
python scheduler.py &
sleep 12

echo "All services running"
