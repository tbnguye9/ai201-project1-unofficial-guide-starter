import chromadb
import gradio as gr
from dotenv import load_dotenv
from ingest import load_documents, chunk_documents
from retriever import get_embedding_model, CHROMA_DIR, COLLECTION_NAME
from query import ask

# Load environment variables
load_dotenv()

# Initialize pipeline once at startup
print("Initializing pipeline...")
documents = load_documents()
chunks = chunk_documents(documents)
model = get_embedding_model()

client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)
print("Pipeline ready.")


def handle_query(question):
    """Handle a user query and return answer + sources."""
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question, collection, model)

    # Format sources as bullet list
    sources_text = "\n".join(f"• {s}" for s in result["sources"])

    return result["answer"], sources_text


# Build Gradio UI
with gr.Blocks(title="The Unofficial Dining Guide") as demo:
    gr.Markdown("# 🍽️ The Unofficial Campus Dining Guide")
    gr.Markdown(
        "Ask anything about campus dining halls — wait times, meal plan tips, "
        "dietary options, late-night food, and more. "
        "Answers are grounded in real student reviews."
    )

    with gr.Row():
        with gr.Column(scale=4):
            inp = gr.Textbox(
                label="Your question",
                placeholder="e.g. What do students say about wait times at Main Hall?",
                lines=2
            )
        with gr.Column(scale=1):
            btn = gr.Button("Ask", variant="primary")

    answer = gr.Textbox(label="Answer", lines=10, interactive=False)
    sources = gr.Textbox(label="Sources", lines=4, interactive=False)

    # Example questions
    gr.Examples(
        examples=[
            "What do students say about wait times at Main Hall during lunch?",
            "What are the best late-night food options on campus after 8pm?",
            "What meal plan tips do students recommend for best value?",
            "Which dining hall is best for students with dietary restrictions?",
            "How does North Grill compare to Main Hall in food quality?"
        ],
        inputs=inp
    )

    # Wire up button and enter key
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()