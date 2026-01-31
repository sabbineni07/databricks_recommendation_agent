"""Shared data models."""
from .job_metrics import JobMetrics
from .recommendations import Recommendation, RecommendationStatus, RiskLevel

__all__ = [
    "JobMetrics",
    "Recommendation",
    "RecommendationStatus",
    "RiskLevel"
]

