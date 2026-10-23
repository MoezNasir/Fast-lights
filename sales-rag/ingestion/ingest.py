import json
import os
from pathlib import Path
from ingestion.pdf_parser import parse_pdf
from indexing.faiss_index import build_and_save_faiss
from indexing.bm25_index import build_and_save_bm25

RAW_PDFS_DIR = Path("data/raw_pdfs")
PROCESSED_DIR = Path("data/processed")

def ingest_all_pdfs():
    """Parses all raw PDFs, saves unified chunks, and builds FAISS & BM25 indexes."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(list(RAW_PDFS_DIR.glob("*.pdf")))
    
    if not pdf_files:
        print("No PDF files found in data/raw_pdfs.")
        return []

    all_chunks = []
    print(f"Starting ingestion of {len(pdf_files)} PDF datasheets...")

    for pdf_path in pdf_files:
        print(f"Parsing: {pdf_path.name}")
        chunks = parse_pdf(pdf_path)
        all_chunks.extend(chunks)
        print(f" -> Generated {len(chunks)} high-quality structured chunks.")

    # Save to chunks.json
    chunks_file = PROCESSED_DIR / "chunks.json"
    with open(chunks_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\nTotal structured chunks across all products: {len(all_chunks)}")
    print(f"Saved chunks to {chunks_file}")

    # Build FAISS and BM25 indexes
    print("\nBuilding FAISS Vector Index...")
    build_and_save_faiss(all_chunks)

    print("\nBuilding BM25 Lexical Index...")
    build_and_save_bm25(all_chunks)

    print("\nIngestion and Indexing complete!")
    return all_chunks

if __name__ == "__main__":
    ingest_all_pdfs()