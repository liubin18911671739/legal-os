from typing import List, Optional, Dict, Any
import os
from app.rag.loaders import PDFLoader, DocxLoader, TextLoader, Document, FileType


class DocumentProcessor:
    """Service for processing uploaded documents."""
    
    def __init__(self):
        self.pdf_loader = PDFLoader()
        self.docx_loader = DocxLoader()
        self.text_loader = TextLoader()
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process document using appropriate loader."""
        try:
            # Determine file type
            file_name = os.path.basename(file_path)
            file_ext = file_name.split('.')[-1].lower() if '.' in file_name else ""
        
            # Select loader based on file type
            if file_ext == "pdf":
                document = self.pdf_loader.load(file_path)
            elif file_ext == "docx":
                document = self.docx_loader.load(file_path)
            elif file_ext == "txt":
                document = self.text_loader.load(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            return {
                "success": True,
                "document": document,
                "message": f"Document '{document.title}' loaded successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "document": None,
                "message": f"Error processing document {os.path.basename(file_path)}: {str(e)}"
            }
    
    def batch_process(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Process multiple documents."""
        results = []
        for file_path in file_paths:
            result = self.process_document(file_path)
            results.append(result)
        return results
    
    def get_loader(self, file_type: FileType):
        """Get appropriate loader for file type."""
        if file_type == FileType.PDF:
            return self.pdf_loader
        elif file_type == FileType.DOCX:
            return self.docx_loader
        elif file_type == FileType.TXT:
            return self.text_loader
        else:
            raise ValueError(f"No loader for file type: {file_type}")
