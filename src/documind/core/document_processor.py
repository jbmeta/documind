import fitz  # PyMuPDF
from pathlib import Path

def extract_text_from_pdf(pdf_path: Path) -> str | None:
    """
    Extracts all text from a given PDF file.
    Returns the text content as a string, or None if an error occurs.
    """
    try:
        doc = fitz.open(pdf_path)
        text = "".join(page.get_text() for page in doc)
        doc.close()
        return text
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