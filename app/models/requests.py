from pydantic import BaseModel, Field, validator
from typing import Optional


class EncryptRequest(BaseModel):
    key_id: str = Field(..., min_length=1, max_length=100, description="Key ID for encryption")
    plaintext: str = Field(..., min_length=1, max_length=65536, description="Plaintext to encrypt")
    
    @validator('key_id')
    def validate_key_id(cls, v):
        if not v.strip():
            raise ValueError('Key ID cannot be empty')
        return v.strip()
    
    @validator('plaintext')
    def validate_plaintext(cls, v):
        if not v.strip():
            raise ValueError('Plaintext cannot be empty')
        return v.strip()


class DecryptRequest(BaseModel):
    key_id: str = Field(..., min_length=1, max_length=100, description="Key ID for decryption")
    ciphertext: str = Field(..., min_length=1, description="Ciphertext to decrypt")
    nonce: str = Field(..., min_length=1, description="Nonce used for encryption")
    
    @validator('key_id')
    def validate_key_id(cls, v):
        if not v.strip():
            raise ValueError('Key ID cannot be empty')
        return v.strip()
    
    @validator('ciphertext')
    def validate_ciphertext(cls, v):
        if not v.strip():
            raise ValueError('Ciphertext cannot be empty')
        return v.strip()
    
    @validator('nonce')
    def validate_nonce(cls, v):
        if not v.strip():
            raise ValueError('Nonce cannot be empty')
        return v.strip()


class AsymmetricEncryptRequest(BaseModel):
    key_id: str = Field(..., min_length=1, max_length=100, description="Public key ID for encryption")
    plaintext: str = Field(..., min_length=1, max_length=190, description="Plaintext to encrypt (max 190 chars for RSA-2048)")
    
    @validator('key_id')
    def validate_key_id(cls, v):
        if not v.strip():
            raise ValueError('Key ID cannot be empty')
        return v.strip()
    
    @validator('plaintext')
    def validate_plaintext(cls, v):
        if not v.strip():
            raise ValueError('Plaintext cannot be empty')
        if len(v) > 190:
            raise ValueError('Plaintext too long for RSA-2048 encryption (max 190 characters)')
        return v.strip()


class AsymmetricDecryptRequest(BaseModel):
    key_id: str = Field(..., min_length=1, max_length=100, description="Private key ID for decryption")
    ciphertext: str = Field(..., min_length=1, description="Ciphertext to decrypt")
    
    @validator('key_id')
    def validate_key_id(cls, v):
        if not v.strip():
            raise ValueError('Key ID cannot be empty')
        return v.strip()
    
    @validator('ciphertext')
    def validate_ciphertext(cls, v):
        if not v.strip():
            raise ValueError('Ciphertext cannot be empty')
        return v.strip() 