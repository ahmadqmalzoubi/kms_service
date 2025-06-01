from pydantic import BaseModel
from typing import Optional

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
