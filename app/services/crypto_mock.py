import uuid
from app.models.key import KeyResponse

def create_key(algorithm: str, key_size: int):
    key_id = str(uuid.uuid4())
    return key_id, KeyResponse(
        key_id=key_id,
        algorithm=algorithm,
        key_size=key_size
    )
