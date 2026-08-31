import os
import json
import subprocess

checks = {}

checks["index_html_exists"] = os.path.exists("index.html")
checks["script_js_exists"] = os.path.exists("script.js")
checks["dockerfile_exists"] = os.path.exists("Dockerfile")
checks["domain_schema_exists"] = os.path.exists("DOMAIN_SCHEMA.md")
checks["agents_demo_exists"] = os.path.exists("src/agents_demo.py")
checks["model_client_exists"] = os.path.exists("src/model_client.py")
checks["nondeterminism_results_exist"] = os.path.exists("reports/hw01/raw/nondeterminism_results.csv")

try:
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
    checks["ollama_reachable"] = result.returncode == 0
except Exception:
    checks["ollama_reachable"] = False

checks["all_passed"] = all(checks.values())

with open("verification.json", "w") as f:
    json.dump(checks, f, indent=2)

print(json.dumps(checks, indent=2))