from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EvaluationResponse(BaseModel):
    """Represents the response for an evaluation from the DeepRails API."""
    eval_id: str
    evaluation_status: str
    guardrail_metrics: Optional[List[str]] = None
    model_used: Optional[str] = None
    run_mode: Optional[str] = None
    model_input: Optional[Dict[str, Any]] = None
    model_output: Optional[str] = None
    estimated_cost: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    nametag: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    start_timestamp: Optional[datetime] = None
    completion_timestamp: Optional[datetime] = None
    error_message: Optional[str] = None
    error_timestamp: Optional[datetime] = None
    evaluation_result: Optional[Dict[str, Any]] = None
    evaluation_total_cost: Optional[float] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    class Config:
        extra = 'ignore'

class MonitorResponse(BaseModel):
    """Represents a monitor from the DeepRails API."""
    monitor_id: str
    user_id: str
    name: str
    description: Optional[str] = None
    monitor_status: str
    created_at: str
    updated_at: str

    class Config:
        extra = 'ignore'

class MonitorEventCreate(BaseModel):
    """Model for creating a new monitor event."""
    model_input: Dict[str, Any]
    model_output: str
    model_used: Optional[str] = None
    run_mode: Optional[str] = None
    guardrail_metrics: List[str]
    nametag: Optional[str] = None
    webhook: Optional[str] = None

class MonitorEventResponse(BaseModel):
    """Response model for a monitor event."""
    event_id: str
    monitor_id: str
    evaluation_id: str
    created_at: str

    class Config:
        extra = 'ignore'

class PaginationInfo(BaseModel):
    """Pagination information for list responses."""
    page: int
    limit: int
    total_pages: int
    total_count: int
    has_next: bool
    has_previous: bool

class MonitorFiltersApplied(BaseModel):
    """Information about which filters were applied to the monitor query."""
    search: Optional[List[str]] = None
    status: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None

class MonitorWithEventCountResponse(MonitorResponse):
    """Monitor response with event count information."""
    event_count: int
    latest_event_modified_at: Optional[str] = None

class MonitorListResponse(BaseModel):
    """Response model for a paginated list of monitors."""
    monitors: List[MonitorWithEventCountResponse]
    pagination: PaginationInfo
    filters_applied: MonitorFiltersApplied
