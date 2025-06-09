import pathlib
from sentence_transformers import SentenceTransformer
import chromadb

# --- Constants ---
# Use a folder in the project directory for the persistent database
DB_PATH = "./documind_db"
# This is the embedding model we'll use
EMBED_MODEL = 'all-MiniLM-L6-v2'
# This is the collection name in ChromaDB
COLLECTION_NAME = "documind_collection"

class AICore:
    """Manages all AI-related operations, including models and the vector database."""

    def __init__(self):
        print("Initializing AI Core...")
        self.embedding_model = None
        self.collection = None

        try:
            # 1. Initialize Sentence Transformer Model
            # This model is automatically cached to disk by the library in your user home directory.
            self.embedding_model = SentenceTransformer(EMBED_MODEL)

            # 2. Initialize Persistent ChromaDB Client
            # This will create the 'documind_db' folder if it doesn't exist
            # and load the database from there if it does.
            client = chromadb.PersistentClient(path=DB_PATH)

            # 3. Get or create the collection
            self.collection = client.get_or_create_collection(name=COLLECTION_NAME)
            
            print(f"AI Core initialized successfully. Using database at: {DB_PATH}")
            print(f"Existing documents in collection: {self.collection.count()}")

        except Exception as e:
            print(f"FATAL: Failed to initialize AI Core: {e}")
            # In a real app, you might want to show a popup error message to the user.

    # We will add functions like embed_and_store() and query() here in the next steps.