import json
from pathlib import Path


ROOT = Path(".")
REPORTS = ROOT / "reports" / "hw09"
RAW = REPORTS / "raw"
SCREENSHOTS = REPORTS / "screenshots"


def check_file(path):
    return {
        "path": str(path),
        "exists": path.exists(),
    }


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    required_files = [
        Path("semantic_cache.py"),
        Path("semantic_cache_demo.py"),
        Path("threshold_sweep.py"),
        Path("cache_cases.yaml"),
        Path("cache_invalidation_demo.py"),
        Path("self_improving_agents.py"),
        Path("part4_variant_comparison.py"),
        Path("training_data.json"),
        Path("validation_data.json"),
        Path("test_data.json"),
        Path("lessons.json"),
        Path("src/migrate_hw9.py"),
        Path("src/redis_counter.py"),
        Path("redis_counter_demo.py"),
        REPORTS / "RUN_LOG.txt",
        REPORTS / "METRICS.md",
        REPORTS / "AI_USE.md",
        RAW / "threshold-sweep-results.json",
        RAW / "cache-invalidation-results.json",
        RAW / "part4-variant-comparison.json",
        RAW / "self-improving-agent-results.json",
    ]

    checks = []

    for path in required_files:
        checks.append(check_file(path))

    threshold_results = load_json(
        RAW / "threshold-sweep-results.json"
    )

    checks.append(
        {
            "name": "five threshold results",
            "passed": len(threshold_results) == 5,
        }
    )

    invalidation_results = load_json(
        RAW / "cache-invalidation-results.json"
    )

    checks.append(
        {
            "name": "old version cache hit",
            "passed": (
                invalidation_results[
                    "before_data_change"
                ]["is_cached"]
                is True
            ),
        }
    )

    checks.append(
        {
            "name": "new version blocks stale cache",
            "passed": (
                invalidation_results[
                    "after_data_change_before_refresh"
                ]["is_cached"]
                is False
            ),
        }
    )

    variant_results = load_json(
        RAW / "part4-variant-comparison.json"
    )

    expected_variants = {
        "baseline",
        "evaluator_repair",
        "lesson_memory",
        "validated_improvement",
    }

    checks.append(
        {
            "name": "four Part 4 variants",
            "passed": set(variant_results) == expected_variants,
        }
    )

    lessons = load_json(Path("lessons.json"))

    checks.append(
        {
            "name": "lessons file is valid",
            "passed": isinstance(lessons, list),
        }
    )

    screenshots = sorted(SCREENSHOTS.glob("*.png"))

    checks.append(
        {
            "name": "screenshots present",
            "passed": len(screenshots) >= 10,
            "count": len(screenshots),
        }
    )

    all_files_exist = all(
        check.get("exists", check.get("passed", False))
        for check in checks
    )

    verification = {
        "homework": "HW9",
        "student": "Rohini Ramasheshu",
        "sid4": 2604,
        "passed": all_files_exist,
        "checks": checks,
        "screenshot_count": len(screenshots),
    }

    output_path = REPORTS / "verification.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(verification, file, indent=2)

    print(json.dumps(verification, indent=2))
    print(f"\nWrote {output_path}")

    if not all_files_exist:
        raise SystemExit("Verification failed")


if __name__ == "__main__":
    main()