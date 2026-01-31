"""Recommendation data models."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RecommendationStatus(str, Enum):
    """Recommendation status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    MODIFIED = "modified"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recommendation(BaseModel):
    """Cluster configuration recommendation model."""
    
    recommendation_id: str
    date: str
    workspace_id: str
    job_id: str
    
    # Current configuration
    current_node_type: str
    current_min_workers: int
    current_max_workers: int
    
    # Recommended configuration
    recommended_node_family: str
    recommended_vcpus: int
    recommended_min_workers: int
    recommended_max_workers: int
    recommended_auto_termination_minutes: Optional[int] = None
    
    # Projections
    projected_cost_savings_pct: float
    projected_cost_savings_usd: float
    projected_performance_impact: str
    
    # Analysis
    confidence_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    rationale: str
    detailed_explanation: str
    
    # Status
    status: RecommendationStatus = RecommendationStatus.PENDING
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    implemented_at: Optional[datetime] = None
    
    # Feedback
    actual_cost_savings_usd: Optional[float] = None
    actual_performance_impact: Optional[str] = None
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True

