import asyncio
import os
import asyncpg
from app.core.security import generate_api_keys

async def seed():
    dsn = "postgresql://app_admin:admin_password@127.0.0.1:5432/agent_analytics"
    conn = await asyncpg.connect(dsn)
    
    # Insert Tenant
    tenant = await conn.fetchrow("INSERT INTO tenants (name) VALUES ($1) RETURNING id;", "Acme Corp")
    tenant_id = tenant['id']
    
    # Generate Key
    raw_key, key_hash, key_prefix = generate_api_keys()
    
    # Insert API Key
    await conn.execute(
        "INSERT INTO api_keys (tenant_id, key_hash, key_prefix, name) VALUES ($1, $2, $3, $4);",
        tenant_id, key_hash, key_prefix, "Test Key"
    )
    
    print("\n--- SEED SUCCESSFUL ---")
    print(f"Tenant ID : {tenant_id}")
    print(f"RAW API KEY: {raw_key}  <-- SAVE THIS FOR TESTING")
    print("------------------------\n")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(seed())