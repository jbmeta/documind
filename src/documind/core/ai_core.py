import pathlib
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# --- Constants ---
DATA_PATH = pathlib.Path("./documind_data")
INDEX_FILE_PATH = DATA_PATH / "documind_index.faiss"
LIBRARY_FILE_PATH = DATA_PATH / "documind_library.json"
EMBED_MODEL = 'all-MiniLM-L6-v2'
VECTOR_DIMENSION = 384

class AICore:
    def __init__(self, status_callback=None):
        """Initializes AI Core, optionally sending status updates to a callback."""
        self.log = lambda message: print(f"[LOG] {message}") if status_callback is None else status_callback(message)
        
        self.log("AI Core: Initializing...")
        self.embedding_model = None
        self.index = None
        self.document_library = []

        try:
            DATA_PATH.mkdir(exist_ok=True)
            self.log("AI Core: Loading SentenceTransformer model...")
            self.embedding_model = SentenceTransformer(EMBED_MODEL)
            self.log("AI Core: Model loaded successfully.")
            self._load_state()
        except Exception as e:
            self.log(f"FATAL: Failed to initialize AI Core: {e}")
    
    # ... (all other methods remain exactly the same)
    def _load_state(self):
        """Loads the FAISS index and library, and validates that files exist."""
        if not (LIBRARY_FILE_PATH.exists() and INDEX_FILE_PATH.exists()):
            self.log("AI Core: No existing library/index found. Creating new ones.")
            self.index = faiss.IndexFlatL2(VECTOR_DIMENSION)
            self.document_library = []
            return

        self.log(f"AI Core: Loading existing library and FAISS index...")
        with open(LIBRARY_FILE_PATH, 'r') as f:
            loaded_library = json.load(f)
        
        loaded_index = faiss.read_index(str(INDEX_FILE_PATH))
        
        self.log("AI Core: Performing health check on document library...")
        valid_library = []
        needs_resave = False
        
        for i, doc_info in enumerate(loaded_library):
            if pathlib.Path(doc_info['source_path']).exists():
                valid_library.append(doc_info)
            else:
                self.log(f"[WARNING] Pruning missing file from library: {doc_info['source_path']}")
                needs_resave = True

        self.document_library = valid_library
        self.index = loaded_index
        
        if needs_resave:
            self.log("AI Core: Resaving cleaned library...")
            with open(LIBRARY_FILE_PATH, 'w') as f:
                json.dump(self.document_library, f, indent=4)

        self.log(f"AI Core: Health check complete. Loaded {len(self.document_library)} valid documents.")

    def _save_state(self):
        self.log("AI Core: Saving state to disk...")
        faiss.write_index(self.index, str(INDEX_FILE_PATH))
        with open(LIBRARY_FILE_PATH, 'w') as f:
            json.dump(self.document_library, f, indent=4)
        self.log("AI Core: State saved successfully.")

    def get_document_list(self) -> list[str]:
        return [doc['display_name'] for doc in self.document_library]

    def has_document(self, file_path: pathlib.Path) -> bool:
        return any(doc['source_path'] == str(file_path) for doc in self.document_library)

    def embed_and_store(self, chunks: list[str], source_path: pathlib.Path):
        if not self.embedding_model or self.index is None:
            return
        self.document_library.append({
            'source_path': str(source_path),
            'display_name': source_path.name
        })
        embeddings = self.embedding_model.encode(chunks)
        self.index.add(embeddings.astype('float32'))
        self._save_state()