"""All-MiniLM-L6-v2 embedding utilities for API usage."""

from functools import lru_cache
from typing import List

import numpy as np
import torch
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(MODEL_NAME, device=device)
    return model


def embed_text(text: str) -> np.ndarray:
    if not text or not text.strip():
        raise ValueError("Text input cannot be empty.")
    model = _load_model()
    return model.encode(text, convert_to_numpy=True, normalize_embeddings=True)


def embed_texts(texts: List[str]) -> np.ndarray:
    clean = [t for t in texts if t and t.strip()]
    if not clean:
        raise ValueError("Text list cannot be empty.")
    model = _load_model()
    return model.encode(
        clean,
        batch_size=8,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )


__all__ = ["embed_text", "embed_texts", "MODEL_NAME"]
