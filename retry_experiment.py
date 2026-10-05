import json
import os
import random
import time
from pathlib import Path


VERIFY_SEED = 262604
MAX_RETRIES = 3
RATES = [0.0, 0.20, 0.50]
CALLS_PER_RATE = 50


def run_with_retry(failure_rate, rng):
    """Run one operation with bounded exponential backoff."""

    started = time.perf_counter()
    attempts = 0

    while attempts <= MAX_RETRIES:
        attempts += 1

        # Deterministic simulated failure.
        failed = rng.random() < failure_rate

        if not failed:
            latency_ms = (time.perf_counter() - started) * 1000
            return {
                "ok": True,
                "attempts": attempts,
                "latency_ms": round(latency_ms, 3),
                "error": None,
            }

        if attempts <= MAX_RETRIES:
            # Bounded exponential backoff: 1ms, 2ms, 4ms.
            delay_seconds = min(0.001 * (2 ** (attempts - 1)), 0.01)
            time.sleep(delay_seconds)

    latency_ms = (time.perf_counter() - started) * 1000

    return {
        "ok": False,
        "attempts": attempts,
        "latency_ms": round(latency_ms, 3),
        "error": "operation failed after all retries",
    }


def percentile(values, percentage):
    values = sorted(values)
    index = int((percentage / 100) * (len(values) - 1))
    return values[index]


def main():
    output_dir = Path("reports/hw05/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_path = output_dir / "retry-results.jsonl"
    rng = random.Random(VERIFY_SEED)
    all_results = []

    with raw_path.open("w", encoding="utf-8") as raw_file:
        for rate in RATES:
            for call_number in range(1, CALLS_PER_RATE + 1):
                result = run_with_retry(rate, rng)

                record = {
                    "failure_rate": rate,
                    "call_number": call_number,
                    **result,
                }

                all_results.append(record)
                raw_file.write(json.dumps(record) + "\n")

    print("Part 3 retry experiment")
    print(f"Seed: {VERIFY_SEED}")
    print(f"Max retries: {MAX_RETRIES}")
    print()
    print("rate | success_rate | mean_ms | p99_ms")

    for rate in RATES:
        rows = [
            row for row in all_results
            if row["failure_rate"] == rate
        ]

        successes = sum(row["ok"] for row in rows)
        latencies = [row["latency_ms"] for row in rows]

        success_rate = successes / len(rows)
        mean_ms = sum(latencies) / len(latencies)
        p99_ms = percentile(latencies, 99)

        print(
            f"{rate:>4.0%} | "
            f"{success_rate:>12.1%} | "
            f"{mean_ms:>7.3f} | "
            f"{p99_ms:>6.3f}"
        )

    print()
    print(f"Raw results written to: {raw_path}")


if __name__ == "__main__":
    main()