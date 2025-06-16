# DocuMind

DocuMind is a desktop application built with PyQt6 that leverages AI and natural language processing capabilities to interact with and process documents. It features a conversational interface, allowing users to query and extract information from their documents.

## Features

* **Interactive Chat Interface**: Engage in a conversational manner with your documents through a user-friendly chat interface.
* **PDF Document Processing**: Extracts text from PDF files using PyMuPDF and prepares it for AI processing.
* **AI-Powered Document Understanding**: Utilizes advanced AI models for semantic search and question answering over your documents.
* **Local LLM Integration**: Connects with a local Large Language Model (LLM) via Ollama for generating responses, ensuring data privacy and offline capability.
* **Theming**: Supports dynamic light and dark themes for a personalized user experience.
* **Splash Screen**: Provides a smooth startup experience with background initialization of AI models.

## Technical Details

DocuMind's AI core is built upon a Retrieval-Augmented Generation (RAG) architecture, leveraging several key components to provide intelligent document interaction:

* **Embedding Model**: Uses `SentenceTransformer` with the `all-MiniLM-L6-v2` model to convert document chunks and user queries into dense numerical vectors (embeddings). This allows for semantic understanding and comparison.
* **Vector Database**: Employs `FAISS` (specifically `IndexFlatL2`) as an in-memory vector store for efficient similarity search. Document embeddings are indexed, allowing for rapid retrieval of relevant content. The FAISS index and document metadata are persisted to `documind_data/documind_index.faiss` and `documind_data/documind_library.json` respectively.
* **Local LLM (Ollama)**: Integrates with a local Large Language Model served via Ollama. The application is configured to use the `phi3:mini` model by default for generating conversational responses.
* **Retrieval-Augmented Generation (RAG)**: When a user asks a question, DocuMind retrieves the most semantically similar document chunks from the FAISS index. These retrieved chunks are then provided as context to the local LLM, enabling it to generate accurate and contextually relevant answers based *only* on your documents.

### High-Level Workflow

The interaction with DocuMind follows a clear RAG workflow:

1. **Document Ingestion**:
    * User adds a PDF document via the UI.
    * `document_processor.py` extracts text from the PDF.
    * The extracted text is split into manageable chunks.
    * Each chunk is sent to the `ai_core.py`'s `add_document` method.
    * `ai_core.py` uses the `SentenceTransformer` to generate embeddings for each chunk.
    * These embeddings are added to the `FAISS` vector index, and the original text chunks with metadata are stored in `document_map`.
    * The FAISS index and document map are saved to disk (`documind_data/`).

2. **User Query Processing**:
    * User types a question into the chat interface.
    * The question is sent to `ai_core.py`'s `query` method.
    * `ai_core.py` uses the `SentenceTransformer` to generate an embedding for the user's question.
    * This question embedding is used to perform a similarity search in the `FAISS` index, retrieving the most relevant document chunks.

3. **Response Generation (RAG)**:
    * The retrieved relevant document chunks are passed as `context` to `ai_core.py`'s `generate_response` method.
    * A prompt is constructed, combining the user's question and the retrieved context.
    * This prompt is sent to the local LLM (Ollama, `phi3:mini` model) via its API.
    * The LLM generates an answer based *only* on the provided context.
    * The generated answer, along with citations to the source documents, is returned to the UI and displayed to the user.

```mermaid
graph TD
    A[User] --> B(Add PDF Document);
    B --> C{Document Processor};
    C --> D[Extract Text & Chunk];
    D --> E[Generate Embeddings];
    E --> F[Add to FAISS Index & Document Map];
    F --> G[Persist to documind_data/];

    A --> H(Ask Question);
    H --> I{AI Core};
    I --> J[Generate Question Embedding];
    J --> K[FAISS Search for Relevant Chunks];
    K --> L[Construct LLM Prompt with Context];
    L --> M[Local LLM (Ollama)];
    M --> N[Generate Answer];
    N --> O[Return Answer to User];

    subgraph Document Ingestion Flow
        B --> C; C --> D; D --> E; E --> F; F --> G;
    end

    subgraph Query & Response Flow
        H --> I; I --> J; J --> K; K --> L; L --> M; M --> N; N --> O;
    end
```

## Prerequisites

Before running DocuMind, you need to have **Ollama** installed and the `phi3:mini` model downloaded.

