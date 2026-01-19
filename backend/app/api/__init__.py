# from .rag_routes import router as rag_router  # Temporarily disabled due to FlagEmbedding dependency
from .v1.contracts import router as contracts_router

# __all__ = ["rag_router", "contracts_router"]
__all__ = ["contracts_router"]
