"""API Key query logic"""
import asyncpg
from typing import Optional, Dict, Any

class APIKeyRepository:
    def __init__(self, connection: asyncpg.Connection):
        self.__conn = connection

    async def get_tenant_by_key_hash(self, key_hash: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT tenant_id
            FROM api_keys
            WHERE key_hash = $1 AND is_active = TRUE;
        """

        record = await self.__conn.fetchrow(query, key_hash)
        return dict(record) if record else None

    async def create_key(self, tenant_id: str, key_hash: str, key_prefix: str, name: str) -> Dict[str, Any]:
        query = """
            INSERT INTO api_keys (tenant_id, key_hash, key_prefix, name)
            VALUES ($1, $2, $3, $4)
            RETURNING id, tenant_id, key_prefix, name, created_at;
        """
        record = await self._conn.fetchrow(query, tenant_id, key_hash, key_prefix, name)
        return dict(record)