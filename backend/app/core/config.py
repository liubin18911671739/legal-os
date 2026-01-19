from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings.
    Loaded from environment variables and .env file.
    """
    
    # Database
    DATABASE_URL: str = "postgresql://legal_user:password@localhost:5432/legal_os"
    
    # ZhipuAI
    ZHIPU_API_KEY: str = ""
    
    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION_NAME: str = "legal_documents"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Application
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "LegalOS"
    
    # Embeddings
    EMBEDDING_MODEL: str = "BAAI/bge-large-zh-v1.5"
    EMBEDDING_DIMENSION: int = 1024
    
    # Reranker
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"
    
    # Chunking
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 100
    
    # Tracing - LangSmith
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "legal-os"
    LANGCHAIN_ENDPOINT: str = ""
    
    # Tracing - LangFuse
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    LANGFUSE_ENABLED: bool = False
    
    # Tracing settings
    TRACE_ENABLED: bool = False
    TRACE_SAMPLE_RATE: float = 1.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
