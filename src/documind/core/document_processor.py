import fitz  # PyMuPDF
from pathlib import Path
from documind.core.ai_core import AICore

def extract_text_from_pdf(pdf_path: Path) -> str | None:
    """
    Extracts all text from a given PDF file.
    Returns the text content as a string, or None if an error occurs.
    """
    try:
        with fitz.open(pdf_path) as doc:
            return "".join(page.get_text() for page in doc)
    except Exception as e:
        print(f"Error extracting text from {pdf_path.name}: {e}")
        return None

def chunk_text(text: str) -> list[str]:
    """
    Splits a long text into smaller, meaningful chunks.
    This simple strategy splits by paragraphs.
    """
    chunks = text.split('\n\n')
    # Filter out very small or empty chunks to avoid noise
    return [chunk.strip() for chunk in chunks if len(chunk.strip()) > 150]

def process_document(pdf_path: Path, ai_core: AICore):
    """Orchestrates the processing of a single document."""
    print(f"Processing document: {pdf_path.name}")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return

    chunks = chunk_text(text)
    if not chunks:
        print(f"Could not extract meaningful chunks from {pdf_path.name}.")
        return
    
    metadatas = [{'source': pdf_path.name} for _ in chunks]
    
    # Hand off to the AI Core for the heavy lifting
    ai_core.embed_and_store(chunks, metadatas, pdf_path)