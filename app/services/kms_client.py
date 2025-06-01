import httpx

KMS_BASE_URL = "http://localhost:9000"

async def generate_key():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{KMS_BASE_URL}/generate_key")
        response.raise_for_status()
        return response.json()

async def encrypt(key_id: str, plaintext: str):
    payload = {"key_id": key_id, "plaintext": plaintext}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{KMS_BASE_URL}/encrypt", json=payload)
        response.raise_for_status()
        return response.json()

async def decrypt(key_id: str, ciphertext: str, nonce: str):
    payload = {"key_id": key_id, "ciphertext": ciphertext, "nonce": nonce}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{KMS_BASE_URL}/decrypt", json=payload)
        response.raise_for_status()
        return response.json()

async def generate_keypair():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{KMS_BASE_URL}/generate_keypair")
        response.raise_for_status()
        return response.json()

async def encrypt_asymmetric(key_id: str, plaintext: str):
    payload = {"key_id": key_id, "plaintext": plaintext}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{KMS_BASE_URL}/encrypt_asymmetric", json=payload)
        response.raise_for_status()
        return response.json()

async def decrypt_asymmetric(key_id: str, ciphertext: str):
    payload = {"key_id": key_id, "ciphertext": ciphertext}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{KMS_BASE_URL}/decrypt_asymmetric", json=payload)
        response.raise_for_status()
        return response.json()
