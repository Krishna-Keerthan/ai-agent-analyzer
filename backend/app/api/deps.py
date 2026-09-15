"""FastAPI dependency injection definitions."""
from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
import asyncpg

from app.core.database import get_db_connection
from app.services.factory import ServiceFactory

api_key_header = APIKeyHeader(name='X-API-Key', auto_error=False)


async def verify_tenant(
    raw_api_key: str = Security(api_key_header),
    conn: asyncpg.Connection = Depends(get_db_connection)
) -> str:
    if not raw_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing 'X-API-Key' header"
        )
    auth_service = ServiceFactory.get_auth_service(conn)
    try:
        tenant_id = await auth_service.authenticate_key(raw_api_key)
        return tenant_id
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err)
        )