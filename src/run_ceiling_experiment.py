import sys
import os
import json
import time
import csv

sys.path.append(os.path.dirname(__file__))
import agent_graph

with open("reports/hw02/cases/schema_input.json") as f:
    case = json.load(f)

def run_once(app):
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
    final_state = initial_state

    for step in app.stream(initial_state):
        for node_name, updates in step.items():
            final_state = {**final_state, **updates}

    latency_ms = (time.time() - start) * 1000

    completed = final_state.get("schema_valid") and not final_state.get("reviewer_feedback", {}).get("has_issues", True)

    return completed, latency_ms

results = []

for ceiling in [2, 10]:
    agent_graph.TURN_CEILING = ceiling
    app = agent_graph.build_graph()

    print(f"\n=== Running 20 iterations with TURN_CEILING={ceiling} ===")
    for i in range(20):
        completed, latency_ms = run_once(app)
        results.append({"ceiling": ceiling, "run": i + 1, "completed": completed, "latency_ms": round(latency_ms, 2)})
        print(f"Run {i+1}: completed={completed}, latency={latency_ms:.0f}ms")

with open("reports/hw02/raw/ceiling_comparison_runs.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["ceiling", "run", "completed", "latency_ms"])
    writer.writeheader()
    writer.writerows(results)

print("\nDone. Results saved to reports/hw02/raw/ceiling_comparison_runs.csv")