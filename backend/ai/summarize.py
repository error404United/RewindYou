"""Lightweight wrapper around FLAN-T5 summarization for API usage."""

import os
from functools import lru_cache
from typing import Optional

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch


MODEL_NAME = os.getenv("SUMMARY_MODEL", "google/flan-t5-base")
MAX_INPUT_TOKENS = 2048
MAX_SUMMARY_TOKENS = 512
MIN_SUMMARY_TOKENS = 60


@lru_cache(maxsize=1)
def _load_components():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    return tokenizer, model, device


def summarize_text(text: str, max_length: Optional[int] = None) -> str:
    if not text or not text.strip():
        raise ValueError("Text to summarize cannot be empty.")

    tokenizer, model, device = _load_components()

    inputs = tokenizer(
        "Summarize the following notes in concise sentences:\n" + text,
        return_tensors="pt",
        max_length=MAX_INPUT_TOKENS,
        truncation=True,
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    summary_tokens = model.generate(
        **inputs,
        max_length=max_length or MAX_SUMMARY_TOKENS,
        min_length=MIN_SUMMARY_TOKENS,
        num_beams=4,
        repetition_penalty=2.5,
        length_penalty=0.7,
        early_stopping=True,
    )

    return tokenizer.decode(summary_tokens[0], skip_special_tokens=True)


__all__ = ["summarize_text", "MODEL_NAME", "MAX_INPUT_TOKENS"]



