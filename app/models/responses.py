from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class KeyResponse(BaseModel):
    key_id: str = Field(..., description="Generated key ID")
    algorithm: str = Field(..., description="Cryptographic algorithm used")
    key_size: int = Field(..., description="Key size in bits")
    created_at: datetime = Field(..., description="Key creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Key expiration timestamp")


class KeyPairResponse(BaseModel):
    key_id: str = Field(..., description="Generated key pair ID")
    public_key_pem: str = Field(..., description="Public key in PEM format")
    created_at: datetime = Field(..., description="Key pair creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Key pair expiration timestamp")


class EncryptResponse(BaseModel):
    key_id: str = Field(..., description="Key ID used for encryption")
    ciphertext: str = Field(..., description="Base64 encoded ciphertext")
    nonce: str = Field(..., description="Base64 encoded nonce")
    algorithm: str = Field(..., description="Algorithm used for encryption")
    timestamp: datetime = Field(..., description="Encryption timestamp")


class DecryptResponse(BaseModel):
    plaintext: str = Field(..., description="Decrypted plaintext")
    algorithm: str = Field(..., description="Algorithm used for decryption")
    timestamp: datetime = Field(..., description="Decryption timestamp")


class AsymmetricEncryptResponse(BaseModel):
    ciphertext: str = Field(..., description="Base64 encoded ciphertext")
    algorithm: str = Field(..., description="Algorithm used for encryption")
    timestamp: datetime = Field(..., description="Encryption timestamp")


class AsymmetricDecryptResponse(BaseModel):
    plaintext: str = Field(..., description="Decrypted plaintext")
    algorithm: str = Field(..., description="Algorithm used for decryption")
    timestamp: datetime = Field(..., description="Decryption timestamp")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Service version")
    uptime: int = Field(..., description="Service uptime in seconds")
    backend_status: str = Field(..., description="Backend KMS service status")
    backend_latency: Optional[float] = Field(None, description="Backend response time in milliseconds")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    timestamp: datetime = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    status_code: int = Field(..., description="HTTP status code") 