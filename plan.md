# Plan of Action

## DocuMind: The Complete Project Plan

### **1. Vision & Core Architecture**

**Vision:** To create a private, cross-platform desktop application that allows users to have intelligent conversations with their documents. The application will be **stateful** and **scalable**, allowing users to build a persistent library of documents by **adding files directly** via a file picker or by **dragging and dropping them** into the application.

**Core Architecture: "Storage-First" & "Design-First"**
The architecture is designed for persistence, scalability, and a superior user experience.

1. **Persistent Vector Database:** All document embeddings—the AI's "memory" of the text—will be stored permanently on the user's disk. This allows the application to remember documents between sessions.
2. **Stateful Processing with File Checksums:** The application will maintain a record of every processed file. When files are added, it will intelligently ignore duplicates and only process new or modified documents, saving significant time and computational resources.
3. **Decoupled & Threaded Logic:** A clean separation between the UI, document processing, and AI core layers ensures maintainability. All intensive work is performed in background threads, keeping the UI fast and responsive.

***

### **2. The Definitive Tech Stack**

The technology stack remains the same, as PyQt6 has excellent built-in support for all our UI requirements.

* **Core Language**: **Python 3.10+**
* **Desktop GUI**: **PyQt6**
* **UI Assets**: **Feather Icons** (or a similar open-source SVG icon set).
* **PDF Parsing**: **PyMuPDF**
* **Vector Database**: **ChromaDB (in Persistent Mode)**
* **Text Embeddings**: **Sentence-Transformers** (`all-MiniLM-L6-v2` model)
* **Local LLM Runner (Development)**: **Ollama**
* **Local LLM Runner (Production/Distribution)**: **`llama-cpp-python`**
* **Packaging Tool**: **PyInstaller**

***

### **3. Comprehensive Implementation Roadmap**

This is the step-by-step guide to building the complete application with the new file handling requirements.

#### **Phase 1: A Modern UI Foundation with Direct File Input**

* **Step 1: Project Setup & Asset Gathering**
  * Create the project structure (`DocuMind/documind`), Git repository, and Python virtual environment.
  * Create an `assets` folder and add a `style.qss` file and selected `.svg` icons.
  * Create a `.gitignore` file.

* **Step 2: Build the Advanced UI Layout for Drag-and-Drop**
  * Install PyQt6: `pip install PyQt6`.
  * In `main.py`, build the two-pane `QSplitter` layout.
  * The "Select Folder" button will be renamed to **Add Documents**.
  * **Enable Drag-and-Drop**: In the main window's `__init__` method, add `self.setAcceptDrops(True)`. This signals that the window is a valid drop target.

* **Step 3: Implement File Handling Events**
  * **File Picker Logic**: Connect the "Add Documents..." button to a slot that opens a `QFileDialog`. Use `getOpenFileNames` to allow the user to select one or more PDF files.
  * **Drag-and-Drop Logic**: Override two methods in your main window class:
        1. `dragEnterEvent(event)`: This method checks if the data being dragged over the window contains file paths (`event.mimeData().hasUrls()`). If it does, it accepts the event, showing the user a visual cue (e.g., a plus icon).
        2. `dropEvent(event)`: This method is triggered when the user releases the mouse. It extracts the list of file paths from the event's MIME data.
  * Both the file picker and the drop event will ultimately produce a list of file paths. This list will be the trigger for the indexing pipeline.

* **Step 4: Apply Styling and Icons**
  * Load the `style.qss` file to apply a modern look and feel.
  * Use `QIcon` to apply icons to buttons.

#### **Phase 2: The Persistent & Scalable Backend**

* **Step 5: Architect the AI Core and Checksum Store**
  * Create `ai_core.py` and initialize the persistent ChromaDB and the SentenceTransformer model.
  * Implement a simple checksum manager (e.g., using a JSON file) to store the file paths and content hashes of processed documents.

* **Step 6: Build the Robust Indexing Pipeline**
  * In `main.py`, create a `QThread` worker. This worker will be started whenever a list of file paths is received (either from the file picker or a drop event).
  * The worker will receive the list of file paths.
  * For each file path in the list, the worker will:
        1. First, check if the file has already been processed and is unchanged by comparing its hash against the checksum store. If so, it will be skipped.
        2. If the file is new or modified, it will call the functions in `document_processor.py` to extract text and create chunks.
        3. The chunks are then passed to the `ai_core.py` module for batch embedding and storage in ChromaDB.
        4. Finally, the file's hash is added/updated in the checksum store.
  * The worker will use signals to update a `QProgressBar` in the UI, showing the progress of the batch of files being added.

#### **Phase 3: Querying and Answering**

* **Step 7: Implement Query and Answer Logic**
  * This phase remains the same. The functions in `ai_core.py` will embed the user's question, query the entire persistent database (which now contains the user-curated library of documents), and generate an answer with the LLM.

* **Step 8: Implement Responsive Querying in the UI**
  * This also remains the same. The "Ask" button will trigger a background worker, and the UI will show a loading indicator while waiting for a response to ensure the application never freezes.

#### **Phase 4: Finalization and Distribution**

* **Step 9: Integrate Production LLM Runner**
  * Modify `ai_core.py` to use `llama-cpp-python` and load a local `.gguf` model file.
* **Step 10: Implement One-Time Asset Downloader**
  * On the app's first launch, check for the required LLM model file and download it with a progress bar if it's missing.
* **Step 11: Package the Application**
  * Use **PyInstaller** to create the final, standalone executable.
* **Step 12: Test**
  * Thoroughly test the entire workflow on clean machines, paying special attention to the file picker, drag-and-drop functionality, and the stateful nature of the document library.
