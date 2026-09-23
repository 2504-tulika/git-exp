"""
Vector store lifecycle: owns the one ChromaDB collection our RAG pipeline
reads from and writes to.

ingestion.py calls get_collection() (via reset_collection()) to upsert
policy chunks; retriever.py calls get_collection() to query them. Neither
of those files talks to ChromaDB directly -- this is the only file that
does, so if we ever swap ChromaDB for FAISS or another store, this is the
only file that changes.
"""

import chromadb
from chromadb.utils import embedding_functions

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "policy_clauses"

_client = None
_collection = None


def get_client():
    """Return a singleton persistent ChromaDB client, creating it on first use."""
    global _client
    if _client is None:
        logger.info(f"Opening ChromaDB persistent client at {settings.vector_store_dir}")
        _client = chromadb.PersistentClient(path=settings.vector_store_dir)
    return _client


def _embedding_function():
    """
    Same embedding model for both writes (ingestion) and reads (retrieval)
    -- if these ever drift apart, similarity scores become meaningless.
    Pulled from settings so there's exactly one place that names the model.
    """
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=settings.embedding_model_name
    )


def get_collection():
    """Return the singleton 'policy_clauses' collection, creating it if needed."""
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=_embedding_function(),
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"Collection '{COLLECTION_NAME}' ready "
            f"({_collection.count()} chunks currently stored)"
        )
    return _collection


def reset_collection():
    """
    Drop and recreate the collection. ingestion.py calls this before every
    run so stale chunks (e.g. from a policy PDF that changed or was
    removed) don't linger alongside the new ones -- ingestion is always a
    full rebuild, never an incremental patch.
    """
    global _collection
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
        logger.info(f"Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass  # collection didn't exist yet -- nothing to delete
    _collection = None
    return get_collection()
