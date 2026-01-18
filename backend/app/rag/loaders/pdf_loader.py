import fitz  # PyMuPDF
import uuid
from typing import List, Optional
from app.rag.loaders.base_loader import BaseLoader, Document, FileType


class PDFLoader(BaseLoader):
    """PDF document loader using pymupdf (PyMuPDF alternative)."""
    
    def load(self, file_path: str) -> Document:
        """Load PDF document and extract text."""
        # Validate file first
        self.validate_file(file_path)
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Extract metadata
        metadata = self.extract_metadata(file_path)
        metadata["id"] = doc_id  # Add ID to metadata
        
        # Extract text content
        text_content = self._extract_text(file_path)
        metadata["pages"] = text_content.get("pages", 0)
        
        # Create document object
        return Document(
            id=doc_id,
            title=metadata["title"],
            file_name=metadata["file_name"],
            file_type=FileType.PDF,
            content=text_content.get("text"),
            file_path=file_path,
            file_size=metadata["file_size"],
            metadata=metadata,
        )
    
    def _extract_text(self, file_path: str) -> dict:
        """Extract text from PDF file."""
        text_parts = []
        total_pages = 0
        
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            for page_num, page in enumerate(doc, start=1):
                try:
                    page_text = page.get_text()
                    if page_text.strip():
                        text_parts.append(f"\\n--- Page {page_num} ---\\n")
                        text_parts.append(page_text)
                    elif page.get_images():
                        # Page has images but no text
                        text_parts.append(f"\\n--- Page {page_num} (images only) ---\\n")
                except Exception as e:
                    print(f"Error reading page {page_num}: {e}")
                    text_parts.append(f"\\n--- Page {page_num} (error) ---\\n")
            
            doc.close()
            
            full_text = "\\n".join(text_parts)
            
            return {
                "text": full_text,
                "pages": total_pages,
                "success": True,
            }
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return {
                "text": None,
                "pages": 0,
                "success": False,
                "error": str(e),
            }
