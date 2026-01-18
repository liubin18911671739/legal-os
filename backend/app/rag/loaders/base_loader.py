import os
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    UNKNOWN = "unknown"


class Document:
    """Document model."""
    
    id: str
    title: str
    file_name: str
    file_type: FileType
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    pages: Optional[int] = None
    metadata: Dict[str, Any]
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    @classmethod
    def from_file(cls, file_path: str) -> "Document":
        """Create document from file path."""
        file_name = os.path.basename(file_path)
        file_ext = file_name.split('.')[-1].lower() if '.' in file_name else ""
        
        # Determine file type
        if file_ext == "pdf":
            file_type = FileType.PDF
        elif file_ext == "docx":
            file_type = FileType.DOCX
        elif file_ext == "txt":
            file_type = FileType.TXT
        else:
            file_type = FileType.UNKNOWN
        
        return cls(
            id=str(uuid.uuid4()),
            title=file_name.replace(f".{file_ext}", ""),
            file_name=file_name,
            file_type=file_type,
            file_path=file_path,
            file_size=os.path.getsize(file_path) if os.path.exists(file_path) else None,
        )


class BaseLoader:
    """Base class for document loaders."""
    
    def load(self, file_path: str) -> Document:
        """Load document from file path. Subclasses must implement this."""
        raise NotImplementedError("Subclasses must implement load() method")
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from document. Subclasses can override."""
        file_name = os.path.basename(file_path)
        # Extract title from filename (remove extension)
        title = os.path.splitext(file_name)[0]
        
        metadata = {
            "title": title,
            "file_name": file_name,
            "file_size": os.path.getsize(file_path),
            "created_at": datetime.utcnow().isoformat(),
        }
        return metadata
    
    def validate_file(self, file_path: str) -> bool:
        """Validate file before loading."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError("File is empty")
        
        # 10MB limit
        max_size = 10 * 1024 * 1024
        if file_size > max_size:
            raise ValueError(f"File size exceeds limit ({max_size} bytes)")
        
        return True
