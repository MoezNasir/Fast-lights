# Sales Technical Datasheet RAG System

This project is a Retrieval-Augmented Generation (RAG) application designed to assist technical sales engineers by answering questions based on commercial and architectural lighting product datasheets.

## Project Flow

The system operates in three main phases: Ingestion, Indexing, and Querying.

### 1. Data Ingestion (`ingestion/ingest.py`)
- **Input:** Raw PDF datasheets are placed in the `data/raw_pdfs/` directory.
- **Process:** The ingestion script parses these PDFs (`ingestion.pdf_parser`), extracting text and structuring it into high-quality chunks.
- **Output:** The extracted chunks are saved as a unified JSON file (`data/processed/chunks.json`).

### 2. Indexing (`indexing/`)
To enable fast and accurate retrieval, the system builds two types of indexes from the processed chunks:
- **Semantic Index (FAISS):** `indexing/faiss_index.py` generates vector embeddings for each chunk (using an embedding model) and stores them in a FAISS index (`data/faiss/`). This allows for context-aware, semantic similarity search.
- **Lexical Index (BM25):** `indexing/bm25_index.py` builds a sparse keyword-based index. This is crucial for exact matches on technical specifications (e.g., "IP40", "3000K").

### 3. Querying & API (`app/main.py` & `app/llm.py`)
The application is served via a FastAPI backend.
- **Endpoint (`/query`):** Receives user questions from the frontend.
- **Intent Detection:** `app.products.identify_product_metadata` detects product names or categories mentioned in the query.
- **Hybrid Retrieval:** `app.retrieval.hybrid_search` queries both the FAISS and BM25 indexes, combining the scores to retrieve the most relevant document chunks.
- **LLM Generation:** `app.llm.generate_rag_answer` passes the retrieved chunks to a Groq LLM (e.g., Qwen or GPT-oss models). The LLM is strictly prompted to answer the user's question using *only* the provided technical context, preventing hallucinations.
- **Response:** The API returns a natural language answer, the detected product, the specific specification type, and exact source citations (document name, page number, and confidence score).

### 4. Frontend (`static/index.html`)
- A web interface is served by the FastAPI application (mounted at `/static`), allowing users to interact with the RAG system seamlessly.

## How to Run

1. **Setup Environment:** Ensure all dependencies in `requirements.txt` are installed. Set up your `.env` file with necessary API keys (e.g., `GROQ_API_KEY`).
2. **Ingest & Index:** Run the ingestion pipeline to process your PDFs and build the FAISS/BM25 indexes:
   ```bash
   python -m ingestion.ingest
   ```
3. **Start the API:** Launch the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
4. **Access the UI:** Open your browser and navigate to `http://localhost:8000`.
