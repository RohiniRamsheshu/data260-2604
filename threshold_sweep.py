import json
import time
from pathlib import Path

import yaml

from semantic_cache import SemanticCache, CACHE_INDEX_KEY


CANONICAL_QUERY = "What is the severity of CVE-2026-1001?"
CANONICAL_ANSWER = "CVE-2026-1001 has severity 5."
DATA_VERSION = "v1"

THRESHOLDS = [0.75, 0.80, 0.85, 0.90, 0.95]

# Illustrative cost units:
# A cache hit is cheap; an agent/model call is expensive.
CACHE_HIT_COST = 0.05
AGENT_CALL_COST = 1.00
FALSE_HIT_PENALTY = 5.00


def clear_cache(cache):
    """Remove previous semantic-cache records before each threshold test."""
    keys = list(cache.redis.smembers(CACHE_INDEX_KEY))

    if keys:
        cache.redis.delete(*keys)

    cache.redis.delete(CACHE_INDEX_KEY)


def run_threshold(cache, cases, threshold):
    clear_cache(cache)

    # Store one known answer that all test cases compare against.
    cache.store(
        query=CANONICAL_QUERY,
        answer=CANONICAL_ANSWER,
        data_version=DATA_VERSION,
    )

    hits = 0
    expected_hits = 0
    false_hits = 0
    correct_predictions = 0
    latencies = []
    details = []

    for case in cases:
        start = time.perf_counter()

        result = cache.lookup(
            query=case["query"],
            threshold=threshold,
            data_version=DATA_VERSION,
        )

        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

        actual_hit = result["is_cached"]
        expected_hit = case["should_hit"]

        if actual_hit:
            hits += 1

        if expected_hit:
            expected_hits += 1

        if actual_hit and not expected_hit:
            false_hits += 1

        if actual_hit == expected_hit:
            correct_predictions += 1

        details.append(
            {
                "case_id": case["case_id"],
                "category": case["category"],
                "query": case["query"],
                "expected_hit": expected_hit,
                "actual_hit": actual_hit,
                "similarity": result["similarity"],
                "latency_ms": round(elapsed_ms, 4),
            }
        )

    misses = len(cases) - hits
    hit_rate = hits / len(cases)
    false_hit_rate = false_hits / len(cases)
    accuracy = correct_predictions / len(cases)
    mean_latency_ms = sum(latencies) / len(latencies)

    total_cost = (
        hits * CACHE_HIT_COST
        + misses * AGENT_CALL_COST
        + false_hits * FALSE_HIT_PENALTY
    )

    return {
        "threshold": threshold,
        "total_cases": len(cases),
        "hits": hits,
        "misses": misses,
        "expected_hits": expected_hits,
        "false_hits": false_hits,
        "hit_rate": round(hit_rate, 4),
        "false_hit_rate": round(false_hit_rate, 4),
        "accuracy": round(accuracy, 4),
        "mean_lookup_latency_ms": round(mean_latency_ms, 4),
        "total_cost_units": round(total_cost, 4),
        "details": details,
    }


def main():
    with open("cache_cases.yaml", "r", encoding="utf-8") as file:
        cases = yaml.safe_load(file)

    cache = SemanticCache()
    results = []

    print("=== Semantic Cache Threshold Sweep ===")
    print(f"Test cases: {len(cases)}")
    print(f"Thresholds: {THRESHOLDS}")
    print()

    for threshold in THRESHOLDS:
        result = run_threshold(cache, cases, threshold)
        results.append(result)

        print(
            f"threshold={result['threshold']:.2f} | "
            f"hit_rate={result['hit_rate']:.2%} | "
            f"false_hit_rate={result['false_hit_rate']:.2%} | "
            f"accuracy={result['accuracy']:.2%} | "
            f"latency_ms={result['mean_lookup_latency_ms']:.4f} | "
            f"cost={result['total_cost_units']:.2f}"
        )

    output_path = Path("reports/hw09/raw/threshold-sweep-results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    print()
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()