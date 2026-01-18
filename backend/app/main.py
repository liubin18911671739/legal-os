from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db, close_db, check_db_connection
from app.schemas import HealthResponse
from app.core.config import settings
from app.middleware import LoggingMiddleware, ErrorHandlerMiddleware
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting LegalOS API...")
    print(f"Database URL: {settings.DATABASE_URL}")
    db_healthy = await check_db_connection()
    if db_healthy:
        print("✓ Database connection successful")
        await init_db()
        print("✓ Database initialized")
    else:
        print("✗ Database connection failed")
    
    yield
    
    # Shutdown
    print("Shutting down LegalOS API...")
    await close_db()
    print("✓ Database connections closed")


app = FastAPI(
    title="LegalOS API",
    description="Enterprise Legal Intelligence Analysis System",
    version="0.1.0",
    lifespan=lifespan,
)

# Add middleware (order matters - error handler should be last)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    db_status = "healthy" if await check_db_connection() else "unhealthy"
    return HealthResponse(
        status="healthy",
        database=db_status,
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LegalOS API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
