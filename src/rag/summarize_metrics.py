"""
HW3 - Part 2: Computes summary metrics (top-1 cosine, mean@k cosine,
chunk counts, avg chunk length, mean retrieval latency) per technique
from the raw retrieval_results.csv, for filling in METRICS.md.

Also reports total node/chunk counts per technique (from a fresh
chunking run) since that count isn't otherwise present in the
per-query retrieval CSV.
"""

import csv
from collections import defaultdict
from pathlib import Path

from chunking import (
    load_corpus_documents,
    build_token_nodes,
    build_semantic_nodes,
    build_sentence_window_nodes,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = REPO_ROOT / "reports" / "hw03" / "raw" / "retrieval_results.csv"


def summarize():
    rows = []
    with open(CSV_PATH, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["rank"] = int(row["rank"])
            row["cosine_sim"] = float(row["cosine_sim"])
            row["chunk_len"] = int(row["chunk_len"])
            row["latency_ms"] = float(row["latency_ms"])
            rows.append(row)

    by_technique = defaultdict(list)
    for row in rows:
        by_technique[row["technique"]].append(row)

    # chunk counts + avg length per technique (from a fresh chunking pass)
    print("Rebuilding chunks to report chunk counts / avg length...")
    docs = load_corpus_documents()
    node_sets = {
        "token": build_token_nodes(docs),
        "semantic": build_semantic_nodes(docs),
        "sentence_window": build_sentence_window_nodes(docs),
    }

    print("\n| Technique | Chunks | Avg chunk length | Top-1 cosine | Mean@k cosine | Mean retrieval latency (ms) |")
    print("|---|---|---|---|---|---|")

    for technique in ["token", "semantic", "sentence_window"]:
        technique_rows = by_technique[technique]

        # group by question_id to get top-1 (rank==1) and mean@k per question
        by_question = defaultdict(list)
        for r in technique_rows:
            by_question[r["question_id"]].append(r)

        top1_cosines = []
        mean_at_k_cosines = []
        for qid, qrows in by_question.items():
            qrows_sorted = sorted(qrows, key=lambda r: r["rank"])
            top1_cosines.append(qrows_sorted[0]["cosine_sim"])
            mean_at_k_cosines.append(sum(r["cosine_sim"] for r in qrows_sorted) / len(qrows_sorted))

        avg_top1 = sum(top1_cosines) / len(top1_cosines)
        avg_mean_at_k = sum(mean_at_k_cosines) / len(mean_at_k_cosines)
        avg_latency = sum(r["latency_ms"] for r in technique_rows) / len(technique_rows)

        nodes = node_sets[technique]
        n_chunks = len(nodes)
        avg_len = sum(len(n.get_content()) for n in nodes) / n_chunks

        print(f"| {technique} | {n_chunks} | {avg_len:.0f} | {avg_top1:.4f} | {avg_mean_at_k:.4f} | {avg_latency:.2f} |")


if __name__ == "__main__":
    summarize()
