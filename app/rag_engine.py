import os
import fitz  # PyMuPDF
import chromadb
from app.ollama_client import ask_ai, get_embedding

# ─── CONFIG ───────────────────────────────────────────────
PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "deep_work.pdf")
CHUNK_SIZE = 800        # characters per chunk
CHUNK_OVERLAP = 100     # overlap so we don't cut sentences in half
COLLECTION_NAME = "deep_work_book"
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
# ──────────────────────────────────────────────────────────

# Initialize ChromaDB (a local vector database)
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Step 1: Read the entire PDF and return all text as one string."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Step 2: Split the long text into smaller chunks.
    We use overlap so that if a sentence is cut at the boundary,
    it still appears (fully) in the next chunk.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:  # skip empty chunks
            chunks.append(chunk)
        start = end - overlap  # move forward but overlap with previous
    return chunks


def build_vector_store():
    """
    Steps 3 & 4: Generate embeddings for every chunk and store them in ChromaDB.
    Only runs once. After that, the data is saved on disk.
    """
    if collection.count() > 0:
        print(f"✅ Vector store already built ({collection.count()} chunks). Skipping.")
        return

    print("📖 Step 1: Extracting text from PDF...")
    text = extract_text_from_pdf(PDF_PATH)
    print(f"   Extracted {len(text)} characters")

    print("✂️  Step 2: Chunking text...")
    chunks = chunk_text(text)
    print(f"   Created {len(chunks)} chunks")

    print("🔢 Step 3: Generating embeddings (this may take a minute)...")
    embeddings = []
    for i, chunk in enumerate(chunks):
        emb = get_embedding(chunk)
        embeddings.append(emb)
        if (i + 1) % 20 == 0:
            print(f"   Embedded {i + 1}/{len(chunks)} chunks...")

    print("💾 Step 4: Storing in ChromaDB...")
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    print(f"✅ Done! Stored {len(chunks)} chunks in the vector database.")


def retrieve_relevant_chunks(query: str, n_results: int = 3) -> list[str]:
    """
    Step 5: Convert the user's question into a vector,
    then find the most similar chunks from the book.
    """
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results["documents"][0]


def build_prompt(query: str, retrieved_chunks: list[str]) -> str:
    """
    Step 6: Build a custom prompt that combines:
      - Instructions for the AI
      - The retrieved context from the book
      - The user's question
    """
    context = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""You are a Deep Work Coach — an expert assistant trained specifically 
on Cal Newport's book "Deep Work: Rules for Focused Success in a Distracted World".

Answer the user's question using ONLY the context provided below from the book.
If the context does not contain enough information to answer, say:
"I couldn't find that in the book. Try rephrasing your question."

Quote the book when relevant. Be concise but thorough.

═══════════════════════════════════════════════════════════
CONTEXT FROM THE BOOK:
═══════════════════════════════════════════════════════════

{context}

═══════════════════════════════════════════════════════════
USER'S QUESTION: {query}
═══════════════════════════════════════════════════════════

YOUR ANSWER:"""
    return prompt


def ask_coach(question: str) -> dict:
    """
    The full RAG pipeline:
      1. Retrieve relevant chunks from the book
      2. Build a custom prompt with that context
      3. Send to the LLM
      4. Return the answer + the sources used
    """
    # Step 5: Retrieve
    chunks = retrieve_relevant_chunks(question, n_results=3)

    # Step 6: Build prompt
    prompt = build_prompt(question, chunks)

    # Step 7: Generate
    answer = ask_ai(prompt)

    return {
        "answer": answer,
        "sources": chunks
    }