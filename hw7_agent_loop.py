import json
from pathlib import Path

from tool_runtime import execute_tool


MAX_STEPS = 4
RAW_DIR = Path("reports/hw07/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def repair_call(call):
    """Repair one malformed or incomplete tool call."""
    name = call.get("name")
    inputs = call.get("inputs")

    if not isinstance(inputs, dict):
        inputs = {}

    if name == "search_vulnerabilities":
        inputs.setdefault("query", "CVE")
        inputs.setdefault("limit", 2)

    elif name == "vulnerability_detail":
        value = inputs.get("vulnerability_id", 5005)
        if not isinstance(value, int) or value <= 0:
            inputs["vulnerability_id"] = 5005

    elif name == "vulnerability_summary":
        value = inputs.get("min_severity", 0)
        if not isinstance(value, int) or value < 0 or value > 10:
            inputs["min_severity"] = 5

    return {
        "name": name,
        "inputs": inputs,
    }


def run_agent(task_name, planned_calls, allow_repair=True):
    messages = [
        {
            "role": "user",
            "content": task_name,
        }
    ]

    logs = []
    repair_used = False
    stop_reason = "max_steps"

    for step in range(1, MAX_STEPS + 1):
        if not planned_calls:
            stop_reason = "completed"
            break

        call = planned_calls.pop(0)
        tool_name = call.get("name")
        inputs = call.get("inputs", {})

        if tool_name not in {
            "search_vulnerabilities",
            "vulnerability_detail",
            "vulnerability_summary",
        }:
            if allow_repair and not repair_used:
                repair_used = True
                call = repair_call(
                    {
                        "name": "search_vulnerabilities",
                        "inputs": {"query": "CVE", "limit": 2},
                    }
                )
                tool_name = call["name"]
                inputs = call["inputs"]
            else:
                stop_reason = "unknown_tool"
                break

        result = json.loads(execute_tool(tool_name, inputs))

        messages.append(
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "tool": tool_name,
                        "inputs": inputs,
                    }
                ),
            }
        )
        messages.append(
            {
                "role": "tool",
                "content": json.dumps(result),
            }
        )

        record = {
            "task": task_name,
            "step": step,
            "tool": tool_name,
            "inputs": inputs,
            "result": result,
        }
        logs.append(record)

        if not result["ok"]:
            if allow_repair and not repair_used:
                repair_used = True
                repaired = repair_call(
                    {
                        "name": tool_name,
                        "inputs": inputs,
                    }
                )
                planned_calls.insert(0, repaired)
                continue

            stop_reason = "tool_error"
            break

    else:
        stop_reason = "max_steps"

    if len(logs) < MAX_STEPS and stop_reason == "max_steps":
        stop_reason = "completed"

    return {
        "task": task_name,
        "success": stop_reason in {"completed", "max_steps"}
        and bool(logs),
        "steps": len(logs),
        "total_tool_calls": len(logs),
        "repair_used": repair_used,
        "stop_reason": stop_reason,
        "messages": messages,
        "logs": logs,
    }


def main():
    tasks = [
        (
            "Task A: find CVE vulnerabilities and inspect one result",
            [
                {
                    "name": "search_vulnerabilities",
                    "inputs": {"query": "CVE", "limit": 2},
                },
                {
                    "name": "vulnerability_detail",
                    "inputs": {"vulnerability_id": 5005},
                },
            ],
        ),
        (
            "Task B: summarize vulnerabilities and find supporting examples",
            [
                {
                    "name": "vulnerability_summary",
                    "inputs": {"min_severity": 5},
                },
                {
                    "name": "search_vulnerabilities",
                    "inputs": {"query": "package", "limit": 2},
                },
            ],
        ),
        (
            "Task C: compare two vulnerabilities",
            [
                {
                    "name": "search_vulnerabilities",
                    "inputs": {"query": "CVE", "limit": 2},
                },
                {
                    "name": "vulnerability_detail",
                    "inputs": {"vulnerability_id": 5005},
                },
                {
                    "name": "vulnerability_detail",
                    "inputs": {
                        "vulnerability_id": 5006,
                        "approved": True,
                    },
                },
            ],
        ),
        (
            "Task D: recover from a malformed tool call",
            [
                {
                    "name": "wrong_tool_name",
                    "inputs": {},
                },
                {
                    "name": "vulnerability_summary",
                    "inputs": {"min_severity": 5},
                },
            ],
        ),
    ]

    all_results = []

    for task_name, planned_calls in tasks:
        result = run_agent(task_name, planned_calls.copy())
        all_results.append(result)
        print(
            task_name,
            "success=",
            result["success"],
            "calls=",
            result["total_tool_calls"],
            "repair=",
            result["repair_used"],
        )

    output_path = RAW_DIR / "agent-loop-results.json"
    output_path.write_text(
        json.dumps(all_results, indent=2),
        encoding="utf-8",
    )

    total_calls = sum(
        result["total_tool_calls"] for result in all_results
    )
    successes = sum(
        result["success"] for result in all_results
    )

    metrics = f"""# HW7 Part 2 Agent Metrics

- Tasks: {len(all_results)}
- Successful tasks: {successes}
- Total tool calls: {total_calls}
- Maximum steps per task: {MAX_STEPS}
- Repair policy: one repair attempt per task
- Tool-role messages: recorded in each task result
"""

    (RAW_DIR / "agent-loop-metrics.md").write_text(
        metrics,
        encoding="utf-8",
    )

    print(f"Wrote {output_path}")
    print(f"Successful tasks: {successes}/{len(all_results)}")


if __name__ == "__main__":
    main()