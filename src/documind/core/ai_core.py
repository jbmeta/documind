import pathlib
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# --- Constants ---
INDEX_FILE_PATH = "./documind_index.faiss" # We'll save our index to a single file
EMBED_MODEL = 'all-MiniLM-L6-v2'
# The embedding model produces vectors of dimension 384
VECTOR_DIMENSION = 384

class AICore:
    """Manages AI operations using FAISS for vector storage."""
    def __init__(self):
        print("[LOG] AI Core: Initializing...")
        self.embedding_model = None
        self.index = None # This is our FAISS index
        self.documents = [] # A simple list to store the text chunks and metadata

        try:
            print("[LOG] AI Core: Loading SentenceTransformer model...")
            self.embedding_model = SentenceTransformer(EMBED_MODEL)
            print("[LOG] AI Core: Model loaded successfully.")

            # Load the FAISS index from disk if it exists
            index_path = pathlib.Path(INDEX_FILE_PATH)
            if index_path.exists():
                print(f"[LOG] AI Core: Loading existing FAISS index from {INDEX_FILE_PATH}...")
                self.index = faiss.read_index(str(index_path))
                # NOTE: For a complete solution, you would also save and load the `self.documents` list.
                # For now, we will rebuild it each time, but the expensive embeddings are saved.
                print(f"[LOG] AI Core: FAISS index loaded. Contains {self.index.ntotal} vectors.")
            else:
                print("[LOG] AI Core: No existing index found. Creating a new one.")
                # Create a new, empty index. IndexFlatL2 is a standard, exact-search index.
                self.index = faiss.IndexFlatL2(VECTOR_DIMENSION)
            
            print("[LOG] AI Core: Initialization complete.")
        except Exception as e:
            print(f"[FATAL LOG] AI Core: Failed to initialize: {e}")

    def embed_and_store(self, chunks: list[str], metadata: list[dict], source_path: pathlib.Path):
        """Embeds text chunks and adds them to the in-memory FAISS index."""
        if not self.embedding_model or self.index is None:
            print("[LOG] AI Core: Not initialized. Cannot perform embedding.")
            return

        print(f"[LOG] AI Core: Encoding {len(chunks)} chunks from {source_path.name}...")
        # The .encode() method returns a numpy array directly, which is what FAISS needs.
        embeddings = self.embedding_model.encode(chunks)
        print("[LOG] AI Core: Encoding complete.")

        # --- This is the new, robust way to add to the index ---
        print("[LOG] AI Core: Starting to add vectors to FAISS index...")
        self.index.add(embeddings.astype('float32')) # FAISS works best with float32
        print("[LOG] AI Core: Finished adding vectors to FAISS index.")
        
        # Store the corresponding text and metadata in our own list.
        # The vector at index `i` in FAISS corresponds to the document at index `i`.
        for i, chunk in enumerate(chunks):
            doc_info = {
                'document': chunk,
                'metadata': metadata[i]
            }
            self.documents.append(doc_info)

        # Save the updated index to disk
        print(f"[LOG] AI Core: Saving updated FAISS index to {INDEX_FILE_PATH}...")
        faiss.write_index(self.index, str(pathlib.Path(INDEX_FILE_PATH).absolute()))
        print("[LOG] AI Core: Index saved successfully.")