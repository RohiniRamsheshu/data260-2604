"""
HW3 - Self-check script. Verifies the key deliverables exist and meet
the assignment's basic requirements, then writes the results to
reports/hw03/verification.json.

Run with: python src/verify_hw03.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HW03_DIR = REPO_ROOT / "reports" / "hw03"

checks = []


def check(name, passed, detail=""):
    checks.append({"check": name, "passed": bool(passed), "detail": detail})
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name} - {detail}")


def run_checks():
    # 1. Corpus exists and is >= 200KB
    corpus_dir = REPO_ROOT / "corpus"
    if corpus_dir.exists():
        txt_files = list(corpus_dir.glob("*.txt"))
        total_size = sum(f.stat().st_size for f in txt_files)
        check(
            "corpus_min_200kb",
            total_size >= 200_000,
            f"{len(txt_files)} files, {total_size} bytes",
        )
    else:
        check("corpus_min_200kb", False, "corpus/ directory not found")

    # 2. SOURCES.md and CORPUS_MANIFEST.json exist
    sources_path = HW03_DIR / "SOURCES.md"
    manifest_path = HW03_DIR / "CORPUS_MANIFEST.json"
    check("sources_md_exists", sources_path.exists(), str(sources_path))
    check("corpus_manifest_exists", manifest_path.exists(), str(manifest_path))

    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        check(
            "corpus_manifest_matches_files",
            manifest.get("total_files") == len(list(corpus_dir.glob("*.txt"))),
            f"manifest says {manifest.get('total_files')} files",
        )

    # 3. questions.yaml exists with 5 questions
    questions_path = HW03_DIR / "questions.yaml"
    if questions_path.exists():
        import yaml
        with open(questions_path) as f:
            data = yaml.safe_load(f)
        n_questions = len(data.get("questions", []))
        check("questions_yaml_has_5", n_questions == 5, f"{n_questions} questions found")

        n_single_source = sum(1 for q in data.get("questions", []) if q.get("single_source"))
        check(
            "at_least_2_single_source_questions",
            n_single_source >= 2,
            f"{n_single_source} single-source questions",
        )
    else:
        check("questions_yaml_has_5", False, "questions.yaml not found")
        check("at_least_2_single_source_questions", False, "questions.yaml not found")

    # 4. raw/ output files exist (CSV/JSON/JSONL)
    raw_dir = HW03_DIR / "raw"
    for fname in ["retrieval_results.csv", "retrieval_results.json", "retrieval_results.jsonl"]:
        fpath = raw_dir / fname
        check(f"raw_{fname}_exists", fpath.exists(), str(fpath))

    # 5. METRICS.md exists
    metrics_path = HW03_DIR / "METRICS.md"
    check("metrics_md_exists", metrics_path.exists(), str(metrics_path))

    # 6. RUN_LOG.txt exists and is non-empty
    run_log_path = HW03_DIR / "RUN_LOG.txt"
    if run_log_path.exists():
        size = run_log_path.stat().st_size
        check("run_log_non_empty", size > 100, f"{size} bytes")
    else:
        check("run_log_non_empty", False, "RUN_LOG.txt not found")

    # 7. Auth app files exist
    for relpath in ["src/auth.py", "src/templates/home.html", "src/templates/login.html", "src/templates/dashboard.html"]:
        p = REPO_ROOT / relpath
        check(f"auth_file_{relpath}", p.exists(), relpath)

    # 8. RAG code exists
    for relpath in ["src/rag/chunking.py", "src/rag/retrieval.py", "src/rag/run_comparison.py"]:
        p = REPO_ROOT / relpath
        check(f"rag_file_{relpath}", p.exists(), relpath)


def main():
    run_checks()
    n_passed = sum(1 for c in checks if c["passed"])
    n_total = len(checks)

    result = {
        "overall_pass": n_passed == n_total,
        "checks_passed": n_passed,
        "checks_total": n_total,
        "checks": checks,
    }

    HW03_DIR.mkdir(parents=True, exist_ok=True)
    out_path = HW03_DIR / "verification.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n{n_passed}/{n_total} checks passed.")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
