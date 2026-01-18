from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List
from datetime import datetime


T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """Generic response model."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    message: str
    detail: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    
    @property
    def skip(self) -> int:
        """Calculate offset."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, size: int):
        """Create paginated response."""
        pages = (total + size - 1) // size
        return cls(items=items, total=total, page=page, size=size, pages=pages)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: Optional[str] = None
    redis: Optional[str] = None
    qdrant: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
