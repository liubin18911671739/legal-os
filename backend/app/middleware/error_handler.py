from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """Middleware for handling exceptions globally."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        """Handle exceptions."""
        try:
            return await call_next(request)
        except Exception as exc:
            return await self.handle_exception(request, exc)
    
    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle different types of exceptions."""
        logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=exc)
        
        # Handle validation errors
        if isinstance(exc, RequestValidationError):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "success": False,
                    "message": "Validation error",
                    "detail": exc.errors(),
                }
            )
        
        # Handle FastAPI HTTP exceptions
        elif isinstance(exc, HTTPException) or isinstance(exc, StarletteHTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "message": exc.detail,
                    "detail": getattr(exc, "detail", None),
                }
            )
        
        # Handle SQLAlchemy errors
        elif isinstance(exc, SQLAlchemyError):
            logger.error(f"Database error: {str(exc)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "message": "Database error occurred",
                    "detail": "An error occurred while processing your request",
                }
            )
        
        # Handle all other exceptions
        else:
            logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "message": "Internal server error",
                    "detail": "An unexpected error occurred",
                }
            )
