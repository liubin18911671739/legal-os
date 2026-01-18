from typing import Optional
from app.rag.loaders.base_loader import BaseLoader, Document, FileType


class TextLoader(BaseLoader):
    """Plain text document loader."""
    
    def load(self, file_path: str) -> Document:
        """Load text document and extract content."""
        # Validate file first
        self.validate_file(file_path)
        
        # Extract metadata
        metadata = self.extract_metadata(file_path)
        
        # Read text content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except Exception as e:
            raise IOError(f"Error reading text file: {e}")
        
        # Create document object
        return Document(
            id=metadata["id"],
            title=metadata["title"],
            file_name=metadata["file_name"],
            file_type=FileType.TXT,
            content=text_content,
            file_path=file_path,
            file_size=metadata["file_size"],
            metadata=metadata,
        )
