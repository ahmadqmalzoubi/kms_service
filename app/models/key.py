from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class KeyCreateRequest(BaseModel):
    algorithm: str = "AES"
    key_size: int = 256

class KeyResponse(BaseModel):
    key_id: str
    algorithm: str
    key_size: int

class EncryptRequest(BaseModel):
    key_id: str
    plaintext: str

class DecryptRequest(BaseModel):
    key_id: str
    ciphertext: str

class KeyMetadata(BaseModel):
    id: str = Field(..., description="Key ID")
    algorithm: str = Field(..., description="Cryptographic algorithm")
    key_size: int = Field(..., description="Key size in bits")
    created_at: datetime = Field(..., description="Key creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Key expiration timestamp")
    usage_count: int = Field(default=0, description="Number of times key has been used")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    is_active: bool = Field(default=True, description="Whether the key is active")
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if the key has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
