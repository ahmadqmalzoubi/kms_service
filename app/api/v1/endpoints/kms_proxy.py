from fastapi import APIRouter, Security
from pydantic import BaseModel
from app.services import kms_client
from app.middleware.auth import verify_api_key

router = APIRouter()

class EncryptRequest(BaseModel):
    key_id: str
    plaintext: str

class DecryptRequest(BaseModel):
    key_id: str
    ciphertext: str
    nonce: str

class AsymmetricEncryptRequest(BaseModel):
    key_id: str
    plaintext: str

class AsymmetricDecryptRequest(BaseModel):
    key_id: str
    ciphertext: str

@router.post("/generate_key")
async def generate_key(api_key: str = Security(verify_api_key)):
    return await kms_client.generate_key()

@router.post("/encrypt")
async def encrypt(data: EncryptRequest, api_key: str = Security(verify_api_key)):
    return await kms_client.encrypt(data.key_id, data.plaintext)

@router.post("/decrypt")
async def decrypt(data: DecryptRequest, api_key: str = Security(verify_api_key)):
    return await kms_client.decrypt(data.key_id, data.ciphertext, data.nonce)

@router.post("/generate_keypair")
async def generate_keypair(api_key: str = Security(verify_api_key)):
    return await kms_client.generate_keypair()

@router.post("/encrypt_asymmetric")
async def encrypt_asymmetric(data: AsymmetricEncryptRequest, api_key: str = Security(verify_api_key)):
    return await kms_client.encrypt_asymmetric(data.key_id, data.plaintext)

@router.post("/decrypt_asymmetric")
async def decrypt_asymmetric(data: AsymmetricDecryptRequest, api_key: str = Security(verify_api_key)):
    return await kms_client.decrypt_asymmetric(data.key_id, data.ciphertext)
