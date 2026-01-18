import asyncio
from app.rag.chunker import Chunker


async def test_recursive_chunking():
    """Test recursive character chunking."""
    chunker = Chunker(strategy="recursive_character", chunk_size=512, chunk_overlap=100)
    
    text = "这是一段测试文本。我们需要对很长的文本进行切分。这段文字应该被正确地分成多个块。每个块的大小应该在512左右字符左右。相邻的块之间应该有100个字符的重叠。"
    
    chunks = chunker.chunk("test-doc-1", text, {"test": True})
    
    print(f"✓ Generated {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}: {len(chunk.text)} chars, tokens≈{chunk.tokens}")
    
    assert len(chunks) > 0
    assert all(chunk.text for chunk in chunks)


async def test_semantic_chunking():
    """Test semantic chunking."""
    chunker = Chunker(strategy="semantic", chunk_size=512, chunk_overlap=100)
    
    text = "第一条：甲方是某某公司。第二条：合同金额为100万元。第三条：履行期限为30天。"
    
    chunks = chunker.chunk("test-doc-2", text, {"test": True})
    
    print(f"✓ Generated {len(chunks)} semantic chunks")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}: {chunk.text}")
    
    assert len(chunks) > 0


async def test_fixed_size_chunking():
    """Test fixed-size chunking."""
    chunker = Chunker(strategy="fixed_size", chunk_size=300, chunk_overlap=0)
    
    text = "这个是固定大小切分的测试文本。每段固定为300字符。不应该有重叠。"
    
    chunks = chunker.chunk("test-doc-3", text, {"test": True})
    
    print(f"✓ Generated {len(chunks)} fixed-size chunks")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}: {chunk.text}")
    
    assert len(chunks) > 0
    assert all(chunk.metadata.get("length") == len(chunk.text) for chunk in chunks)


async def run_tests():
    """Run all chunking tests."""
    print("=" * 60)
    print("Document Chunking Tests")
    print("=" * 60)
        
    print("\nTest 1: Recursive Character Chunking")
    await test_recursive_chunking()
    print("✓ Test passed")
        
    print("\nTest 2: Semantic Chunking")
    await test_semantic_chunking()
    print("✓ Test passed")
        
    print("\nTest 3: Fixed-size Chunking")
    await test_fixed_size_chunking()
    print("✓ Test passed")
        
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())
