import json
import urllib.request
from pathlib import Path

from tool_runtime import execute_tool


MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"


def ask_ollama(user_input):
    prompt = f"""
You are a tool-selection assistant.

Choose exactly one tool for the user's request.

Available tools:

1. search_vulnerabilities
Input:
{{"query": "string", "limit": 1}}

2. vulnerability_detail
Input:
{{"vulnerability_id": 5005}}

3. vulnerability_summary
Input:
{{"min_severity": 0}}

Return ONLY valid JSON in this exact shape:

{{
  "name": "tool_name",
  "inputs": {{}}
}}

User request:
{user_input}
"""

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
        "format": "json",
    }

    body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        response_data = json.loads(response.read().decode("utf-8"))

    content = response_data["message"]["content"]
    return json.loads(content)


def run_agent(user_input, max_steps=3):
    """Run one real Ollama decision and execute the selected tool."""

    log_path = Path("ollama_agent_runs.jsonl")
    steps = []
    stop_reason = "max_steps"

    for step_number in range(1, max_steps + 1):
        planned_call = ask_ollama(user_input)

        tool_name = planned_call.get("name")
        inputs = planned_call.get("inputs", {})

        result = json.loads(execute_tool(tool_name, inputs))

        record = {
            "user_input": user_input,
            "step": step_number,
            "tool": tool_name,
            "inputs": inputs,
            "result": result,
        }

        steps.append(record)

        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(record) + "\n")

        if not result["ok"]:
            stop_reason = "tool_error_or_safety_block"
            break

        stop_reason = "normal_completion"
        break

    return {
        "steps": len(steps),
        "tool_calls": len(steps),
        "stop_reason": stop_reason,
    }


def main():
    scenarios = [
        "Find vulnerabilities related to CVE",
        "Show vulnerability with ID 5005",
        "Show vulnerability with ID 5006",
        "Give me a summary of vulnerabilities with severity at least 5",
    ]

    metrics = []

    for scenario in scenarios:
        print(f"\nScenario: {scenario}")

        try:
            result = run_agent(scenario)
        except Exception as exc:
            result = {
                "steps": 0,
                "tool_calls": 0,
                "stop_reason": f"agent_error: {exc}",
            }

        print(result)

        metrics.append(
            {
                "scenario": scenario,
                **result,
            }
        )

    Path("OLLAMA_METRICS.md").write_text(
        "# Ollama Agent Metrics\n\n"
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

    print("\nWrote ollama_agent_runs.jsonl and OLLAMA_METRICS.md")


if __name__ == "__main__":
    main()