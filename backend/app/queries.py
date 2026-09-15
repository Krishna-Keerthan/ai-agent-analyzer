import asyncpg
from typing import Optional

async def get_active_tenant_by_key_hash(
        conn: asyncpg.Connection, key_hash: str
) -> Optional[dict]:
    """Fetches tenant_id associated with a valid API key hash."""
    query = """
        SELECT tenant_id
        FROM api_keys
        WHERE key_hash = $1 AND is_active = TRUE;
    """
    record = await conn.fetchrow(query, key_hash)
    return dict(record) if record else None

async def create_tenant_and_key(
        conn: asyncpg.Connection,
        tenant_name: str,
        key_hash: str,
        key_prefix: str,
        key_name: str = "Default Key"
) -> dict:
    """Executes a transaction to create a tenant and issue an initian API key."""
    async with conn.transaction:
        tenant = await conn.fetchrow(
            "INSERT INTO tenants (name) VALUES ($1) RETURNING id;",
            tenant_name
        )
        tenant_id = tenant["id"]

        await conn.execute(
            """INSERT INTO api_keys (tenant_id, key_hash, key_prefix, name)
            VALUES ($1, $2, $3, $4);
            """,
            tenant_id, key_hash, key_prefix,  key_name
        )

        return {
            "tenant_id": str(tenant_id)
        }