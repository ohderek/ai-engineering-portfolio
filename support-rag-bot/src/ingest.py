"""
Step 1: Document ingestion pipeline.

Loads a document, splits it into chunks, embeds each chunk,
and stores the embeddings in a local Chroma vector database.

Key concepts demonstrated:
- Document loading      : LangChain TextLoader reads any .txt file
- Text chunking         : RecursiveCharacterTextSplitter breaks the document
                          into overlapping chunks so context is not lost at
                          boundaries. chunk_size and chunk_overlap are the two
                          most important tuning parameters.
- Embeddings            : HuggingFace all-MiniLM-L6-v2 converts each chunk
                          into a 384-dimension vector. Runs locally — no API
                          key required for this step.
- Vector store (Chroma) : Stores the vectors on disk so ingestion only needs
                          to run once. Subsequent queries load from disk.
"""

from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rich.console import Console
from rich.progress import track

console = Console()

# ── Tuning parameters ─────────────────────────────────────────────────────────
CHUNK_SIZE = 500       # max characters per chunk
CHUNK_OVERLAP = 50     # characters shared between adjacent chunks
EMBED_MODEL = "all-MiniLM-L6-v2"  # fast, lightweight, runs locally
VECTOR_DB_PATH = "./vector_db"


def ingest(file_path: str) -> Chroma:
    """
    Full ingestion pipeline: load → chunk → embed → store.
    Returns the Chroma vector store ready for querying.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    console.print(f"\n[bold cyan]Loading:[/bold cyan] {path.name}")

    # ── 1. Load ───────────────────────────────────────────────────────────────
    loader = TextLoader(str(path))
    documents = loader.load()
    console.print(f"  Loaded {len(documents)} document(s)")

    # ── 2. Chunk ──────────────────────────────────────────────────────────────
    # RecursiveCharacterTextSplitter tries to split on paragraphs, then
    # sentences, then words — preserving semantic units where possible.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    console.print(f"  Split into [bold]{len(chunks)} chunks[/bold] "
                  f"(size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    # ── 3. Embed + Store ──────────────────────────────────────────────────────
    console.print(f"  Embedding with [bold]{EMBED_MODEL}[/bold] (runs locally)...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_PATH,
    )
    console.print(f"  [green]Stored {len(chunks)} vectors → {VECTOR_DB_PATH}[/green]\n")

    return vectorstore


def load_existing() -> Chroma:
    """Load a previously ingested vector store from disk."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings,
    )
