from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
import asyncpg

from backend.app.core.security import hash_api_key
from backend.app.core.database import get_db_connection
from app.queries import get_active_tenant_by_key_hash

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(
        raw_api_key: str = Security(api_key_header),
        conn: asyncpg.Connection = Depends(get_db_connection)
) -> str:
    """Verfies API key against DB and returns valid tenant_id."""

    if not raw_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing 'X-API-Key' header"
        )

    key_hash = hash_api_key(raw_api_key)
    record = await get_active_tenant_by_key_hash(conn, key_hash)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API Key"
        )

    return str(record["tenant_id"])