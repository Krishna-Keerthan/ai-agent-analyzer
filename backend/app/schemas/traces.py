from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field


class SpanSchema(BaseModel):
    """
    Represents an individual execution step within a trace 
    (e.g., LLM call, vector search, tool execution).
    """
    id: UUID = Field(default_factory=uuid4, description="Unique span identifier")
    name: str = Field(..., description="Span name (e.g., 'openai_chat_completion')")
    span_type: str = Field(..., description="Type of span: 'llm', 'tool', 'retrieval', etc.")
    start_time: datetime = Field(..., description="UTC timestamp when span started")
    end_time: datetime = Field(..., description="UTC timestamp when span completed")
    status: str = Field(default="success", description="Span status: 'success' or 'error'")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Span metadata (prompts, tokens, model name)")


class TraceIngestSchema(BaseModel):
    """
    Single trace event payload received during ingestion.
    """
    id: UUID = Field(default_factory=uuid4, description="Unique trace execution ID")
    tenant_id: Optional[UUID] = Field(default=None, description="Tenant UUID (overwritten by auth middleware)")
    agent_id: str = Field(..., min_length=1, max_length=255, description="Unique identifier of the agent")
    name: Optional[str] = Field(default="default_run", max_length=255, description="Friendly trace/session name")
    status: str = Field(default="success", description="Run status: 'success', 'error', or 'pending'")
    latency_ms: float = Field(default=0.0, ge=0.0, description="Execution duration in milliseconds")
    total_tokens: int = Field(default=0, ge=0, description="Total tokens consumed (prompt + completion)")
    cost_usd: float = Field(default=0.0, ge=0.0, description="Calculated cost in USD")
    execution_metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Arbitrary execution context (e.g., tokens breakdown, status, environment)"
    )
    spans: List[SpanSchema] = Field(default_factory=list, description="Sub-spans associated with this trace")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Ingestion timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "agent_id": "customer_support_v2",
                "name": "refund_processing_run",
                "status": "success",
                "latency_ms": 245.8,
                "total_tokens": 1520,
                "cost_usd": 0.00304,
                "execution_metadata": {
                    "status": "SUCCESS",
                    "tokens": {"prompt": 1200, "completion": 320, "total": 1520},
                    "environment": "production"
                },
                "spans": []
            }
        }
    )


class BatchTraceIngestRequest(BaseModel):
    """
    High-throughput batch ingestion wrapper supporting up to 10,000 trace events per request.
    """
    traces: List[TraceIngestSchema] = Field(
        ..., 
        min_length=1, 
        max_length=10000, 
        description="Array of trace events for binary COPY ingestion"
    )


class TraceResponseSchema(BaseModel):
    """
    API Response model for trace queries and analytics inspection.
    """
    id: UUID
    tenant_id: UUID
    agent_id: str
    name: Optional[str]
    status: str
    latency_ms: float
    total_tokens: int
    cost_usd: float
    execution_metadata: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)