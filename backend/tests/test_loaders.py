import pytest
import os
import tempfile
from app.rag.loaders.pdf_loader import PDFLoader
from app.rag.loaders.docx_loader import DocxLoader
from app.rag.loaders.text_loader import TextLoader
from app.rag.loaders.base_loader import FileType


@pytest.mark.asyncio
async def test_pdf_loader():
    """Test PDF loader."""
    # Create a simple test PDF
    pdf_content = b'%PDF-1.4\\nTest PDF file\\n'
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
        f.write(pdf_content)
        temp_file = f.name
    
    try:
        loader = PDFLoader()
        document = loader.load(temp_file)
        
        assert document.file_type == FileType.PDF
        assert document.title == "test_pdf"
        assert document.content is not None
        assert "Test PDF file" in document.content
        assert "pages" in document.metadata
    finally:
        os.unlink(temp_file)


@pytest.mark.asyncio
async def test_text_loader():
    """Test text loader."""
    text_content = b'This is a test text file.\\nSecond line.\\nThird line.'
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
        f.write(text_content)
        temp_file = f.name
    
    try:
        loader = TextLoader()
        document = loader.load(temp_file)
        
        assert document.file_type == FileType.TXT
        assert document.title == "test_txt"
        assert document.content == "This is a test text file.\\nSecond line.\\nThird line."
    finally:
        os.unlink(temp_file)


@pytest.mark.asyncio
async def test_document_processor():
    """Test document processor service."""
    from app.rag.services.document_processor import DocumentProcessor
    
    processor = DocumentProcessor()
    
    # Test text file
    text_content = b'Test content'
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
        f.write(text_content)
        temp_file = f.name
    
    try:
        result = processor.process_document(temp_file)
        
        assert result["success"] is True
        assert "document" in result
        assert result["document"]["file_type"] == FileType.TXT
    finally:
        os.unlink(temp_file)


if __name__ == "__main__":
    import asyncio
    import sys
    
    async def test_all():
        """Run all tests."""
        print("=" * 60)
        print("Document Loaders Tests")
        print("=" * 60)
        
        print("\\nTesting Text Loader...")
        await test_text_loader()
        print("✓ Text loader test passed")
        
        print("\\nTesting Document Processor...")
        await test_document_processor()
        print("✓ Document processor test passed")
        
        print("\\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
    
    asyncio.run(test_all())
