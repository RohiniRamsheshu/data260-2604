import json
from pathlib import Path


INPUT_COST_PER_MILLION = 1.00
OUTPUT_COST_PER_MILLION = 5.00
CONVERSATIONS = 10_000
TURNS_PER_CONVERSATION = 30
SUMMARY_TOKENS = 30


def estimate_cost(input_tokens, output_tokens):
    input_cost = (
        input_tokens / 1_000_000
    ) * INPUT_COST_PER_MILLION

    output_cost = (
        output_tokens / 1_000_000
    ) * OUTPUT_COST_PER_MILLION

    return input_cost + output_cost


def main():
    source_path = Path(
        "reports/hw06/raw/memory-cost-results.json"
    )

    results = json.loads(
        source_path.read_text(encoding="utf-8")
    )

    by_size = {
        row["memory_size"]: row
        for row in results
    }

    full_memory = by_size[30]
    medium_memory = by_size[12]

    policies = {
        "full_30_messages": {
            "prompt_tokens": full_memory["prompt_tokens"],
            "completion_tokens": full_memory["completion_tokens"],
        },
        "compressed_12_plus_summary": {
            "prompt_tokens": (
                medium_memory["prompt_tokens"]
                + SUMMARY_TOKENS
            ),
            "completion_tokens": medium_memory["completion_tokens"],
        },
    }

    report = []

    for name, values in policies.items():
        input_tokens = (
            values["prompt_tokens"]
            * TURNS_PER_CONVERSATION
            * CONVERSATIONS
        )

        output_tokens = (
            values["completion_tokens"]
            * TURNS_PER_CONVERSATION
            * CONVERSATIONS
        )

        cost = estimate_cost(
            input_tokens,
            output_tokens,
        )

        report.append(
            {
                "policy": name,
                "prompt_tokens_per_turn": values["prompt_tokens"],
                "completion_tokens_per_turn": values[
                    "completion_tokens"
                ],
                "total_input_tokens": input_tokens,
                "total_output_tokens": output_tokens,
                "estimated_cost_usd": round(cost, 4),
            }
        )

    output_path = Path(
        "reports/hw06/raw/memory-policy-results.json"
    )

    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("Memory policy comparison")

    for row in report:
        print(
            f"{row['policy']}: "
            f"${row['estimated_cost_usd']:.4f}"
        )

    print(f"\nWrote {output_path}")


if __name__ == "__main__":
    main()