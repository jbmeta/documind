import pathlib
import json
import numpy as np
import faiss
import httpx
import asyncio
from sentence_transformers import SentenceTransformer

# --- Constants ---
DATA_PATH = pathlib.Path("./documind_data")
INDEX_FILE_PATH = DATA_PATH / "documind_index.faiss"
LIBRARY_FILE_PATH = DATA_PATH / "documind_library.json"
EMBED_MODEL = 'all-MiniLM-L6-v2'
VECTOR_DIMENSION = 384
OLLAMA_API_URL = "http://localhost:11434/api/generate"

class AICore:
    # ... (All methods remain the same except for generate_response) ...
    def __init__(self, status_callback=None):
        self.log = lambda message: print(f"[LOG] {message}") if status_callback is None else status_callback(message)
        self.log("AI Core: Initializing...")
        self.embedding_model = None
        self.index = None
        self.document_map = [] 
        try:
            DATA_PATH.mkdir(exist_ok=True)
            self.log("AI Core: Loading SentenceTransformer model...")
            self.embedding_model = SentenceTransformer(EMBED_MODEL)
            self.log("AI Core: Model loaded successfully.")
            self._load_state()
        except Exception as e:
            self.log(f"[FATAL LOG] AI Core: Failed to initialize: {e}")

    def _load_state(self):
        if LIBRARY_FILE_PATH.exists() and INDEX_FILE_PATH.exists():
            self.log(f"AI Core: Loading existing library and FAISS index...")
            with open(LIBRARY_FILE_PATH, 'r') as f:
                self.document_map = json.load(f)
            self.index = faiss.read_index(str(INDEX_FILE_PATH))
            if len(self.document_map) != self.index.ntotal:
                self.log(f"[WARNING] Mismatch between library ({len(self.document_map)}) and index ({self.index.ntotal}). Rebuilding.")
                self.index = faiss.IndexFlatL2(VECTOR_DIMENSION)
                self.document_map = []
                return
            self.log(f"AI Core: Loaded {self.index.ntotal} vectors/documents.")
        else:
            self.log("AI Core: No existing library/index found. Creating new ones.")
            self.index = faiss.IndexFlatL2(VECTOR_DIMENSION)
            self.document_map = []

    def _save_state(self):
        self.log("AI Core: Saving state to disk...")
        faiss.write_index(self.index, str(INDEX_FILE_PATH))
        with open(LIBRARY_FILE_PATH, 'w') as f:
            json.dump(self.document_map, f, indent=4)
        self.log("AI Core: State saved successfully.")

    def get_processed_files(self) -> list[str]:
        if not self.document_map: return []
        return sorted(list(set(item['metadata']['source'] for item in self.document_map)))

    def is_file_processed(self, file_path: pathlib.Path) -> bool:
        return any(item['metadata']['source'] == file_path.name for item in self.document_map)

    def add_document(self, chunks: list[str], source_path: pathlib.Path):
        if not self.embedding_model or self.index is None: return
        for chunk in chunks:
            self.document_map.append({
                'document': chunk,
                'metadata': {'source': source_path.name}
            })
        embeddings = self.embedding_model.encode(chunks)
        self.index.add(embeddings.astype('float32'))
        self._save_state()

    def query(self, user_question: str, num_results: int = 3) -> list[dict]:
        if self.index is None or self.index.ntotal == 0: return []
        question_embedding = self.embedding_model.encode([user_question])
        distances, indices = self.index.search(question_embedding.astype('float32'), num_results)
        return [self.document_map[i] for i in indices[0] if i < len(self.document_map)]

    async def generate_response(self, user_question: str, context: list[dict]) -> str:
        """Constructs a prompt and gets a response from the local LLM asynchronously."""
        if not context:
            return "I couldn't find any relevant information in your documents to answer that question."

        context_str = "\n\n---\n\n".join([item['document'] for item in context])
        sources = sorted(list(set([item['metadata']['source'] for item in context])))
        sources_str = ", ".join(sources)

        prompt = f"""You are a helpful question-answering assistant named DocuMind. Your task is to answer the user's question based *only* on the provided context.
Do not use any outside knowledge. If the answer is not available in the context, say "I could not find an answer in the provided documents."

Provide a clear and concise answer, then cite the source documents your answer is based on.

CONTEXT:
{context_str}

QUESTION:
{user_question}

ANSWER (be concise and cite your sources):
"""
        # --- THIS IS THE KEY CHANGE ---
        payload = {
            "model": "phi3:mini", # Use the smaller, more efficient model
            "prompt": prompt,
            "stream": False
        }
        # --- END OF CHANGE ---

        try:
            # Use an AsyncClient for non-blocking requests
            async with httpx.AsyncClient(timeout=180.0) as client:
                print(f"[LOG] AI Core: Sending prompt (length: {len(prompt)}) to Ollama...")
                response = await client.post(OLLAMA_API_URL, json=payload)
                print(f"[LOG] AI Core: Received response from Ollama with status code {response.status_code}.")
                response.raise_for_status()

            full_response = response.json().get("response", "").strip()
            return f"{full_response}\n\n**Sources:** {sources_str}"

        except httpx.TimeoutException:
            return "Error: The local AI model took too long to respond. Your system may be under heavy load."
        except httpx.RequestError as e:
            return f"Error: Could not connect to the local AI model. Please ensure Ollama is running.\n\n({e})"
        except Exception as e:
            return f"An unexpected error occurred while generating the answer: {e}"