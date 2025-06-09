import fitz
from pathlib import Path
from documind.core.ai_core import AICore

def extract_text_from_pdf(pdf_path: Path) -> str | None:
    try:
        with fitz.open(pdf_path) as doc:
            return "".join(page.get_text() for page in doc)
    except Exception as e:
        print(f"Error extracting text from {pdf_path.name}: {e}")
        return None

def chunk_text(text: str) -> list[str]:
    chunks = text.split('\n\n')
    return [chunk.strip() for chunk in chunks if len(chunk.strip()) > 150]

def process_document(pdf_path: Path, ai_core: AICore):
    """Orchestrates the processing of a single document."""
    # Check if document has already been processed
    if ai_core.has_document(pdf_path):
        print(f"[LOG] DocumentProcessor: Skipping already processed file: {pdf_path.name}")
        return

    print(f"Processing document: {pdf_path.name}")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return

    chunks = chunk_text(text)
    if not chunks:
        print(f"Could not extract meaningful chunks from {pdf_path.name}.")
        return
    
    # Pass chunks and the source path to the AI Core
    ai_core.embed_and_store(chunks, pdf_path)