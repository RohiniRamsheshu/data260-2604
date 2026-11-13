import json

from trace_utils import trace_span


TRACE_ID = "hw10-failure-demo-001"


def main():
    try:
        with trace_span(TRACE_ID, "reviewer") as span:
            span["failure_type"] = "simulated_test_failure"
            raise RuntimeError(
                "Simulated reviewer failure for HW10 tracing"
            )

    except RuntimeError as exc:
        print("Expected failure captured:")
        print(str(exc))

    print("\nFailed trace written to:")
    print("reports/hw10/raw/spans.jsonl")

    with open(
        "reports/hw10/raw/spans.jsonl",
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            record = json.loads(line)

            if record["trace_id"] == TRACE_ID:
                print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()