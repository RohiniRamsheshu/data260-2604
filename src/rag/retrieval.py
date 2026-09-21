"""
HW3 - Part 2: Retrieval-only comparison across the three chunking
techniques.

For each technique, builds an in-memory VectorStoreIndex over its nodes,
then exposes compare_query(), which:
  - embeds the query and shows its dimension + first 8 values
  - retrieves top-k nodes
  - for each retrieved node, computes:
      * the vector store's own similarity score
      * cosine similarity between query embedding and the node's own
        embedding (computed explicitly, not just trusting the store)
      * chunk length and a short text preview
  - prints a table: rank, store_score, cosine_sim, chunk_len, preview
  - times the retrieval step (milliseconds)

Returns a list of dicts per call, ready to be written to CSV/JSON/JSONL
by run_comparison.py.
"""

import time
import numpy as np

from llama_index.core import VectorStoreIndex, Settings

from chunking import (
    load_corpus_documents,
    build_token_nodes,
    build_semantic_nodes,
    build_sentence_window_nodes,
    get_embed_model,
)

TOP_K = 5


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Standard cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def build_indexes():
    """
    Loads the corpus once, builds nodes for all three techniques, and
    returns a dict of {technique_name: (nodes, VectorStoreIndex)}.
    """
    embed_model = get_embed_model()
    Settings.embed_model = embed_model  # global default used by VectorStoreIndex

    documents = load_corpus_documents()

    technique_nodes = {
        "token": build_token_nodes(documents),
        "semantic": build_semantic_nodes(documents),
        "sentence_window": build_sentence_window_nodes(documents),
    }

    indexes = {}
    for name, nodes in technique_nodes.items():
        print(f"Building in-memory VectorStoreIndex for '{name}' ({len(nodes)} nodes)...")
        index = VectorStoreIndex(nodes, embed_model=embed_model)
        indexes[name] = (nodes, index)

    return indexes


def compare_query(technique: str, nodes, index, query: str, top_k: int = TOP_K, question_id: str = ""):
    """
    Runs one retrieval-only comparison for a single technique + query.
    Prints a results table and returns a list of row-dicts for logging.
    """
    embed_model = Settings.embed_model

    # 1. Embed the query, show dimension + first 8 values
    query_embedding = embed_model.get_query_embedding(query)
    print(f"\n=== Technique: {technique} | Query: {query!r} ===")
    print(f"Query embedding dim: {len(query_embedding)}")
    print(f"Query embedding[:8]: {[round(v, 4) for v in query_embedding[:8]]}")

    # 2. Retrieve top-k, timing the retrieval step
    retriever = index.as_retriever(similarity_top_k=top_k)
    t0 = time.perf_counter()
    results = retriever.retrieve(query)
    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000

    # 3. For each retrieved node: store score, explicit cosine sim, chunk len, preview
    doc_vectors = []
    rows = []
    print(f"{'rank':<5}{'store_score':<13}{'cosine_sim':<12}{'chunk_len':<11}preview")
    for rank, node_with_score in enumerate(results, start=1):
        node = node_with_score.node
        store_score = node_with_score.score if node_with_score.score is not None else float("nan")

        chunk_text = node.get_content()
        node_embedding = embed_model.get_text_embedding(chunk_text)
        doc_vectors.append(node_embedding)

        cos_sim = cosine_similarity(query_embedding, node_embedding)
        chunk_len = len(chunk_text)
        preview = chunk_text[:160].replace("\n", " ")

        print(f"{rank:<5}{store_score:<13.4f}{cos_sim:<12.4f}{chunk_len:<11}{preview}")

        rows.append({
            "question_id": question_id,
            "technique": technique,
            "query": query,
            "rank": rank,
            "store_score": round(store_score, 6),
            "cosine_sim": round(cos_sim, 6),
            "chunk_len": chunk_len,
            "preview": preview,
            "source_file": node.metadata.get("file_name", "unknown"),
            "latency_ms": round(latency_ms, 3),
        })

    # 4. Shapes, for the assignment's explicit requirement
    query_vec_shape = (len(query_embedding),)
    doc_vecs_shape = (len(doc_vectors), len(doc_vectors[0]) if doc_vectors else 0)
    print(f"Query vector shape: {query_vec_shape}")
    print(f"Stacked doc vectors shape: {doc_vecs_shape}")
    print(f"Retrieval latency: {latency_ms:.3f} ms")

    return rows


if __name__ == "__main__":
    indexes = build_indexes()

    test_query = "What version of lodash fixes the prototype pollution vulnerability?"
    for technique, (nodes, index) in indexes.items():
        compare_query(technique, nodes, index, test_query, question_id="smoke_test")
