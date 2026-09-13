from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Any, Dict, List, Optional

class AgentTraceItem(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    tenant_id: UUID
    agent_id: UUID
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    execution_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        examples={
            "model": "gpt-4o",
            "tokens": {"prompt": 120, "completion": 45, "total": 165},
            "status": "SUCCESS",
            "tool_calls": ["search_db", "format_json"]
        }
    )


class BatchTraceIngestRequest(BaseModel):
    traces: List[AgentTraceItem] = Field(..., min_length=1, max_length=10000)