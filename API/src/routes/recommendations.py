"""Recommendation endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from AI.src.agents.cluster_config_agent import ClusterConfigAgent
from shared.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class GenerateRecommendationRequest(BaseModel):
    """Request model for generating recommendations."""
    job_id: str
    start_date: str
    end_date: str


class RecommendationResponse(BaseModel):
    """Response model for recommendations."""
    recommendation: Dict
    explanation: str
    pattern_analysis: str
    risk_assessment: Dict


@router.post("/generate", response_model=RecommendationResponse)
async def generate_recommendation(request: GenerateRecommendationRequest):
    """Generate a recommendation for a job.
    
    Args:
        request: Request containing job_id and date range
        
    Returns:
        Recommendation with explanation and analysis
    """
    try:
        logger.info("generating_recommendation", job_id=request.job_id)
        
        agent = ClusterConfigAgent()
        result = await agent.generate_recommendation(
            job_id=request.job_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return RecommendationResponse(
            recommendation=result["recommendation"],
            explanation=result["explanation"],
            pattern_analysis=result["pattern_analysis"],
            risk_assessment=result["risk_assessment"]
        )
    except Exception as e:
        logger.error("recommendation_generation_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

