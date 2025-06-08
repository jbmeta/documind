# Plan

## DocuMind: The Complete Project Plan (Revised & Consolidated)

### **1. Vision & Core Architecture**

**Vision:** To create a private, cross-platform desktop application that allows users to have intelligent conversations with their local documents. The application must be **stateful**, remembering all processed work between sessions, and **scalable**, capable of handling a large number of documents without performance degradation or crashes.

**Core Architecture: "Storage-First" Retrieval-Augmented Generation (RAG)**
This architecture is designed for persistence and robustness.

1. **Persistent Vector Database:** All document embeddings (the AI's "memory" of the text) will be stored permanently on the user's disk. This eliminates the need to re-process files every time the app starts and allows the system to scale beyond the limits of system RAM.
2. **Stateful Processing:** The application will keep a record of which files have already been processed. When scanning a folder, it will intelligently ignore unchanged files and only process new or modified ones.
3. **Decoupled & Threaded Logic:** The application will be split into three distinct layers (UI, Document Processing, AI Core). All heavy lifting will be performed in background threads, ensuring the user interface remains responsive at all times.

---

### **2. The Definitive Tech Stack**

* **Core Language**: **Python 3.10+**
* **Desktop GUI**: **PyQt6**
  * **Purpose**: To build a professional, responsive, and native-looking user interface for Windows and macOS.
* **PDF Parsing**: **PyMuPDF**
  * **Purpose**: For high-speed, accurate text extraction from PDF documents.
* **Text Embeddings**: **Sentence-Transformers** (`all-MiniLM-L6-v2` model)
  * **Purpose**: To convert text chunks into meaningful numerical vectors. The library automatically caches the model to disk, making it efficient.
* **Vector Database**: **ChromaDB (in Persistent Mode)**
  * **Purpose**: To store and efficiently query the text embeddings. By running in persistent mode, it saves all data to a local folder, making our application stateful.
* **Local LLM Runner (Development)**: **Ollama**
  * **Purpose**: To rapidly test and iterate with different local language models (like Llama 3 or Phi-3) via a simple API during development.
* **Local LLM Runner (Production/Distribution)**: **`llama-cpp-python`**
  * **Purpose**: To embed the language model's reasoning engine directly into the final application. This removes the Ollama dependency and is essential for creating a standalone, distributable product.
* **Packaging Tool**: **PyInstaller**
  * **Purpose**: To bundle the entire Python application, including its dependencies, into a single, double-clickable executable for non-technical users.

---

### **3. Comprehensive Implementation Roadmap**

This is the step-by-step guide to building DocuMind from scratch.

#### **Phase 1: Application Foundation & UI**

* **Step 1: Project Setup**
  * Create the `DocuMind` project directory and a `documind` source sub-directory.
  * Initialize a Git repository.
  * Create and activate a Python virtual environment (`venv`).
  * Create a `.gitignore` file to exclude the `venv` folder, cache files, and the future database folder.
* **Step 2: UI Scaffolding**
  * Install PyQt6: `pip install PyQt6`.
  * Create the main application window (`main.py`) with all necessary UI widgets: folder selection button, file list, progress/log area, question input, and an "Ask" button.
  * Use PyQt layout managers (`QVBoxLayout`, `QHBoxLayout`) to ensure the UI is responsive.

#### **Phase 2: The Persistent & Scalable Backend**

* **Step 3: Architect the AI Core**
  * Create a new module: `documind/ai_core.py`.
  * Inside this module, initialize ChromaDB in **persistent mode** (`chromadb.PersistentClient(path="./documind_db")`).
  * Load the `SentenceTransformer` embedding model in this module. This ensures it's loaded only once.
* **Step 4: Implement the Document Processing Logic**
  * Create a new module: `documind/document_processor.py`.
  * Implement a function to **extract text** from a PDF using PyMuPDF.
  * Implement a function to **chunk the text** into meaningful paragraphs.
* **Step 5: Build the Robust Indexing Pipeline**
  * In `ai_core.py`, create an `embed_and_store` function. This function **must** implement **batch processing** (e.g., in batches of 32) to handle large documents without crashing. It will take text chunks and save their embeddings and metadata to the persistent ChromaDB.
  * In `document_processor.py`, create a high-level `process_document` function that orchestrates the process: it calls the text extractor and chunker, then passes the results to `ai_core.embed_and_store`.
* **Step 6: Implement Threaded UI Integration**
  * In `main.py`, create a `Worker` class that runs on a `QThread`.
  * When the "Select Folder" button is clicked, this `Worker` will be started.
  * The `Worker`'s job is to find all PDFs and, for each one, call the `process_document` function.
  * The `Worker` will use PyQt signals (`pyqtSignal`) to send real-time progress updates back to the UI (e.g., "Processing file X...", "Finished file Y"). This keeps the application from freezing.

#### **Phase 3: Querying and Answering**

* **Step 7: Implement the Query Logic**
  * In `ai_core.py`, create a `query_knowledge_base` function.
  * This function will take a user's question (string), embed it using the same SentenceTransformer model, and query the persistent ChromaDB to retrieve the most relevant text chunks and their source metadata.
* **Step 8: Implement Answer Generation**
  * In `ai_core.py`, create a `generate_answer` function.
  * This function will take the user's question and the retrieved context chunks.
  * It will construct a detailed prompt, instructing the LLM to answer based *only* on the provided context.
  * During development, this function will make an API call to the local Ollama server.
* **Step 9: Connect the "Ask" Button**
  * In `main.py`, connect the "Ask" button to a new slot method.
  * This method will launch a **new `QThread` and `Worker`** to handle the query process, preventing the UI from freezing while waiting for the LLM to respond.
  * The worker will call `query_knowledge_base` and then `generate_answer`.
  * It will use signals to send the final answer and citations back to the UI to be displayed.

#### **Phase 4: Finalization and Distribution**

* **Step 10: Integrate Production LLM Runner**
  * Modify `ai_core.py`. Add logic to use `llama-cpp-python` instead of making an API call to Ollama. This will involve loading a `.gguf` model file directly from disk.
* **Step 11: Implement One-Time Asset Download**
  * In `main.py`, on the first-ever launch, the application should check for the required `.gguf` LLM model file (which is several gigabytes).
  * If the file is missing, the app should show a "First-Time Setup" dialog and programmatically download the model from a source like Hugging Face, displaying a progress bar to the user.
* **Step 12: Package the Application**
  * Use **PyInstaller** to bundle the entire project into a single executable file.
  * Configure the PyInstaller script to correctly include any necessary assets.
* **Step 13: Test**
  * Perform thorough testing of the final executable on clean Windows and macOS machines to ensure the entire user journey—from first-time model download to document processing and querying—is smooth and error-free.
