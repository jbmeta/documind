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
    """Manages AI operations and the persistent document library."""
    def __init__(self):
        print("[LOG] AI Core: Initializing...")
        self.embedding_model = None
        self.index = None
        self.document_library = []

        try:
            DATA_PATH.mkdir(exist_ok=True)
            print("[LOG] AI Core: Loading SentenceTransformer model...")
            self.embedding_model = SentenceTransformer(EMBED_MODEL)
            print("[LOG] AI Core: Model loaded successfully.")
            self._load_state()
        except Exception as e:
            print(f"[FATAL LOG] AI Core: Failed to initialize: {e}")

    def _load_state(self):
        """Loads the FAISS index and library, and validates that files exist."""
        if not (LIBRARY_FILE_PATH.exists() and INDEX_FILE_PATH.exists()):
            print("[LOG] AI Core: No existing library/index found. Creating new ones.")
            self.index = faiss.IndexFlatL2(VECTOR_DIMENSION)
            self.document_library = []
            return

        print(f"[LOG] AI Core: Loading existing library and FAISS index...")
        with open(LIBRARY_FILE_PATH, 'r') as f:
            loaded_library = json.load(f)
        
        loaded_index = faiss.read_index(str(INDEX_FILE_PATH))
        
        # --- HEALTH CHECK LOGIC ---
        print("[LOG] AI Core: Performing health check on document library...")
        valid_library = []
        valid_indices = []
        needs_resave = False

        # We assume a 1-to-1 mapping of chunks to vectors. We need to find all vectors for a given source.
        # This is complex with FAISS alone. For now, we'll handle the simpler case of cleaning the library.
        # A more robust solution would involve a mapping of document to vector IDs.
        
        # Simple health check: Validate file paths
        for i, doc_info in enumerate(loaded_library):
            if pathlib.Path(doc_info['source_path']).exists():
                valid_library.append(doc_info)
            else:
                print(f"[WARNING] Pruning missing file from library: {doc_info['source_path']}")
                needs_resave = True

        self.document_library = valid_library
        self.index = loaded_index # For now, we don't prune the index, just the library list.
                                  # Pruning FAISS is complex and can be added later if needed.
        
        if needs_resave:
            print("[LOG] AI Core: Resaving cleaned library...")
            # We only resave the library file, not the FAISS index yet.
            with open(LIBRARY_FILE_PATH, 'w') as f:
                json.dump(self.document_library, f, indent=4)

        print(f"[LOG] AI Core: Health check complete. Loaded {len(self.document_library)} valid documents.")

    def _save_state(self):
        """Saves the FAISS index and document library to disk."""
        print(f"[LOG] AI Core: Saving state to disk...")
        faiss.write_index(self.index, str(INDEX_FILE_PATH))
        with open(LIBRARY_FILE_PATH, 'w') as f:
            json.dump(self.document_library, f, indent=4)
        print("[LOG] AI Core: State saved successfully.")

    def get_document_list(self) -> list[str]:
        """Returns a list of display names for the documents in the library."""
        return [doc['display_name'] for doc in self.document_library]

    def has_document(self, file_path: pathlib.Path) -> bool:
        """Checks if a document already exists in the library."""
        return any(doc['source_path'] == str(file_path) for doc in self.document_library)

    def embed_and_store(self, chunks: list[str], source_path: pathlib.Path):
        """Embeds text chunks and adds them to the index and library."""
        if not self.embedding_model or self.index is None:
            return
            
        # Add to document library first
        self.document_library.append({
            'source_path': str(source_path),
            'display_name': source_path.name
        })

        embeddings = self.embedding_model.encode(chunks)
        self.index.add(embeddings.astype('float32'))
        
        self._save_state()