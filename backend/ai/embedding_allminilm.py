"""
===========================================================
 All-MiniLM-L6-v2 Embedding Module for RewindYou
===========================================================

Integrates directly after your FLAN-T5 summarizer (summarize.py).
It reads the summary text, generates normalized 384-D embeddings,
and provides similarity and semantic search utilities.
"""

from sentence_transformers import SentenceTransformer, util
import numpy as np
import torch
import os
from typing import List, Tuple


class AllMiniLMEmbedder:
    """
    Wrapper for the SentenceTransformer 'all-MiniLM-L6-v2' model.
    Handles embedding generation, normalization, and similarity.
    """

    def __init__(self, device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[INFO] Loading All-MiniLM-L6-v2 model on {self.device} ...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2", device=self.device)
        print("[INFO] Model loaded successfully ✅")

    # ------------------------------------------------------
    # Embedding Generation
    # ------------------------------------------------------

    def embed_text(self, text: str) -> np.ndarray:
        """Generate a 384-dimensional normalized embedding for a single text."""
        if not text or not text.strip():
            raise ValueError("Text input cannot be empty.")
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding  # shape: (384,)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts at once."""
        clean_texts = [t for t in texts if t and t.strip()]
        if not clean_texts:
            raise ValueError("Text list cannot be empty.")
        embeddings = self.model.encode(
            clean_texts,
            batch_size=8,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings

    # ------------------------------------------------------
    # Similarity & Search
    # ------------------------------------------------------

    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings."""
        dot = np.dot(vec1, vec2)
        norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
        return float(dot / norm) if norm != 0 else 0.0

    def semantic_search(
        self,
        query: str,
        corpus: List[str],
        top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """Compare a query text against a list of corpus texts."""
        if not corpus:
            raise ValueError("Corpus cannot be empty.")
        query_emb = self.model.encode(query, convert_to_tensor=True, normalize_embeddings=True)
        corpus_embs = self.model.encode(corpus, convert_to_tensor=True, normalize_embeddings=True)
        cos_scores = util.cos_sim(query_emb, corpus_embs)[0]
        top_results = torch.topk(cos_scores, k=min(top_k, len(corpus)))
        return [(corpus[idx], float(score)) for idx, score in zip(top_results.indices, top_results.values)]


# ----------------------------------------------------------
# Integration Test: Use output from summarize.py
# ----------------------------------------------------------
if __name__ == "__main__":
    print("=== Testing Full AI Flow: FLAN-T5 → All-MiniLM-L6-v2 ===")

    # Check if summarize.py has produced a summary file
    summary_text = None
    if os.path.exists("summary.txt"):
        with open("summary.txt", "r", encoding="utf-8") as f:
            summary_text = f.read().strip()
    elif os.path.exists("input.txt"):
        # fallback if summary.txt not found
        print("[WARN] summary.txt not found; reading input.txt instead (for demo).")
        with open("input.txt", "r", encoding="utf-8") as f:
            summary_text = f.read().strip()

    if not summary_text:
        raise RuntimeError("No summary or input text found. Run summarize.py first.")

    # Initialize embedder
    embedder = AllMiniLMEmbedder()

    # Generate embedding
    embedding = embedder.embed_text(summary_text)
    print(f"\n✅ Embedding generated! Shape: {embedding.shape}")

    # Optional: show first few values (to verify numerically)
    print("First 10 embedding values:", np.round(embedding[:10], 4))

    # Small demo with query
    query = "Explain what DP is mainly about."
    results = embedder.semantic_search(query, [summary_text], top_k=1)
    print("\nTop match for query:")
    for text, score in results:
        print(f"  → Similarity: {score:.4f}")

    print("\n✅ End-to-end AI pipeline test completed successfully.")
