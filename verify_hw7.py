import json
import subprocess
from pathlib import Path


ROOT = Path(".")
REPORT = ROOT / "reports" / "hw07"
RAW = REPORT / "raw"
SCREENSHOTS = REPORT / "screenshots"


def exists(path):
    return path.exists()


def valid_json(path):
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def main():
    checks = {
        "hw7_report_folder": exists(REPORT),
        "run_log": exists(REPORT / "RUN_LOG.txt"),
        "metrics": exists(REPORT / "METRICS.md"),
        "ai_use": exists(REPORT / "AI_USE.md"),
        "agent_loop_results": valid_json(
            RAW / "agent-loop-results.json"
        ),
        "reflexion_results": valid_json(
            RAW / "reflexion-results.json"
        ),
        "bike_mrkl_results": valid_json(
            RAW / "bike-mrkl-results.json"
        ),
        "prompt_injection_results": valid_json(
            RAW / "prompt-injection-results.json"
        ),
        "file_tools_results": valid_json(
            RAW / "file-tools-safety-results.json"
        ),
        "screenshots_folder": exists(SCREENSHOTS),
    }

    commit_hash = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        text=True,
    ).strip()

    output = {
        "homework": "HW7",
        "sid4": 2604,
        "commit_hash": commit_hash,
        "model": "qwen2.5:3b",
        "config": {
            "PORT_BASE": 8804,
            "PREFIX": "s2604",
            "SEED": 2604,
            "VERIFY_SEED": 262604,
            "DOMAIN_ID": 4,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }

    path = REPORT / "verification.json"
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(json.dumps(output, indent=2))
    print(f"\nOverall passed: {output['passed']}")


if __name__ == "__main__":
    main()