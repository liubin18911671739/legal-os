import logging
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, close_db, check_db_connection
from app.schemas import HealthResponse
from app.core.config import settings
from app.middleware import LoggingMiddleware, ErrorHandlerMiddleware
from app.api.v1 import api_router

# RAG components
from app.rag.embeddings import BGEEmbeddingModel, RedisEmbeddingCache
from app.rag.services import QdrantVectorStore, CollectionManager
from app.rag.retrieval import RetrievalPipeline, RetrievalConfig
from app.rag.retrieval import ChineseTokenizer, BM25Indexer, HybridRetriever, BGEReranker
from app.rag.llm import ZhipuLLM, ContextBuilder, RAGPipeline, RAGResponse

# Monitoring (simplified)
# Note: Full monitoring system requires additional dependencies
logger = logging.getLogger(__name__)

# Global RAG components
rag_pipeline: Optional[RAGPipeline] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global rag_pipeline
    
    # Startup
    print("Starting LegalOS API...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # Initialize database
    db_healthy = await check_db_connection()
    if db_healthy:
        print("✓ Database connection successful")
        await init_db()
        print("✓ Database initialized")
    else:
        print("✗ Database connection failed")
    
    # Initialize RAG components
    try:
        print("Initializing RAG components...")
        
        # 1. Initialize BGE embedding model
        print("  Loading BGE embedding model...")
        bge_model = BGEEmbeddingModel(
            model_name="BAAI/bge-large-zh-v1.5",
            device="cpu",
        )
        print(f"  ✓ BGE model loaded (dimension: {bge_model.dimension})")
        
        # 2. Initialize Redis cache
        print("  Initializing Redis cache...")
        embedding_cache = RedisEmbeddingCache(
            redis_url=settings.REDIS_URL,
            embedding_model=bge_model,
            ttl=86400,  # 24 hours
        )
        print("  ✓ Redis cache initialized")
        
        # 3. Initialize Qdrant vector store
        print("  Initializing Qdrant vector store...")
        collection_manager = CollectionManager(
            url=settings.QDRANT_URL,
        )
        
        # Ensure collection exists
        collection_exists = await collection_manager.ensure_collection(
            collection_name="knowledge_base",
            vector_size=1024,
            distance="cosine",
        )
        if collection_exists:
            print("  ✓ Qdrant collection ready")
        
        vector_store = QdrantVectorStore(url=settings.QDRANT_URL)
        
        # 4. Initialize retrieval pipeline
        print("  Initializing retrieval pipeline...")
        retrieval_pipeline = RetrievalPipeline(
            embedding_model=embedding_cache,
            vector_store=vector_store,
            collection_name="knowledge_base",
            use_cache=True,
        )
        print("  ✓ Retrieval pipeline initialized")
        
        # 5. Initialize BM25 indexer
        print("  Initializing BM25 indexer...")
        tokenizer = ChineseTokenizer(remove_stopwords=True)
        bm25_indexer = BM25Indexer(
            redis_url=settings.REDIS_URL,
            tokenizer=tokenizer,
            k1=1.5,
            b=0.75,
        )
        print("  ✓ BM25 indexer initialized")
        
        # 6. Initialize BGE reranker
        print("  Initializing BGE reranker...")
        reranker = None
        try:
            reranker = BGEReranker(
                model_name="BAAI/bge-reranker-v2-m3",
                device="cpu",
                batch_size=32,
            )
            print("  ✓ BGE reranker loaded")
        except Exception as e:
            logger.warning(f"Failed to load BGE reranker: {e}")
            print("  ✗ BGE reranker skipped (will use RRF only)")
        
        # 7. Initialize hybrid retriever
        print("  Initializing hybrid retriever...")
        if reranker:
            hybrid_retriever = HybridRetriever(
                vector_retriever=retrieval_pipeline,
                bm25_indexer=bm25_indexer,
                reranker=reranker,
                vector_weight=0.7,
                bm25_weight=0.3,
                fusion_method="rrf",
            )
        else:
            hybrid_retriever = HybridRetriever(
                vector_retriever=retrieval_pipeline,
                bm25_indexer=bm25_indexer,
                reranker=None,
                vector_weight=0.7,
                bm25_weight=0.3,
                fusion_method="rrf",
            )
        print("  ✓ Hybrid retriever initialized")
        
        # 8. Initialize ZhipuAI LLM
        print("  Initializing ZhipuAI LLM...")
        zhipu_llm = ZhipuLLM(
            api_key=settings.ZHIPU_API_KEY,
            model="glm-4",
        )
        print("  ✓ ZhipuAI LLM initialized")
        
        # 9. Initialize RAG pipeline
        print("  Initializing RAG pipeline...")
        context_builder = ContextBuilder(
            max_context_length=4000,
            include_metadata=False,
            include_sources=True,
            merge_adjacent=True,
            merge_distance=2,
        )
        
        rag_pipeline = RAGPipeline(
            llm=zhipu_llm,
            retrieval_pipeline=hybrid_retriever,
            context_builder=context_builder,
            system_prompt=None,  # Use default
        )
        print("  ✓ RAG pipeline initialized")
        
        # 10. Register to RAG service
        from app.api.rag_routes import RAGService
        RAGService.get_instance().set_pipeline(rag_pipeline)
        print("  ✓ RAG pipeline registered")
        
        print("✓ All RAG components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG components: {e}", exc_info=True)
        print(f"✗ RAG initialization failed: {e}")
        rag_pipeline = None
    
    yield
    
    # Shutdown
    print("Shutting down LegalOS API...")
    await close_db()
    print("✓ Database connections closed")
    
    # Close RAG resources
    if rag_pipeline:
        try:
            await embedding_cache.close()
            print("✓ Redis cache closed")
        except Exception as e:
            logger.error(f"Failed to close Redis cache: {e}")
            print("✗ Redis cache close failed")


app = FastAPI(
    title="LegalOS API",
    description="Enterprise Legal Intelligence Analysis System",
    version="0.1.0",
    lifespan=lifespan,
)

# Add middleware (order matters)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)
