import time
import uuid
import logging
import structlog
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.config import settings


# Configure structured logging
def setup_logging():
    """Setup structured logging configuration."""
    if settings.log_format.lower() == "json":
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    else:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced logging middleware with request tracking and performance monitoring."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = structlog.get_logger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to response headers
        start_time = time.time()
        
        # Log request
        self.logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            content_length=request.headers.get("content-length"),
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = (time.time() - start_time) * 1000
            
            # Log response
            self.logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time_ms=round(process_time, 2),
                content_length=response.headers.get("content-length"),
            )
            
            # Add request ID and timing to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 2))
            
            return response
            
        except Exception as e:
            # Calculate processing time
            process_time = (time.time() - start_time) * 1000
            
            # Log error
            self.logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(e),
                error_type=type(e).__name__,
                process_time_ms=round(process_time, 2),
                exc_info=True,
            )
            
            # Re-raise the exception
            raise


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and metrics."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = structlog.get_logger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate metrics
        process_time = (time.time() - start_time) * 1000
        
        # Log slow requests
        if process_time > 1000:  # Log requests taking more than 1 second
            self.logger.warning(
                "Slow request detected",
                request_id=getattr(request.state, 'request_id', 'unknown'),
                method=request.method,
                url=str(request.url),
                process_time_ms=round(process_time, 2),
                status_code=response.status_code,
            )
        
        return response
