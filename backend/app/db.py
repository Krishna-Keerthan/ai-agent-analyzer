import os
from typing import AsyncGenerator
import asyncpg

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://app_admin:admin_password@127.0.0.1:6432/agent_analytics"
)

pool: asyncpg.Pool | None = None

async def init_db_pool() -> None:
    global pool
    pool = await asyncpg.create_pool(
        dsn=DATABASE_URL,
        min_size=5,
        max_size=30,
        max_queries=50000,
        statement_cache_size=0,
        max_inactive_connection_lifetime=30.0,
    )


async def close_db_pool() -> None:
    global pool
    if pool:
        await pool.close()


async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    if pool is None:
        raise RuntimeError("Databse connection pool is not initialized.")

    async with pool.acquire(timeout=10.0) as connection:
        yield connection