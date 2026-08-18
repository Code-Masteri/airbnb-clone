import subprocess
import sys
import time

subprocess.run([sys.executable, "-m", "ensurepip"], check=False)
subprocess.run([sys.executable, "-m", "pip", "install",
    "flask==3.0.3", "requests==2.31.0", "redis==5.0.1",
    "psycopg2-binary==2.9.9", "sqlalchemy==2.0.23", "schedule==1.2.1",
    "-q", "--break-system-packages"], check=False)

import requests

BASE = "http://localhost:8000"

def wait_for_api(timeout=30):
    for _ in range(timeout):
        try:
            r = requests.get(f"{BASE}/health", timeout=2)
            if r.status_code == 200 and r.json().get("status") == "healthy":
                return True
        except:
            pass
        time.sleep(1)
    return False

def test_api_health():
    assert wait_for_api(), "API never became healthy — DB or Redis connection failed"
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
    assert r.json()["db"] == "ok"
    assert r.json()["redis"] == "ok"

def test_job_creation():
    wait_for_api()
    r = requests.post(f"{BASE}/jobs", json={"payload": "test_job", "priority": 1})
    assert r.status_code == 201, f"Expected 201 got {r.status_code}: {r.text}"
    assert isinstance(r.json()["id"], int)

def test_priority_ordering():
    wait_for_api()
    requests.post(f"{BASE}/jobs", json={"payload": "low_prio", "priority": 1})
    requests.post(f"{BASE}/jobs", json={"payload": "high_prio", "priority": 10})
    requests.post(f"{BASE}/jobs", json={"payload": "mid_prio", "priority": 5})
    r = requests.get(f"{BASE}/jobs?status=pending")
    jobs = r.json()
    priorities = [j["priority"] for j in jobs]
    assert priorities == sorted(priorities, reverse=True), \
        f"Not ordered DESC: {priorities}"

def test_worker_processes_to_completed():
    wait_for_api()
    r = requests.post(f"{BASE}/jobs", json={"payload": "worker_test", "priority": 0})
    job_id = r.json()["id"]
    for _ in range(20):
        rg = requests.get(f"{BASE}/jobs/{job_id}")
        if rg.json()["status"] == "completed":
            return
        time.sleep(1)
    assert False, f"Job never completed, status: {requests.get(f'{BASE}/jobs/{job_id}').json()['status']}"

def test_scheduler_jobs_submitted():
    wait_for_api()
    time.sleep(12)
    r = requests.get(f"{BASE}/jobs")
    payloads = [j["payload"] for j in r.json()]
    assert "health_check" in payloads
    assert "cleanup_old_records" in payloads
    assert "generate_report" in payloads

def test_stats():
    wait_for_api()
    r = requests.get(f"{BASE}/stats")
    assert r.status_code == 200
    assert isinstance(r.json(), dict)
