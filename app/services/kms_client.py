import httpx
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import time
import logging
from app.core.config import settings
from app.models.responses import (
    KeyResponse, KeyPairResponse, EncryptResponse, DecryptResponse,
    AsymmetricEncryptResponse, AsymmetricDecryptResponse, HealthResponse
)
from app.models.requests import (
    EncryptRequest, DecryptRequest, AsymmetricEncryptRequest, AsymmetricDecryptRequest
)

logger = logging.getLogger(__name__)


class KMSClientError(Exception):
    """Base exception for KMS client errors."""
    pass


class KMSBackendError(KMSClientError):
    """Exception raised when backend returns an error."""
    def __init__(self, message: str, status_code: int, response_text: str = ""):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"{message} (Status: {status_code})")


class KMSConnectionError(KMSClientError):
    """Exception raised when connection to backend fails."""
    pass


class KMSClient:
    """Enhanced KMS client with retry logic, error handling, and connection pooling."""
    
    def __init__(self):
        self.base_url = settings.kms_backend_url.rstrip('/')
        self.timeout = settings.kms_backend_timeout
        self.max_retries = settings.kms_backend_retries
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
            headers={"User-Agent": f"KMS-Service/{settings.version}"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        if not self._client:
            raise KMSConnectionError("Client not initialized. Use async context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = await self._client.get(url)
            elif method.upper() == "POST":
                response = await self._client.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            logger.info(f"KMS backend request: {method} {endpoint} - Status: {response.status_code} - Latency: {latency:.2f}ms")
            
            if response.status_code >= 400:
                error_msg = f"Backend request failed: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', error_msg)
                except:
                    error_msg = f"{error_msg} - {response.text}"
                
                raise KMSBackendError(error_msg, response.status_code, response.text)
            
            return response.json()
            
        except httpx.TimeoutException as e:
            logger.warning(f"KMS backend timeout: {method} {endpoint}")
            if retry_count < self.max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self._make_request(method, endpoint, data, retry_count + 1)
            raise KMSConnectionError(f"Backend timeout after {self.max_retries} retries: {e}")
            
        except httpx.ConnectError as e:
            logger.error(f"KMS backend connection error: {method} {endpoint} - {e}")
            if retry_count < self.max_retries:
                await asyncio.sleep(2 ** retry_count)
                return await self._make_request(method, endpoint, data, retry_count + 1)
            raise KMSConnectionError(f"Backend connection failed after {self.max_retries} retries: {e}")
            
        except Exception as e:
            logger.error(f"KMS backend unexpected error: {method} {endpoint} - {e}")
            raise KMSClientError(f"Unexpected error: {e}")
    
    async def health_check(self) -> HealthResponse:
        """Check backend health status."""
        try:
            start_time = time.time()
            data = await self._make_request("GET", "/health")
            latency = (time.time() - start_time) * 1000
            
            return HealthResponse(
                status="healthy",
                timestamp=datetime.utcnow(),
                version=settings.version,
                uptime=int(time.time()),
                backend_status=data.get("status", "unknown"),
                backend_latency=latency
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthResponse(
                status="unhealthy",
                timestamp=datetime.utcnow(),
                version=settings.version,
                uptime=int(time.time()),
                backend_status="unreachable",
                backend_latency=None
            )
    
    async def generate_key(self) -> KeyResponse:
        """Generate a new symmetric key."""
        data = await self._make_request("POST", "/generate_key")
        return KeyResponse(**data)
    
    async def encrypt(self, key_id: str, plaintext: str) -> EncryptResponse:
        """Encrypt data with symmetric key."""
        request_data = EncryptRequest(key_id=key_id, plaintext=plaintext)
        data = await self._make_request("POST", "/encrypt", request_data.dict())
        return EncryptResponse(**data)
    
    async def decrypt(self, key_id: str, ciphertext: str, nonce: str) -> DecryptResponse:
        """Decrypt data with symmetric key."""
        request_data = DecryptRequest(key_id=key_id, ciphertext=ciphertext, nonce=nonce)
        data = await self._make_request("POST", "/decrypt", request_data.dict())
        return DecryptResponse(**data)
    
    async def generate_keypair(self) -> KeyPairResponse:
        """Generate a new asymmetric key pair."""
        data = await self._make_request("POST", "/generate_keypair")
        return KeyPairResponse(**data)
    
    async def encrypt_asymmetric(self, key_id: str, plaintext: str) -> AsymmetricEncryptResponse:
        """Encrypt data with public key."""
        request_data = AsymmetricEncryptRequest(key_id=key_id, plaintext=plaintext)
        data = await self._make_request("POST", "/encrypt_asymmetric", request_data.dict())
        return AsymmetricEncryptResponse(**data)
    
    async def decrypt_asymmetric(self, key_id: str, ciphertext: str) -> AsymmetricDecryptResponse:
        """Decrypt data with private key."""
        request_data = AsymmetricDecryptRequest(key_id=key_id, ciphertext=ciphertext)
        data = await self._make_request("POST", "/decrypt_asymmetric", request_data.dict())
        return AsymmetricDecryptResponse(**data)


# Global client instance for backward compatibility
async def get_kms_client() -> KMSClient:
    """Get KMS client instance."""
    return KMSClient()


# Legacy functions for backward compatibility
async def generate_key():
    async with KMSClient() as client:
        return await client.generate_key()

async def encrypt(key_id: str, plaintext: str):
    async with KMSClient() as client:
        return await client.encrypt(key_id, plaintext)

async def decrypt(key_id: str, ciphertext: str, nonce: str):
    async with KMSClient() as client:
        return await client.decrypt(key_id, ciphertext, nonce)

async def generate_keypair():
    async with KMSClient() as client:
        return await client.generate_keypair()

async def encrypt_asymmetric(key_id: str, plaintext: str):
    async with KMSClient() as client:
        return await client.encrypt_asymmetric(key_id, plaintext)

async def decrypt_asymmetric(key_id: str, ciphertext: str):
    async with KMSClient() as client:
        return await client.decrypt_asymmetric(key_id, ciphertext)
