import json
from pathlib import Path

from tool_runtime import execute_tool


class MockModel:
    """Offline model used for repeatable tests."""

    def __init__(self, planned_calls):
        self.planned_calls = planned_calls
        self.position = 0

    def next_call(self, user_input):
        if self.position >= len(self.planned_calls):
            return None

        call = self.planned_calls[self.position]
        self.position += 1
        return call


def run_agent(user_input, model, max_steps=3):
    """Run a bounded agent loop and log every step."""

    log_path = Path("agent_runs.jsonl")
    steps = []
    stop_reason = "max_steps"

    for step_number in range(1, max_steps + 1):
        planned_call = model.next_call(user_input)

        if planned_call is None:
            stop_reason = "normal_completion"
            break

        tool_name = planned_call["name"]
        inputs = planned_call["inputs"]

        result = execute_tool(tool_name, inputs)

        record = {
            "user_input": user_input,
            "step": step_number,
            "tool": tool_name,
            "inputs": inputs,
            "result": json.loads(result),
        }

        steps.append(record)

        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(record) + "\n")

        if not record["result"]["ok"]:
            stop_reason = "tool_error_or_safety_block"
            break

    return {
        "steps": len(steps),
        "tool_calls": len(steps),
        "stop_reason": stop_reason,
    }


def main():
    scenarios = [
        (
            "Find CVE vulnerabilities",
            [
                {
                    "name": "search_vulnerabilities",
                    "inputs": {"query": "CVE", "limit": 2},
                }
            ],
        ),
        (
            "Show a normal vulnerability",
            [
                {
                    "name": "vulnerability_detail",
                    "inputs": {"vulnerability_id": 5005},
                }
            ],
        ),
        (
            "Show a high severity vulnerability",
            [
                {
                    "name": "vulnerability_detail",
                    "inputs": {"vulnerability_id": 5006},
                }
            ],
        ),
        (
            "Keep asking for more information",
            [
                {
                    "name": "search_vulnerabilities",
                    "inputs": {"query": "CVE"},
                },
                {
                    "name": "vulnerability_summary",
                    "inputs": {"min_severity": 0},
                },
                {
                    "name": "search_vulnerabilities",
                    "inputs": {"query": "package"},
                },
                {
                    "name": "vulnerability_summary",
                    "inputs": {"min_severity": 2},
                },
            ],
        ),
    ]

    metrics = []

    for user_input, planned_calls in scenarios:
        result = run_agent(
            user_input,
            MockModel(planned_calls),
            max_steps=3,
        )

        metrics.append(
            {
                "scenario": user_input,
                **result,
            }
        )

    Path("METRICS.md").write_text(
        "# Part 5 Agent Metrics\n\n"
        "| Scenario | Steps | Tool calls | Stop reason |\n"
        "|---|---:|---:|---|\n"
        + "\n".join(
            f"| {row['scenario']} | {row['steps']} | "
            f"{row['tool_calls']} | {row['stop_reason']} |"
            for row in metrics
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(metrics, indent=2))
    print("\nWrote agent_runs.jsonl and METRICS.md")


if __name__ == "__main__":
    main()