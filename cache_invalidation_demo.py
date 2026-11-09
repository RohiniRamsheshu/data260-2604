import json
from pathlib import Path

from semantic_cache import SemanticCache, CACHE_INDEX_KEY


QUERY = "What is the severity of CVE-2026-1001?"
OLD_ANSWER = "CVE-2026-1001 has severity 5."
NEW_ANSWER = "CVE-2026-1001 has severity 8."

THRESHOLD = 0.85


def clear_cache(cache):
    keys = list(cache.redis.smembers(CACHE_INDEX_KEY))

    if keys:
        cache.redis.delete(*keys)

    cache.redis.delete(CACHE_INDEX_KEY)


def main():
    cache = SemanticCache()
    clear_cache(cache)

    cache.store(
        query=QUERY,
        answer=OLD_ANSWER,
        data_version="v1",
    )

    old_version_result = cache.lookup(
        query=QUERY,
        threshold=THRESHOLD,
        data_version="v1",
    )

    new_version_result = cache.lookup(
        query=QUERY,
        threshold=THRESHOLD,
        data_version="v2",
    )

    cache.store(
        query=QUERY,
        answer=NEW_ANSWER,
        data_version="v2",
    )

    refreshed_result = cache.lookup(
        query=QUERY,
        threshold=THRESHOLD,
        data_version="v2",
    )

    output = {
        "threshold": THRESHOLD,
        "before_data_change": {
            "data_version": "v1",
            "is_cached": old_version_result["is_cached"],
            "answer": old_version_result["answer"],
        },
        "after_data_change_before_refresh": {
            "data_version": "v2",
            "is_cached": new_version_result["is_cached"],
            "answer": new_version_result["answer"],
        },
        "after_cache_refresh": {
            "data_version": "v2",
            "is_cached": refreshed_result["is_cached"],
            "answer": refreshed_result["answer"],
        },
    }

    print(json.dumps(output, indent=2))

    output_path = Path(
        "reports/hw09/raw/cache-invalidation-results.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()