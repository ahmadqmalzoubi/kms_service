from fastapi.security.api_key import APIKeyHeader
from fastapi import Request, HTTPException, Security
from starlette.status import HTTP_401_UNAUTHORIZED
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
