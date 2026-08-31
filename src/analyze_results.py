import csv
import json
from collections import Counter
import statistics

def analyze(temperature, rows):
    tag_sets = [tuple(sorted(json.loads(r["tags"]))) for r in rows]
    latencies = sorted([float(r["latency_ms"]) for r in rows])

    distinct_sets = len(set(tag_sets))

    all_tags_lists = [json.loads(r["tags"]) for r in rows]
    tag_counter = Counter(tag for tags in all_tags_lists for tag in tags)
    in_all_20 = [tag for tag, count in tag_counter.items() if count == 20]
    in_exactly_1 = [tag for tag, count in tag_counter.items() if count == 1]

    def percentile(data, p):
        idx = int(len(data) * p / 100)
        idx = min(idx, len(data) - 1)
        return data[idx]

    p50 = percentile(latencies, 50)
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)

    print(f"\n=== Temperature {temperature} ===")
    print(f"Distinct tag sets: {distinct_sets}")
    print(f"Tags in all 20 runs: {in_all_20}")
    print(f"Tags in exactly 1 run: {in_exactly_1}")
    print(f"Latency p50/p95/p99 (ms): {p50:.0f} / {p95:.0f} / {p99:.0f}")

with open("reports/hw01/raw/nondeterminism_results.csv") as f:
    rows = list(csv.DictReader(f))

rows_07 = [r for r in rows if r["temperature"] == "0.7"]
rows_00 = [r for r in rows if r["temperature"] == "0.0"]

analyze("0.7", rows_07)
analyze("0.0", rows_00)