from fastapi import APIRouter

from app.api.v1 import documents, tasks, knowledge, websocket, evaluation, contracts, export

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_router.include_router(documents.router)
api_router.include_router(tasks.router)
api_router.include_router(knowledge.router)
api_router.include_router(websocket.router)
api_router.include_router(evaluation.router)
api_router.include_router(contracts.router)
api_router.include_router(export.router)

__all__ = ["api_router"]
