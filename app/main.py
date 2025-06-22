from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import time
import uuid
from datetime import datetime

from app.core.config import settings
from app.middleware.logging import LoggingMiddleware, setup_logging
from app.middleware.auth import verify_api_key
from app.api.v1.endpoints import kms_proxy
from app.services.kms_client import KMSClient, KMSClientError, KMSBackendError, KMSConnectionError
from app.models.responses import HealthResponse, ErrorResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Setup logging
setup_logging()

# Setup rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"🚀 Starting {settings.project_name} v{settings.version}")
    print(f"📊 Debug mode: {settings.debug}")
    print(f"🌐 Server: {settings.host}:{settings.port}")
    print(f"🔗 Backend URL: {settings.kms_backend_url}")
    
    # Test backend connectivity
    try:
        async with KMSClient() as client:
            health = await client.health_check()
            if health.backend_status == "healthy":
                print("✅ Backend KMS service is healthy")
            else:
                print("⚠️  Backend KMS service is unhealthy")
    except Exception as e:
        print(f"❌ Backend KMS service is unreachable: {e}")
    
    yield
    
    # Shutdown
    print(f"🛑 Shutting down {settings.project_name}")


# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Enhanced Key Management Service API with comprehensive security and monitoring",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)


# Global exception handlers
@app.exception_handler(KMSBackendError)
async def kms_backend_exception_handler(request: Request, exc: KMSBackendError):
    """Handle KMS backend errors."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    error_response = ErrorResponse(
        error="Backend Error",
        detail=exc.message,
        timestamp=datetime.utcnow(),
        request_id=request_id,
        status_code=exc.status_code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


@app.exception_handler(KMSConnectionError)
async def kms_connection_exception_handler(request: Request, exc: KMSConnectionError):
    """Handle KMS connection errors."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    error_response = ErrorResponse(
        error="Service Unavailable",
        detail="Backend KMS service is currently unavailable",
        timestamp=datetime.utcnow(),
        request_id=request_id,
        status_code=503
    )
    
    return JSONResponse(
        status_code=503,
        content=error_response.model_dump()
    )


@app.exception_handler(KMSClientError)
async def kms_client_exception_handler(request: Request, exc: KMSClientError):
    """Handle general KMS client errors."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    error_response = ErrorResponse(
        error="Internal Error",
        detail=str(exc),
        timestamp=datetime.utcnow(),
        request_id=request_id,
        status_code=500
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    error_response = ErrorResponse(
        error="HTTP Error",
        detail=exc.detail,
        timestamp=datetime.utcnow(),
        request_id=request_id,
        status_code=exc.status_code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded exceptions."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    error_response = ErrorResponse(
        error="Rate Limit Exceeded",
        detail="Too many requests. Please try again later.",
        timestamp=datetime.utcnow(),
        request_id=request_id,
        status_code=429
    )
    
    return JSONResponse(
        status_code=429,
        content=error_response.model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    error_response = ErrorResponse(
        error="Internal Server Error",
        detail="An unexpected error occurred" if not settings.debug else str(exc),
        timestamp=datetime.utcnow(),
        request_id=request_id,
        status_code=500
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        async with KMSClient() as client:
            health = await client.health_check()
            return health
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version=settings.version,
            uptime=int(time.time()),
            backend_status="unreachable",
            backend_latency=None
        )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.project_name,
        "version": settings.version,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs" if settings.debug else None
    }


# Include API routers
app.include_router(
    kms_proxy.router, 
    prefix="/api/kms", 
    tags=["KMS Operations"],
    dependencies=[Depends(verify_api_key)]
)


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.project_name,
        version=settings.version,
        description="Enhanced Key Management Service API with comprehensive security and monitoring features",
        routes=app.routes,
    )
    
    # Add security schemes
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}
    
    openapi_schema["components"]["securitySchemes"]["APIKeyHeader"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "API key for authentication"
    }
    
    # Add security requirement
    openapi_schema["security"] = [{"APIKeyHeader": []}]
    
    # Add additional info
    openapi_schema["info"]["contact"] = {
        "name": "KMS Service Support",
        "email": "support@kms-service.com"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
