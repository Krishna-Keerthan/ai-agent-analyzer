from fastapi import APIRouter, Depends, status
from app.api.deps import verify_tenant

router = APIRouter()

@router.post("/traces", status_code=status.HTTP_202_ACCEPTED)
async def ingest_trace(
    payload: dict,
    tenant_id: str = Depends(verify_tenant)
):
    return {
        "status": "accepted",
        "tenant_id": tenant_id
    }