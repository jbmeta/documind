import pathlib
from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np # Import numpy

# --- Constants ---
DB_PATH = "./documind_db"
EMBED_MODEL = 'all-MiniLM-L6-v2'
COLLECTION_NAME = "documind_collection"

class AICore:
    """Manages all AI-related operations, including models and the vector database."""
    def __init__(self):
        print("[LOG] AI Core: Initializing...")
        self.embedding_model = None
        self.collection = None
        try:
            print("[LOG] AI Core: Loading SentenceTransformer model...")
            self.embedding_model = SentenceTransformer(EMBED_MODEL)
            print("[LOG] AI Core: Model loaded successfully.")

            print("[LOG] AI Core: Initializing persistent database client...")
            client = chromadb.PersistentClient(path=str(pathlib.Path(DB_PATH).absolute()))
            print("[LOG] AI Core: Database client initialized.")
            
            print("[LOG] AI Core: Getting or creating collection...")
            self.collection = client.get_or_create_collection(name=COLLECTION_NAME)
            print(f"[LOG] AI Core: Initialization complete. Documents in collection: {self.collection.count()}")
        except Exception as e:
            print(f"[FATAL LOG] AI Core: Failed to initialize: {e}")

    def embed_and_store(self, chunks: list[str], metadata: list[dict], source_path: pathlib.Path):
        """Embeds text chunks in batches and stores them in the persistent vector database."""
        if not self.embedding_model or not self.collection:
            print("[LOG] AI Core: Not initialized. Cannot perform embedding.")
            return

        total_chunks = len(chunks)
        BATCH_SIZE = 32

        for i in range(0, total_chunks, BATCH_SIZE):
            batch_chunks = chunks[i:i + BATCH_SIZE]
            batch_metadata = metadata[i:i + BATCH_SIZE]
            batch_ids = [f"{source_path.name}_{j}" for j in range(i, i + len(batch_chunks))]

            try:
                print(f"[LOG] AI Core: Starting to encode batch {i//BATCH_SIZE + 1} for {source_path.name}...")
                # Encode the chunks, result is a numpy array
                batch_embeddings_np = self.embedding_model.encode(batch_chunks)
                print(f"[LOG] AI Core: Finished encoding batch {i//BATCH_SIZE + 1}.")

                # --- THIS IS THE FIX ---
                # Explicitly convert numpy array to a list of lists of standard Python floats.
                # This is more robust than a simple .tolist() in case of C++ binding issues.
                batch_embeddings = [[float(x) for x in emb] for emb in batch_embeddings_np]
                # --- END OF FIX ---

                # --- New Detailed Logging Before the Crash Point ---
                print(f"[LOG] AI Core: Preparing to add batch {i//BATCH_SIZE + 1} to DB.")
                print(f"[LOG] Data types: embeddings={type(batch_embeddings)}, docs={type(batch_chunks)}, meta={type(batch_metadata)}, ids={type(batch_ids)}")
                print(f"[LOG] Data lengths: embeddings={len(batch_embeddings)}, docs={len(batch_chunks)}, meta={len(batch_metadata)}, ids={len(batch_ids)}")
                if batch_embeddings:
                    print(f"[LOG] Embeddings sample type: {type(batch_embeddings[0])}, element type: {type(batch_embeddings[0][0])}")
                # --- End of New Logging ---

                self.collection.add(
                    embeddings=batch_embeddings,
                    documents=batch_chunks,
                    metadatas=batch_metadata,
                    ids=batch_ids
                )
                print(f"[LOG] AI Core: Finished adding batch {i//BATCH_SIZE + 1} to DB.")

            except Exception as e:
                print(f"[FATAL LOG] AI Core: Error processing batch for {source_path.name}: {e}")

        print(f"[LOG] AI Core: Successfully stored all chunks for {source_path.name}.")