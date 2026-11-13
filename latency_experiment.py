import json
import statistics
import subprocess
import sys
import time
from pathlib import Path


SPAN_FILE = Path("reports/hw10/raw/spans.jsonl")
OUTPUT_FILE = Path("reports/hw10/raw/cache-miss-latency-results.json")
STAGES = [
    "cache_lookup",
    "planner",
    "writer",
    "reviewer",
    "queue_wait",
]


def read_spans():
    if not SPAN_FILE.exists():
        return []

    with open(SPAN_FILE, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def percentile(values, percentage):
    if not values:
        return None

    values = sorted(values)
    index = round((percentage / 100) * (len(values) - 1))
    return values[index]


def main():
    before_count = len(read_spans())
    start_time = time.perf_counter()

    for number in range(1, 51):
        query = (
            f"HW10 confirmed cache miss latency probe "
            f"number {number} unique correlation question"
        )

        print(f"Running request {number}/50")

        result = subprocess.run(
            [sys.executable, "traced_request.py", query],
            capture_output=True,
            text=True,
            check=False,
        )

        if "CACHE MISS" not in result.stdout:
            print("Warning: request did not report CACHE MISS")

    elapsed_seconds = time.perf_counter() - start_time
    new_spans = read_spans()[before_count:]

    grouped = {}

    for span in new_spans:
        trace_id = span["trace_id"]
        grouped.setdefault(trace_id, []).append(span)

    stage_values = {stage: [] for stage in STAGES}
    confirmed_misses = 0

    for spans in grouped.values():
        span_map = {span["stage"]: span for span in spans}
        cache_span = span_map.get("cache_lookup")

        if not cache_span:
            continue

        if cache_span.get("cache_path") != "miss":
            continue

        confirmed_misses += 1

        for stage in STAGES:
            if stage in span_map:
                stage_values[stage].append(
                    span_map[stage]["duration_ms"]
                )

    metrics = {}

    for stage, values in stage_values.items():
        metrics[stage] = {
            "count": len(values),
            "p50_ms": percentile(values, 50),
            "p95_ms": percentile(values, 95),
            "mean_ms": (
                round(statistics.mean(values), 3)
                if values
                else None
            ),
        }

    result = {
        "requested": 50,
        "confirmed_cache_misses": confirmed_misses,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "stage_metrics": metrics,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)

    print(json.dumps(result, indent=2))
    print(f"\nWrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()