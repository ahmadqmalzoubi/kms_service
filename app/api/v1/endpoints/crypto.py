from fastapi import APIRouter
from app.models.key import EncryptRequest, DecryptRequest
import base64

router = APIRouter()

mock_key_store = {}  # In-memory mock (same as keys.py should have)


@router.post("/encrypt")
def encrypt(request: EncryptRequest):
    plaintext_bytes = request.plaintext.encode("utf-8")
    ciphertext = base64.b64encode(plaintext_bytes).decode("utf-8")
    return {"ciphertext": ciphertext}


@router.post("/decrypt")
def decrypt(request: DecryptRequest):
    try:
        ciphertext_bytes = base64.b64decode(request.ciphertext)
        plaintext = ciphertext_bytes.decode("utf-8")
        return {"plaintext": plaintext}
    except Exception as e:
        return {"error": "Invalid ciphertext"}
