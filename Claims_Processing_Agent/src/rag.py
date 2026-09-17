import chromadb

from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, ensure_folders_exist
from chunking import load_all_policy_chunks


def get_chroma_client():
    """Returns a ChromaDB client that saves to disk, so we don't have
    to re-embed everything every time the app starts."""
    ensure_folders_exist()
    return chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))


def build_vector_store():
    """
    Reads all policy chunks and embeds them into ChromaDB. Safe to run
    more than once - it deletes and rebuilds the collection each time,
    which keeps things simple while we're still developing.
    """
    client = get_chroma_client()

    # Start fresh each time so we don't end up with duplicate chunks
    # if this is run more than once.
    existing = [c.name for c in client.list_collections()]
    if CHROMA_COLLECTION_NAME in existing:
        client.delete_collection(CHROMA_COLLECTION_NAME)

    collection = client.create_collection(CHROMA_COLLECTION_NAME)

    chunks = load_all_policy_chunks()

    # ChromaDB needs a unique id per chunk, the chunk text itself, and a
    # metadata dict we can later filter on (e.g. only POL-1011's chunks).
    ids = [f"{c['policy_id']}_{c['part']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [{"policy_id": c["policy_id"], "tier": c["tier"], "part": c["part"]} for c in chunks]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)

    print(f"Embedded {len(chunks)} chunks into '{CHROMA_COLLECTION_NAME}'.")
    return collection


def get_collection():
    """Loads the existing collection (assumes build_vector_store() has
    already been run at least once)."""
    client = get_chroma_client()
    return client.get_collection(CHROMA_COLLECTION_NAME)


def search_policies(query, n_results=3, policy_id=None):
    """
    Searches the policy vector store for chunks relevant to `query`.

    If policy_id is given, only searches within that one policy - this
    is what stops the agent from accidentally pulling a clause from a
    similar-looking but wrong policy (e.g. mixing up two different
    water-damage endorsement amounts).
    """
    collection = get_collection()

    where_filter = {"policy_id": policy_id} if policy_id else None

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter,
    )

    # Reshape Chroma's slightly awkward nested-list result into a plain
    # list of dicts, which is easier for the rest of our code to use.
    matches = []
    for text, metadata, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        matches.append({"text": text, "metadata": metadata, "distance": distance})

    return matches


def get_policy_chunks(policy_id):
    """
    Returns all chunks for one policy_id, in PART I-V order, with no
    similarity ranking involved. Used when a tool already knows exactly
    which policy it needs (e.g. checking coverage) - since each policy
    only has 5 chunks, embedding-similarity search is more likely to
    misrank a short exclusion clause against the endorsement that
    overrides it (they share almost identical wording) than to help.
    """
    collection = get_collection()
    results = collection.get(where={"policy_id": policy_id})

    # collection.get() doesn't guarantee PART I-V order, so sort by the
    # "PART" numeral explicitly rather than trusting insertion order.
    part_order = {"PART I": 0, "PART II": 1, "PART III": 2, "PART IV": 3, "PART V": 4}
    zipped = list(zip(results["documents"], results["metadatas"]))
    zipped.sort(key=lambda x: part_order.get(x[1]["part"].split(" - ")[0], 99))

    return [{"text": doc, "metadata": meta} for doc, meta in zipped]

if __name__ == "__main__":
    # Build the store, then run a few test searches to sanity-check
    # retrieval before wiring this into the actual tools.
    build_vector_store()

    print("\nTest 1: water damage limit for POL-1011")
    for m in search_policies("what is the water damage coverage limit", policy_id="POL-1011", n_results=3):
        print(f"{m['metadata']['part']} (distance={m['distance']:.3f}) -> {m['text'][:150]}")
    
    print("\nTest 2: water damage limit for POL-1014 (should be a DIFFERENT amount)")
    for m in search_policies("what is the water damage coverage limit", policy_id="POL-1014", n_results=3):
        print(f"{m['metadata']['part']} (distance={m['distance']:.3f}) -> {m['text'][:150]}")

    print("\nTest 3: is roadside assistance covered for POL-1009")
    for m in search_policies("is roadside assistance covered", policy_id="POL-1009", n_results=3):
        print(m["metadata"]["part"], "->", m["text"][:200])