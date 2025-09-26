from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class UsageEvent(BaseModel):
    """Track usage for billing"""
    workspace_id: str
    user_email: str
    event_type: str  # "research_query", "paper_analyzed", "ai_summary"
    tokens_used: int
    processing_time: float
    quality_score: Optional[float]
    timestamp: datetime
    metadata: Dict[str, Any]

class WorkspaceUsage(BaseModel):
    """Workspace usage summary"""
    workspace_id: str
    current_period_queries: int
    current_period_papers: int
    current_period_tokens: int
    plan_type: str  # "free", "pro", "enterprise"
    usage_limit: int
    billing_cycle_start: datetime
