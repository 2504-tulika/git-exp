"""
RAG retrieval: given a natural-language question (and, usually, a specific
policy_id), return the most relevant policy clause chunks from the vector
store.

This is the only file mcp/tools/policy_tool.py needs to import -- it
never touches ChromaDB or the embedding model directly.
"""

from src.rag.vector_store import get_collection
from src.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_TOP_K = 4


def retrieve_policy_clauses(query, policy_id=None, top_k=DEFAULT_TOP_K):
    """
    Return the top_k chunks most relevant to `query`, as a list of dicts:
    {policy_id, policy_type, sub_type, section, text, distance}.

    Pass policy_id to restrict the search to one policy's own clauses --
    this is what stops the agent from ever citing a different customer's
    policy wording in its recommendation.
    """
    collection = get_collection()

    where = {"policy_id": policy_id} if policy_id else None
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where,
    )

    if not results["ids"] or not results["ids"][0]:
        logger.warning(f"No chunks retrieved for query={query!r} policy_id={policy_id!r}")
        return []

    clauses = []
    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]
        clauses.append({
            "policy_id": metadata["policy_id"],
            "policy_type": metadata["policy_type"],
            "sub_type": metadata["sub_type"],
            "section": metadata["section"],
            "text": results["documents"][0][i],
            "distance": results["distances"][0][i],
        })
    return clauses


def retrieve_for_claim(claim_type, incident_description, policy_id, top_k=DEFAULT_TOP_K):
    """
    Convenience wrapper for the coverage-check tool: builds the retrieval
    query straight from the claim's own fields instead of making every
    caller hand-write a query string.

    incident_description is free text taken directly from the claim, so
    it's used here only as retrieval input -- text to search with, never
    text that gets concatenated into a prompt as an instruction. That's
    what keeps this safe from prompt injection embedded in a claim; see
    utils/validators.py for the corresponding check on the agent side.
    """
    query = f"Coverage and exclusions for a {claim_type} claim: {incident_description}"
    return retrieve_policy_clauses(query, policy_id=policy_id, top_k=top_k)
