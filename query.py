import os
from groq import Groq
from dotenv import load_dotenv
from retriever import get_embedding_model, embed_and_store, retrieve
from ingest import load_documents, chunk_documents

# Load environment variables from .env
load_dotenv()

# Groq model to use for generation
GROQ_MODEL = "llama-3.3-70b-versatile"

# Grounding system prompt — instructs LLM to answer only from retrieved context
SYSTEM_PROMPT = """You are a helpful assistant for university students looking for 
information about campus dining halls.

Answer the user's question using ONLY the information provided in the documents below.
Do not use any outside knowledge. If the documents do not contain enough information 
to answer the question, respond with: 
"I don't have enough information about that in my sources."

Always end your response with a "Sources:" section listing the document filenames 
you used to answer the question."""


def build_context(chunks):
    """Format retrieved chunks into a context string for the LLM."""
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Document {i} - {chunk['source']}]\n{chunk['text']}"
        )
    return "\n\n".join(context_parts)


def ask(question, collection, model):
    """Retrieve relevant chunks and generate a grounded answer."""
    # Step 1: Retrieve top-k relevant chunks
    chunks = retrieve(question, collection, model)

    if not chunks:
        return {
            "answer": "I don't have enough information about that in my sources.",
            "sources": [],
            "chunks": []
        }

    # Step 2: Build context from retrieved chunks
    context = build_context(chunks)

    # Step 3: Build prompt with context
    user_prompt = f"""Documents:
{context}

Question: {question}"""

    # Step 4: Call Groq API
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=1000
    )

    answer = response.choices[0].message.content

    # Step 5: Collect unique sources
    sources = list(set(chunk["source"] for chunk in chunks))

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks
    }


def test_grounding(collection, model):
    """Test grounding with evaluation plan questions and one out-of-scope question."""
    test_questions = [
        # In-scope questions
        "What do students say about wait times at Main Hall during lunch?",
        "What are the best late-night food options on campus after 8pm?",
        # Out-of-scope question — system should refuse
        "What is the best laptop to buy for college?"
    ]

    print("\n" + "="*60)
    print("GROUNDED GENERATION TEST")
    print("="*60)

    for question in test_questions:
        print(f"\nQuestion: {question}")
        print("-" * 50)
        result = ask(question, collection, model)
        print(f"Answer:\n{result['answer']}")
        print(f"\nSources: {result['sources']}")
        print()


if __name__ == "__main__":
    # Load documents and chunks
    documents = load_documents()
    chunks = chunk_documents(documents)

    # Load embedding model
    model = get_embedding_model()

    # Load existing ChromaDB collection (no reset — already embedded)
    from retriever import chromadb, CHROMA_DIR, COLLECTION_NAME
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    # Run grounding test
    test_grounding(collection, model)