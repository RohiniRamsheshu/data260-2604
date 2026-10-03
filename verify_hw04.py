import json
import subprocess
import requests

SID4 = "2604"
SEED = 2604
VERIFY_SEED = 260000 + SEED  # 262604
PORT_BASE = 8000 + (SEED % 900)  # 8004
BASE_URL = f"http://localhost:{PORT_BASE}"

try:
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")
except Exception:
    commit_hash = "unknown"

checks = []

# Check 1: Backend service response
try:
    res = requests.get(f"{BASE_URL}/docs", timeout=5)
    checks.append({"check": "backend_running", "status": "PASS" if res.status_code == 200 else "FAIL"})
except Exception as e:
    checks.append({"check": "backend_running", "status": "FAIL", "error": str(e)})

# Check 2: Naive list endpoint
try:
    res = requests.get(f"{BASE_URL}/api/vulnerabilities/naive?page_size=10", timeout=5)
    checks.append({"check": "naive_endpoint_data", "status": "PASS" if res.status_code == 200 else "FAIL"})
except Exception as e:
    checks.append({"check": "naive_endpoint_data", "status": "FAIL", "error": str(e)})

# Check 3: Fixed list endpoint
try:
    res = requests.get(f"{BASE_URL}/api/vulnerabilities/fixed?page_size=10", timeout=5)
    checks.append({"check": "fixed_endpoint_data", "status": "PASS" if res.status_code == 200 else "FAIL"})
except Exception as e:
    checks.append({"check": "fixed_endpoint_data", "status": "FAIL", "error": str(e)})

output = {
    "homework": "HW04",
    "SID4": SID4,
    "commit_hash": commit_hash,
    "model_configuration": "FastAPI + MySQL 8.0 + SQLAlchemy",
    "SEED": SEED,
    "VERIFY_SEED": VERIFY_SEED,
    "checks": checks
}

with open("reports/hw04/verification.json", "w") as f:
    json.dump(output, f, indent=2)

print("Saved reports/hw04/verification.json successfully.")