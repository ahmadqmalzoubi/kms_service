import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime

logger = logging.getLogger("kms_logger")
handler = logging.FileHandler("kms_audit.log")
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        log_entry = f"{request.method} {request.url.path} | BODY: {body.decode('utf-8')}"
        logger.info(log_entry)
        response = await call_next(request)
        return response
