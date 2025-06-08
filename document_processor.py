import os
import fitz  # PyMuPDF library
from pathlib import Path

def find_pdf_files(folder_path: str) -> list[Path]:
    """Finds all PDF files in a given folder, non-recursively."""
    if not folder_path or not os.path.isdir(folder_path):
        return []
    
    # Use pathlib for a modern, object-oriented approach to file paths
    return list(Path(folder_path).glob("*.pdf"))

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extracts all text from a given PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error processing {pdf_path.name}: {e}")
        return ""