from fastapi import APIRouter, HTTPException, Depends, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import structlog
from datetime import datetime

from app.models.requests import (
    EncryptRequest, DecryptRequest, AsymmetricEncryptRequest, AsymmetricDecryptRequest
)
from app.models.responses import (
    KeyResponse, KeyPairResponse, EncryptResponse, DecryptResponse,
    AsymmetricEncryptResponse, AsymmetricDecryptResponse
)
from app.services.kms_client import KMSClient, KMSClientError, KMSBackendError, KMSConnectionError
from app.middleware.auth import verify_api_key
from app.core.config import settings

# Setup rate limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

# Setup logging
logger = structlog.get_logger(__name__)


@router.post("/generate_key", response_model=KeyResponse, tags=["Symmetric Operations"])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def generate_key(request: Request):
    """
    Generate a new symmetric encryption key.
    
    Returns a new AES-256-GCM key with metadata including creation time and expiration.
    """
    try:
        async with KMSClient() as client:
            result = await client.generate_key()
            logger.info(
                "Key generated successfully",
                request_id=getattr(request.state, 'request_id', 'unknown'),
                key_id=result.key_id,
                algorithm=result.algorithm,
                key_size=result.key_size
            )
            return result
    except KMSBackendError as e:
        logger.error(
            "Backend error during key generation",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            error=str(e),
            status_code=e.status_code
        )
        raise
    except KMSConnectionError as e:
        logger.error(
            "Connection error during key generation",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            error=str(e)
        )
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during key generation",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/encrypt", response_model=EncryptResponse, tags=["Symmetric Operations"])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def encrypt(request: Request, data: EncryptRequest):
    """
    Encrypt data using a symmetric key.
    
    Encrypts the provided plaintext using the specified key with AES-256-GCM.
    Returns the ciphertext, nonce, and metadata.
    """
    try:
        async with KMSClient() as client:
            result = await client.encrypt(data.key_id, data.plaintext)
            logger.info(
                "Data encrypted successfully",
                request_id=getattr(request.state, 'request_id', 'unknown'),
                key_id=data.key_id,
                algorithm=result.algorithm,
                data_length=len(data.plaintext)
            )
            return result
    except KMSBackendError as e:
        logger.error(
            "Backend error during encryption",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            key_id=data.key_id,
            error=str(e),
            status_code=e.status_code
        )
        raise
    except KMSConnectionError as e:
        logger.error(
            "Connection error during encryption",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            key_id=data.key_id,
            error=str(e)
        )
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during encryption",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            key_id=data.key_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/decrypt", response_model=DecryptResponse, tags=["Symmetric Operations"])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def decrypt(request: Request, data: DecryptRequest):
    """
    Decrypt data using a symmetric key.
    
    Decrypts the provided ciphertext using the specified key and nonce with AES-256-GCM.
    Returns the decrypted plaintext and metadata.
    """
    try:
        async with KMSClient() as client:
            result = await client.decrypt(data.key_id, data.ciphertext, data.nonce)
            logger.info(
                "Data decrypted successfully",
                request_id=getattr(request.state, 'request_id', 'unknown'),
                key_id=data.key_id,
                algorithm=result.algorithm
            )
            return result
    except KMSBackendError as e:
        logger.error(
            "Backend error during decryption",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            key_id=data.key_id,
            error=str(e),
            status_code=e.status_code
        )
        raise
    except KMSConnectionError as e:
        logger.error(
            "Connection error during decryption",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            key_id=data.key_id,
            error=str(e)
        )
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during decryption",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            key_id=data.key_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/generate_keypair", response_model=KeyPairResponse, tags=["Asymmetric Operations"])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def generate_keypair(request: Request):
    """
    Generate a new asymmetric key pair.
    
    Returns a new RSA-2048 key pair with the public key in PEM format.
    The private key is stored securely on the backend.
    """
    try:
        async with KMSClient() as client:
            result = await client.generate_keypair()
            logger.info(
                "Key pair generated successfully",
                request_id=getattr(request.state, 'request_id', 'unknown'),
                key_id=result.key_id,
                algorithm="RSA-2048"
            )
            return result
    except KMSBackendError as e:
        logger.error(
            "Backend error during key pair generation",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            error=str(e),
            status_code=e.status_code
        )
        raise
    except KMSConnectionError as e:
        logger.error(
            "Connection error during key pair generation",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            error=str(e)
        )
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during key pair generation",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/encrypt_asymmetric", response_model=AsymmetricEncryptResponse, tags=["Asymmetric Operations"])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def encrypt_asymmetric(request: Request, data: AsymmetricEncryptRequest):
    """
    Encrypt data using a public key.
    
    Encrypts the provided plaintext using the specified public key with RSA-2048.
    Returns the ciphertext and metadata.
    """
    try:
        async with KMSClient() as client:
            result = await client.encrypt_asymmetric(data.key_id, data.plaintext)
            logger.info(
                "Data encrypted asymmetrically successfully",
                request_id=getattr(request.state, 'request_id', 'unknown'),
                key_id=data.key_id,
                algorithm=result.algorithm,
                data_length=len(data.plaintext)
            )
            return result
    except KMSBackendError as e:
        logger.error(
            "Backend error during asymmetric encryption",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            key_id=data.key_id,
            error=str(e),
            status_code=e.status_code
        )
        raise
    except KMSConnectionError as e:
        logger.error(
            "Connection error during asymmetric encryption",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            key_id=data.key_id,
            error=str(e)
        )
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during asymmetric encryption",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            key_id=data.key_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/decrypt_asymmetric", response_model=AsymmetricDecryptResponse, tags=["Asymmetric Operations"])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def decrypt_asymmetric(request: Request, data: AsymmetricDecryptRequest):
    """
    Decrypt data using a private key.
    
    Decrypts the provided ciphertext using the specified private key with RSA-2048.
    Returns the decrypted plaintext and metadata.
    """
    try:
        async with KMSClient() as client:
            result = await client.decrypt_asymmetric(data.key_id, data.ciphertext)
            logger.info(
                "Data decrypted asymmetrically successfully",
                request_id=getattr(request.state, 'request_id', 'unknown'),
                key_id=data.key_id,
                algorithm=result.algorithm
            )
            return result
    except KMSBackendError as e:
        logger.error(
            "Backend error during asymmetric decryption",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            key_id=data.key_id,
            error=str(e),
            status_code=e.status_code
        )
        raise
    except KMSConnectionError as e:
        logger.error(
            "Connection error during asymmetric decryption",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            key_id=data.key_id,
            error=str(e)
        )
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during asymmetric decryption",
            request_id=getattr(request.state, 'request_id', 'unknown'),
            key_id=data.key_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail="Internal server error")
