"""
HW3 - Part 2: Runs the full retrieval comparison across all three
chunking techniques and all five questions in questions.yaml, then
saves per-query, per-technique results as CSV, JSON, and JSONL into
reports/hw03/raw/, for later summarization in METRICS.md.
"""

import csv
import json
from pathlib import Path

import yaml

from retrieval import build_indexes, compare_query

REPO_ROOT = Path(__file__).resolve().parents[2]
QUESTIONS_PATH = REPO_ROOT / "reports" / "hw03" / "questions.yaml"
RAW_OUTPUT_DIR = REPO_ROOT / "reports" / "hw03" / "raw"


def load_questions():
    with open(QUESTIONS_PATH, "r") as f:
        data = yaml.safe_load(f)
    return data["questions"]


def run_all():
    RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    questions = load_questions()
    print(f"Loaded {len(questions)} questions from {QUESTIONS_PATH}")

    indexes = build_indexes()

    all_rows = []
    for q in questions:
        qid = q["id"]
        query_text = q["question"]
        for technique, (nodes, index) in indexes.items():
            rows = compare_query(
                technique=technique,
                nodes=nodes,
                index=index,
                query=query_text,
                question_id=qid,
            )
            all_rows.extend(rows)

    # --- Save as JSONL (one row per line -- easy to append/stream) ---
    jsonl_path = RAW_OUTPUT_DIR / "retrieval_results.jsonl"
    with open(jsonl_path, "w") as f:
        for row in all_rows:
            f.write(json.dumps(row) + "\n")
    print(f"\nSaved {len(all_rows)} rows to {jsonl_path}")

    # --- Save as full JSON (all rows, one array) ---
    json_path = RAW_OUTPUT_DIR / "retrieval_results.json"
    with open(json_path, "w") as f:
        json.dump(all_rows, f, indent=2)
    print(f"Saved {json_path}")

    # --- Save as CSV (for the summary tables) ---
    csv_path = RAW_OUTPUT_DIR / "retrieval_results.csv"
    if all_rows:
        fieldnames = list(all_rows[0].keys())
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"Saved {csv_path}")

    return all_rows


if __name__ == "__main__":
    run_all()