1. **Install Ollama**: Follow the instructions on the [Ollama website](https://ollama.com/download) to install it for your operating system.
2. **Download the `phi3:mini` model**: Open your terminal or command prompt and run:

    ```bash
    ollama pull phi3:mini
    ```

    Ensure Ollama is running in the background before starting DocuMind.

## Installation

To set up DocuMind locally, follow these steps:

1. **Clone the repository**:

    ```bash
    git clone https://github.com/jbmeta/documind.git
    cd documind
    ```

2. **Create a virtual environment** (recommended):

    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment**:
    * **Windows**:

        ```bash
        .\venv\Scripts\activate
        ```

    * **macOS/Linux**:

        ```bash
        source venv/bin/activate
        ```

4. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

    Note: The `requirements.txt` includes a direct editable install of the `documind` package itself.

## How to Run

After installing the dependencies and ensuring Ollama with `phi3:mini` is running, you can launch the application:

```bash
python -m documind.main 
```

This will launch the DocuMind application with a splash screen, followed by the main chat interface.

## Usage

Once the DocuMind application is running:

1. **Add Documents**: Use the interface to select and add PDF documents. The application will process them, extract text, chunk it, and add embeddings to its local FAISS index.
2. **Ask Questions**: Type your questions into the chat input field. The AI will retrieve relevant information from your processed documents and generate a response using the local LLM.
3. **Switch Themes**: Utilize the theme toggle (if available in the UI) to switch between light and dark modes.

## Troubleshooting

* **"Error: Could not connect to the local AI model. Please ensure Ollama is running."**: This error indicates that the DocuMind application cannot connect to the Ollama server.
  * **Solution**: Ensure Ollama is installed and running in the background. You can usually start it by launching the Ollama application or running `ollama serve` in your terminal.
* **"Error: The local AI model took too long to respond."**: This might happen if your system is under heavy load or the `phi3:mini` model is taking a long time to generate a response.
  * **Solution**: Close other demanding applications. If the issue persists, consider allocating more resources to Ollama or trying a smaller model if available.
* **"Mismatch between library and index. Rebuilding."**: This warning indicates an inconsistency between the stored document metadata and the FAISS index. DocuMind will automatically rebuild the index, which might take some time depending on the number of documents.

## Future Improvements and Recommendations

DocuMind is a functional application, but there are several areas where it could be further improved or expanded:

* **UI/UX Polishing**: The current PyQt6 UI provides core functionality, but a more modern and responsive user experience could be achieved. Consider migrating to web-friendly technologies like Electron (with React/Vue/Angular) or a cross-platform framework like Flutter/Qt Quick for a more polished and flexible interface.
* **Advanced Prompt Augmentation**: The current RAG prompt is effective, but exploring more sophisticated prompt engineering techniques could yield better LLM responses. This might include:
  * **Context Re-ranking**: Using a re-ranker model to select the most relevant chunks from the initial FAISS retrieval.
  * **Query Expansion**: Rewriting or expanding user queries to improve retrieval accuracy.
  * **Conversational Memory**: Implementing a more robust chat history management to provide the LLM with better conversational context beyond just the current turn.
* **Optimized Chunking Strategies**: The current chunking method (splitting by `\n\n` and filtering by length) is basic. More advanced chunking techniques could improve retrieval quality:
  * **Semantic Chunking**: Grouping text based on semantic similarity rather than arbitrary splits.
  * **Recursive Chunking**: Breaking down documents into smaller, overlapping chunks.
  * **Metadata-aware Chunking**: Incorporating document structure (headings, paragraphs) into chunking.
* **Support for More Document Types**: Extend `document_processor.py` to handle other formats like DOCX, plain text, Markdown, or even web pages.
* **Model Flexibility**: Allow users to easily switch between different embedding models or local LLMs (e.g., different Ollama models or other local inference servers) via the UI or configuration.
* **Performance Optimization**: For very large document sets, consider optimizing FAISS index loading/saving, or exploring persistent vector databases like ChromaDB or Weaviate.
* **Testing**: Implement a comprehensive suite of unit and integration tests for both the core logic and UI components to ensure stability and facilitate future development.
* **Deployment**: Provide options for easier packaging and distribution of the desktop application (e.g., using PyInstaller).

## Contributing

Contributions are welcome! If you'd like to contribute to DocuMind, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and ensure the code adheres to the project's style.
4. Write appropriate tests (if applicable).
5. Submit a pull request with a clear description of your changes.

## Development Notes

* **UI Components**: The `src/documind/ui/` directory houses the PyQt6-based graphical user interface. Key components include `main_window.py` (the primary application window), `chat_model.py` (managing chat message data), `chat_delegate.py` (customizing how chat messages are displayed), and `theme_manager.py` (handling dynamic theme switching using QSS files from `src/documind/assets/`).
* **Data Persistence**: Processed document data (FAISS index and document metadata) is stored persistently in the `documind_data/` directory. This allows the application to retain its knowledge base across sessions without re-processing documents every time.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Project Structure

The core components of the DocuMind project are organized as follows:

* `src/documind/main.py`: The main entry point of the application, responsible for initializing the PyQt6 application, splash screen, and main window.
* `src/documind/core/`: Contains the core logic of the application, including:
  * `ai_core.py`: Handles interactions with AI models for document understanding, embedding generation, vector search (FAISS), and local LLM (Ollama) integration.
  * `document_processor.py`: Manages the extraction, chunking, and initial processing of PDF documents.
* `src/documind/ui/`: Contains all the user interface components built with PyQt6, such as:
  * `main_window.py`: Defines the main application window and integrates core functionalities.
  * `chat_delegate.py`: Handles custom rendering and display logic for chat messages.
  * `chat_model.py`: Manages the data model for the chat interface, including message history.
  * `custom_widgets.py`: Contains reusable custom PyQt6 widgets used throughout the UI.
  * `splash_screen.py`: Implements the initial splash screen displayed during application startup and AI model initialization.
  * `theme_manager.py`: Manages the application's visual themes (light/dark mode) and applies QSS styles.
* `src/documind/assets/`: Stores static assets like application icons, SVG icons for UI elements, and QSS (Qt Style Sheets) for theming.
* `requirements.txt`: Lists all Python dependencies required for the project, including AI/NLP libraries, GUI framework, and HTTP clients.
* `pyproject.toml`: Project metadata, build configuration, and package discovery settings.
