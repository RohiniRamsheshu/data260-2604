import os
import re
from typing import List, Dict, Any

# Ensure required packages are installed:
# pip install langchain langchain-community chromadb sentence-transformers openai

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 1. Corpus Setup & Chunking
CORPUS_DIR = "corpus"
PERSIST_DIR = "chroma_db"

def build_vector_store():
    print("Loading documents from corpus...")
    loader = DirectoryLoader(CORPUS_DIR, glob="*.txt", loader_cls=TextLoader)
    raw_docs = loader.load()
    
    # Requirements: chunk_size=500, chunk_overlap=50
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_documents(raw_docs)
    
    # Assign metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"chunk_{i}"
        
    print(f"Total documents: {len(raw_docs)} | Total chunks created: {len(chunks)}")
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )
    return vector_store

# 2. Retrieval & Context Engineering Functions
def retrieve_top_k(vector_store, query: str, k: int = 3):
    docs_and_scores = vector_store.similarity_search_with_score(query, k=k)
    results = []
    for doc, score in docs_and_scores:
        results.append({
            "chunk_id": doc.metadata.get("chunk_id", "N/A"),
            "source": os.path.basename(doc.metadata.get("source", "unknown")),
            "text": doc.page_content,
            "score": float(score)
        })
    return results

def deduplicate_and_format_context(retrieved_chunks: List[Dict[str, Any]]) -> str:
    seen_texts = set()
    formatted_context = []
    
    for idx, chunk in enumerate(retrieved_chunks, 1):
        clean_text = chunk["text"].strip()
        if clean_text in seen_texts:
            continue
        seen_texts.add(clean_text)
        formatted_context.append(
            f"[Source {idx}: {chunk['source']} (ID: {chunk['chunk_id']})]\n{clean_text}"
        )
    
    return "\n\n".join(formatted_context)

# 3. Prompt Configurations
def generate_prompt(config: str, query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    if config == "A":
        # No RAG
        return f"Question: {query}"
    
    elif config == "B":
        # Basic RAG
        context = "\n\n".join([c["text"] for c in retrieved_chunks])
        return f"Context:\n{context}\n\nQuestion: {query}"
    
    elif config == "C":
        # Context-Engineered RAG
        context = deduplicate_and_format_context(retrieved_chunks)
        prompt = f"""You are a grounded assistant. Answer the user's question using ONLY the provided document context below.

Grounding Rules:
1. Answer using ONLY facts directly mentioned in the context.
2. Cite the source number (e.g., [Source 1]) for all facts.
3. If the context does not contain sufficient evidence to answer the question, state EXACTLY:
"I cannot answer this question from the provided documents"

Context:
{context}

Question: {query}
Answer:"""
        return prompt

# Test Set Definition
TEST_QUESTIONS = {
    "Q1": "What is the requirement for vulnerability response times?",
    "Q2": "How are session tokens generated and stored in the database?",
    "Q3": "What authentication procedures apply across system services?",
    "Q4": "What are the security logging guidelines?",
    "Q5": "What is the university policy for grading homework extra credit?", # Answer not in docs
    "Q6": "How many miles is it from San Francisco to Los Angeles?" # Unrelated
}

if __name__ == "__main__":
    vector_store = build_vector_store()
    
    print("\n" + "="*50)
    print("RUNNING PART 4 RAG EVALUATION MATRIX")
    print("="*50)
    
    for q_id, query in TEST_QUESTIONS.items():
        print(f"\n--- {q_id}: {query} ---")
        retrieved = retrieve_top_k(vector_store, query, k=3)
        
        print("\nRetrieved Chunks (k=3):")
        for chunk in retrieved:
            print(f"  * [{chunk['source']}] {chunk['chunk_id']} (Score: {chunk['score']:.4f})")
            
        for config in ["A", "B", "C"]:
            prompt = generate_prompt(config, query, retrieved)
            print(f"\n[Config {config} Prompt Generated - Length: {len(prompt)} chars]")
            