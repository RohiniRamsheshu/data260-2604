import sys
import os
import json
import time
import csv

sys.path.append(os.path.dirname(__file__))
from agent_graph import build_graph, TURN_CEILING

with open("reports/hw02/cases/schema_input.json") as f:
    case = json.load(f)

app = build_graph()

def run_once():
    initial_state = {
        "title": case["title"],
        "content": case["content"],
        "planner_proposal": {},
        "reviewer_feedback": {},
        "turn_count": 0,
        "validation_error": "",
        "schema_valid": False
    }

    start = time.time()
    planner_calls = 0
    final_state = initial_state

    for step in app.stream(initial_state):
        for node_name, updates in step.items():
            final_state = {**final_state, **updates}
            if node_name == "planner":
                planner_calls += 1

    latency_ms = (time.time() - start) * 1000

    if final_state.get("turn_count", 0) >= TURN_CEILING and not (
        final_state.get("schema_valid") and not final_state.get("reviewer_feedback", {}).get("has_issues", True)
    ):
        outcome = "abandoned_at_ceiling"
    elif planner_calls == 1:
        outcome = "valid_first_attempt"
    elif planner_calls == 2:
        outcome = "valid_after_1_retry"
    else:
        outcome = "valid_after_2plus_retries"

    return outcome, latency_ms

results = []
for i in range(30):
    print(f"Run {i+1}/30...")
    outcome, latency_ms = run_once()
    results.append({"run": i + 1, "outcome": outcome, "latency_ms": round(latency_ms, 2)})
    print(f"  -> {outcome} ({latency_ms:.0f}ms)")

with open("reports/hw02/raw/schema_validation_runs.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["run", "outcome", "latency_ms"])
    writer.writeheader()
    writer.writerows(results)

print("\nDone. Results saved to reports/hw02/raw/schema_validation_runs.csv")