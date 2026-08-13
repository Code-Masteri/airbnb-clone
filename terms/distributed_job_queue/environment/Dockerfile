FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl gcc redis-server \
    && rm -rf /var/lib/apt/lists/*

COPY services/api/requirements.txt /tmp/api-req.txt
COPY services/worker/requirements.txt /tmp/worker-req.txt
COPY services/scheduler/requirements.txt /tmp/scheduler-req.txt

RUN pip install --no-cache-dir \
    -r /tmp/api-req.txt \
    -r /tmp/worker-req.txt \
    -r /tmp/scheduler-req.txt

COPY services/ /app/services/

CMD ["bash"]
