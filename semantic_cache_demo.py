import time
from statistics import mean

from semantic_cache import (
    CACHE_INDEX_KEY,
    SemanticCache,
)


def run_agent(query):
    """Simulate the normal HW8 agent path."""
    time.sleep(0.05)
    return f"Agent answer for: {query}"


def ask(cache, query, threshold=0.85):
    start = time.perf_counter()

    result = cache.lookup(
        query,
        threshold=threshold,
        data_version="v1",
    )

    if result["is_cached"]:
        result["latency_ms"] = (
            time.perf_counter() - start
        ) * 1000
        print(
            f"CACHE HIT | similarity="
            f"{result['similarity']:.3f} | "
            f"{result['latency_ms']:.2f} ms"
        )
        return result

    answer = run_agent(query)

    cache.store(
        query=query,
        answer=answer,
        data_version="v1",
    )

    latency_ms = (
        time.perf_counter() - start
    ) * 1000

    print(
        f"CACHE MISS | similarity="
        f"{result['similarity']:.3f} | "
        f"{latency_ms:.2f} ms"
    )

    return {
        "is_cached": False,
        "similarity": result["similarity"],
        "answer": answer,
        "latency_ms": latency_ms,
    }


def main():
    cache = SemanticCache()

    # Start with an empty cache for a repeatable run.
    keys = cache.redis.smembers(CACHE_INDEX_KEY)

    if keys:
        cache.redis.delete(*keys)

    cache.redis.delete(CACHE_INDEX_KEY)

    queries = [
        "What is the severity of CVE-2026-1001?",
        "What is the severity of CVE-2026-1001?",
        "Tell me the severity of CVE-2026-1001.",
        "How severe is CVE-2026-1001?",
        "What package contains CVE-2026-1001?",
        "Who is the researcher for CVE-2026-1001?",
        "What is a Kafka consumer group?",
        "How does Redis store keys?",
        "What does a UUID identify?",
        "Explain database normalization.",
    ]

    results = []

    for number, query in enumerate(queries, start=1):
        print(f"\nQuery #{number}: {query}")
        result = ask(cache, query)
        results.append(result)

    cached_latencies = [
        item["latency_ms"]
        for item in results
        if item["is_cached"]
    ]

    uncached_latencies = [
        item["latency_ms"]
        for item in results
        if not item["is_cached"]
    ]

    hit_rate = sum(
        item["is_cached"] for item in results
    ) / len(results) * 100

    print("\n=== Cache Metrics ===")
    print(f"Total queries: {len(results)}")
    print(f"Cache hits: {sum(item['is_cached'] for item in results)}")
    print(f"Cache hit rate: {hit_rate:.2f}%")
    print(
        "Average cached latency: "
        f"{mean(cached_latencies):.2f} ms"
        if cached_latencies
        else "Average cached latency: none"
    )
    print(
        "Average non-cached latency: "
        f"{mean(uncached_latencies):.2f} ms"
        if uncached_latencies
        else "Average non-cached latency: none"
    )


if __name__ == "__main__":
    main()