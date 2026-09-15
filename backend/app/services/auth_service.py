"""Tenant authentication and key generation."""

from app.repositories.api_key_repo import APIKeyRepository
from app.core.security import hash_api_key

class AuthService:
    def __init__(self, api_key_repo: APIKeyRepository):
        self.__api_key_repo = api_key_repo

    async def authenticate_key(self, raw_key: str) -> str:
        key_hash = hash_api_key(raw_key)
        record = await self.__api_key_repo.get_tenant_by_key_hash(key_hash)

        if not record:
            raise ValueError("Invalid or revoke API Key")

        return str(record["tenant_id"])