import os
import glob
import random


def load_documents(raw_dir="documents/raw"):
    """Load all .txt files from the raw directory."""
    documents = []
    txt_files = glob.glob(os.path.join(raw_dir, "*.txt"))

    for filepath in txt_files:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        if not text.strip():
            print(f"Warning: {filepath} is empty, skipping.")
            continue

        documents.append({
            "text": text,
            "source": os.path.basename(filepath)
        })
        print(f"Loaded: {os.path.basename(filepath)} ({len(text)} characters)")

    print(f"\nTotal documents loaded: {len(documents)}")
    return documents


def clean_text(text):
    """Remove metadata headers and excessive blank lines."""
    lines = text.splitlines()
    cleaned_lines = []
    blank_count = 0

    # Skip header metadata lines at the top of each document
    skip_prefixes = ("Source:", "URL:", "Date collected:", "Domain:")
    in_header = True

    for line in lines:
        # Stop skipping after the first --- separator
        if line.strip() == "---" and in_header:
            in_header = False
            continue

        if in_header and any(line.startswith(p) for p in skip_prefixes):
            continue

        # Remove excessive blank lines
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 1:
                cleaned_lines.append(line)
        else:
            blank_count = 0
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def split_text(text, chunk_size=500, chunk_overlap=50):
    """Split text into overlapping chunks by character count."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        # If not at the end, try to break at a sentence or newline
        if end < text_length:
            for sep in ["\n\n", "\n", ". ", " "]:
                pos = text.rfind(sep, start, end)
                if pos != -1:
                    end = pos + len(sep)
                    break

        chunk = text[start:end].strip()
        if len(chunk) >= 50:
            chunks.append(chunk)

        start = end - chunk_overlap

    return chunks


def chunk_documents(documents, chunk_size=500, chunk_overlap=50):
    """Split all documents into chunks."""
    all_chunks = []

    for doc in documents:
        cleaned = clean_text(doc["text"])
        chunks = split_text(cleaned, chunk_size, chunk_overlap)

        for i, chunk_text in enumerate(chunks):
            all_chunks.append({
                "text": chunk_text,
                "source": doc["source"],
                "chunk_index": i
            })

    print(f"Total chunks created: {len(all_chunks)}")
    return all_chunks


def inspect_chunks(chunks, n=5):
    """Print n random chunks for manual inspection."""
    print("\n" + "="*60)
    print(f"INSPECTING {n} RANDOM CHUNKS")
    print("="*60)

    sample = random.sample(chunks, min(n, len(chunks)))

    for i, chunk in enumerate(sample, 1):
        print(f"\n--- Chunk {i} ---")
        print(f"Source : {chunk['source']}")
        print(f"Index  : {chunk['chunk_index']}")
        print(f"Length : {len(chunk['text'])} characters")
        print(f"Content:\n{chunk['text']}")
        print()


if __name__ == "__main__":
    # Step 1: Load all documents
    documents = load_documents()

    # Step 2: Chunk all documents
    chunks = chunk_documents(documents)

    # Step 3: Inspect 5 random chunks
    inspect_chunks(chunks, n=5)

    # Step 4: Sanity check
    print("="*60)
    print("SANITY CHECK")
    print("="*60)
    print(f"Total chunks: {len(chunks)}")

    if len(chunks) < 50:
        print("Warning: fewer than 50 chunks — chunks may be too large.")
    elif len(chunks) > 2000:
        print("Warning: more than 2000 chunks — chunks may be too small.")
    else:
        print("Chunk count looks good (50-2000 range).")