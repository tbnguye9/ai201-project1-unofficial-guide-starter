import os
import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_documents, chunk_documents

# Initialize embedding model (runs locally, no API key needed)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "dining_hall_guides"
TOP_K = 4


def get_embedding_model():
    """Load the sentence transformer embedding model."""
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Embedding model loaded.")
    return model


def embed_and_store(chunks, model, reset=False):
    """Embed all chunks and store them in ChromaDB."""
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Reset collection if requested
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted existing collection: {COLLECTION_NAME}")
        except Exception:
            pass

    # Create or get collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    # Check if already populated
    existing = collection.count()
    if existing > 0 and not reset:
        print(f"Collection already has {existing} chunks. Skipping embedding.")
        print("Run with reset=True to re-embed.")
        return collection

    print(f"Embedding {len(chunks)} chunks...")

    # Prepare data for ChromaDB
    texts = [chunk["text"] for chunk in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"]
        }
        for chunk in chunks
    ]

    # Embed all texts at once
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings_list = embeddings.tolist()

    # Store in ChromaDB in batches of 100
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch_end = min(i + batch_size, len(chunks))
        collection.add(
            ids=ids[i:batch_end],
            documents=texts[i:batch_end],
            embeddings=embeddings_list[i:batch_end],
            metadatas=metadatas[i:batch_end]
        )
        print(f"Stored chunks {i} to {batch_end}")

    print(f"\nTotal chunks stored in ChromaDB: {collection.count()}")
    return collection


def retrieve(query, collection, model, top_k=TOP_K):
    """Retrieve the top-k most relevant chunks for a query."""
    # Embed the query
    query_embedding = model.encode([query]).tolist()

    # Query ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Format results
    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance": results["distances"][0][i]
        })

    return chunks


def test_retrieval(collection, model):
    """Test retrieval with 3 queries from the evaluation plan."""
    test_queries = [
        "What do students say about wait times at Main Hall during lunch?",
        "What are the best late-night food options on campus after 8pm?",
        "What meal plan tips do students recommend for best value?"
    ]

    print("\n" + "="*60)
    print("RETRIEVAL TEST")
    print("="*60)

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        results = retrieve(query, collection, model)

        for i, chunk in enumerate(results, 1):
            print(f"  Result {i}:")
            print(f"    Source  : {chunk['source']}")
            print(f"    Distance: {chunk['distance']:.4f}")
            print(f"    Preview : {chunk['text'][:150]}...")
            print()


if __name__ == "__main__":
    # Step 1: Load and chunk documents
    documents = load_documents()
    chunks = chunk_documents(documents)

    # Step 2: Load embedding model
    model = get_embedding_model()

    # Step 3: Embed and store in ChromaDB
    collection = embed_and_store(chunks, model, reset=True)

    # Step 4: Test retrieval
    test_retrieval(collection, model)