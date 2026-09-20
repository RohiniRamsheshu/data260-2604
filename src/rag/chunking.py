"""
HW3 - Part 2: Chunking setup for the RAG retrieval comparison.

Loads the local vulnerability corpus (corpus/*.txt) and builds nodes
using three different chunking techniques:
  1. Token-based        -> TokenTextSplitter
  2. Semantic            -> SemanticSplitterNodeParser
  3. Sentence-window     -> SentenceWindowNodeParser

Each technique's build_*_nodes() function returns a list of LlamaIndex
Node objects, ready to be indexed into an in-memory VectorStoreIndex.
"""

import os
import time
from pathlib import Path

from llama_index.core import SimpleDirectoryReader, Document
from llama_index.core.node_parser import (
    TokenTextSplitter,
    SemanticSplitterNodeParser,
    SentenceWindowNodeParser,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

CORPUS_DIR = Path(__file__).resolve().parents[2] / "corpus"
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Loaded once and reused across all three techniques -- semantic chunking
# needs the embed model directly (to measure topic-shift similarity while
# deciding where to cut); token and sentence-window chunking don't need it
# for splitting itself, but we embed with the same model later at index time.
_embed_model = None


def get_embed_model():
    """Lazily load and cache the HuggingFace embedding model."""
    global _embed_model
    if _embed_model is None:
        print(f"Loading embedding model: {EMBED_MODEL_NAME} ...")
        _embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
    return _embed_model


def load_corpus_documents() -> list[Document]:
    """Load every .txt file in corpus/ as a LlamaIndex Document."""
    if not CORPUS_DIR.exists():
        raise FileNotFoundError(f"Corpus directory not found: {CORPUS_DIR}")

    reader = SimpleDirectoryReader(input_dir=str(CORPUS_DIR), required_exts=[".txt"])
    documents = reader.load_data()
    print(f"Loaded {len(documents)} documents from {CORPUS_DIR}")
    return documents


# ---------------------------------------------------------------------------
# 1. Token-based chunking
# ---------------------------------------------------------------------------
def build_token_nodes(documents: list[Document], chunk_size=200, chunk_overlap=20):
    """
    Splits every document into fixed-size token chunks, blind to sentence
    or topic boundaries. Fast, simple, but can cut mid-sentence.
    """
    splitter = TokenTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separator=" ",
    )
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"[token] {len(nodes)} nodes (chunk_size={chunk_size}, overlap={chunk_overlap})")
    return nodes


# ---------------------------------------------------------------------------
# 2. Semantic chunking
# ---------------------------------------------------------------------------
def build_semantic_nodes(documents: list[Document], buffer_size=1, breakpoint_percentile=95):
    """
    Cuts where consecutive sentences' embeddings show a meaningful topic
    shift, rather than at a fixed token count. Uses the embed model
    directly to measure sentence-to-sentence similarity.
    """
    embed_model = get_embed_model()
    splitter = SemanticSplitterNodeParser(
        buffer_size=buffer_size,
        breakpoint_percentile_threshold=breakpoint_percentile,
        embed_model=embed_model,
    )
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"[semantic] {len(nodes)} nodes (buffer_size={buffer_size})")
    return nodes


# ---------------------------------------------------------------------------
# 3. Sentence-window chunking
# ---------------------------------------------------------------------------
def build_sentence_window_nodes(documents: list[Document], window_size=3):
    """
    Splits to individual sentences, but attaches `window_size` neighboring
    sentences on each side as metadata, so retrieval can still access
    surrounding context even though the indexed unit is one sentence.
    """
    splitter = SentenceWindowNodeParser.from_defaults(
        window_size=window_size,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"[sentence_window] {len(nodes)} nodes (window_size={window_size})")
    return nodes


if __name__ == "__main__":
    docs = load_corpus_documents()

    t0 = time.time()
    token_nodes = build_token_nodes(docs)
    t1 = time.time()
    semantic_nodes = build_semantic_nodes(docs)
    t2 = time.time()
    sw_nodes = build_sentence_window_nodes(docs)
    t3 = time.time()

    print("\n--- Chunk counts and build time ---")
    print(f"Token:            {len(token_nodes):4d} nodes, {t1 - t0:.2f}s")
    print(f"Semantic:         {len(semantic_nodes):4d} nodes, {t2 - t1:.2f}s")
    print(f"Sentence-window:  {len(sw_nodes):4d} nodes, {t3 - t2:.2f}s")
