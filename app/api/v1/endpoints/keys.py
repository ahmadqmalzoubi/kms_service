from fastapi import APIRouter
from app.models.key import KeyCreateRequest, KeyResponse
from app.services.crypto_mock import create_key

router = APIRouter()
mock_key_db = {}

@router.post("/", response_model=KeyResponse)
def create_key_route(request: KeyCreateRequest):
    key_id, key_info = create_key(request.algorithm, request.key_size)
    mock_key_db[key_id] = key_info
    return key_info
