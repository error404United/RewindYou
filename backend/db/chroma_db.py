"""ChromaDB helpers for vector storage and search."""

import os
from functools import lru_cache
from typing import Dict, List, Optional

import chromadb
from chromadb.api.models.Collection import Collection
from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def _client() -> chromadb.CloudClient:
    api_key = os.getenv("CHROMA_API_KEY")
    tenant = os.getenv("CHROMA_TENANT")
    database = os.getenv("CHROMA_DATABASE")
    if not api_key or not tenant or not database:
        raise RuntimeError("ChromaDB environment variables are missing.")
    return chromadb.CloudClient(api_key=api_key, tenant=tenant, database=database)


def get_collection(name: str = "rewindyou_memory") -> Collection:
    return _client().get_or_create_collection(name=name)


def add_embedding(
    doc_id: str,
    embedding: List[float],
    metadata: Optional[Dict] = None,
    collection_name: str = "rewindyou_memory",
) -> None:
    collection = get_collection(collection_name)
    collection.upsert(ids=[doc_id], embeddings=[embedding], metadatas=[metadata or {}])


def query_embeddings(
    query_embedding: List[float],
    where: Optional[Dict] = None,
    n_results: int = 5,
    collection_name: str = "rewindyou_memory",
) -> Dict:
    collection = get_collection(collection_name)
    # Only pass where if it's provided and not empty
    kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": n_results,
    }
    if where:
        kwargs["where"] = where
    
    return collection.query(**kwargs)


def delete_embedding(
    doc_id: str,
    collection_name: str = "rewindyou_memory",
) -> None:
    collection = get_collection(collection_name)
    collection.delete(ids=[doc_id])


__all__ = ["add_embedding", "delete_embedding", "query_embeddings", "get_collection"]