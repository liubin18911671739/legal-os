import time
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable, Awaitable
import logging

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request and log response."""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client": request.client.host if request.client else None,
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        process_time = (time.time() - start_time) * 1000
        
        # Log response
        logger.info(
            f"Outgoing response: {response.status_code} - {process_time:.2f}ms",
            extra={
                "status_code": response.status_code,
                "process_time_ms": process_time,
                "path": request.url.path,
                "method": request.method,
            }
        )
        
        # Add headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
