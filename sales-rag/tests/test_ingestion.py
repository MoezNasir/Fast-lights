import unittest
from pathlib import Path
import json
from ingestion.pdf_parser import parse_pdf

RAW_PDFS_DIR = Path("data/raw_pdfs")

class TestIngestion(unittest.TestCase):
    def test_raw_pdfs_exist(self):
        pdf_files = list(RAW_PDFS_DIR.glob("*.pdf"))
        self.assertEqual(len(pdf_files), 13, f"Expected 13 PDF files, found {len(pdf_files)}")

    def test_pdf_parsing_structure(self):
        brightspace_pdf = RAW_PDFS_DIR / "BrightSpace.pdf"
        self.assertTrue(brightspace_pdf.exists())
        
        chunks = parse_pdf(brightspace_pdf)
        self.assertGreaterEqual(len(chunks), 4)
        
        chunk_types = {c["type"] for c in chunks}
        self.assertIn("overview", chunk_types)
        self.assertIn("specifications", chunk_types)
        self.assertIn("mechanical_compliance", chunk_types)

        spec_chunk = next(c for c in chunks if c["type"] == "specifications")
        self.assertIn("15°, 24°, 36°", spec_chunk["text"])
        self.assertIn("50,000 hours", spec_chunk["text"])

    def test_processed_chunks_file(self):
        chunks_file = Path("data/processed/chunks.json")
        self.assertTrue(chunks_file.exists())
        
        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        self.assertEqual(len(chunks), 65)

if __name__ == "__main__":
    unittest.main()
