from fastapi import FastAPI
from app.api.v1.endpoints import kms_proxy
from app.middleware.logging import LoggingMiddleware

app = FastAPI()
app.add_middleware(LoggingMiddleware)

app.include_router(kms_proxy.router, prefix="/api/kms", tags=["KMS Proxy"])
