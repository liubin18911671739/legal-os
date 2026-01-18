from fastapi import APIRouter

from app.api.v1 import documents, tasks

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_router.include_router(documents.router)
api_router.include_router(tasks.router)

__all__ = ["api_router"]
