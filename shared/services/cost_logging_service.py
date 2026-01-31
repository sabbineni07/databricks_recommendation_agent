"""Cost and usage logging service."""
from typing import Dict, Optional, List
from datetime import datetime, date
from uuid import UUID, uuid4
from shared.utils.logging import get_logger
from shared.config.settings import settings

logger = get_logger(__name__)

# Import database components conditionally
try:
    from shared.database.connection import get_database_session
    from shared.database.models import CostUsageLog, DailyCostSummary, RecommendationHistory
    DATABASE_AVAILABLE = True
except Exception as e:
    logger.warning("database_import_failed", error=str(e))
    DATABASE_AVAILABLE = False


class CostLoggingService:
    """Service for logging cost and usage data."""
    
    def __init__(self):
        """Initialize cost logging service."""
        self.enable_app_insights = settings.app_env != "development"
        logger.info("cost_logging_service_initialized", app_insights=self.enable_app_insights)
    
    def log_token_usage(
        self,
        request_id: UUID,
        model_name: str,
        chain_name: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        cost_usd: float,
        job_id: Optional[str] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> bool:
        """Log token usage and cost.
        
        Args:
            request_id: Unique request identifier
            model_name: LLM model name (e.g., "gpt-4o")
            chain_name: Chain name (e.g., "pattern_analysis")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            total_tokens: Total tokens
            cost_usd: Cost in USD
            job_id: Optional job ID
            user_id: Optional user ID
            workspace_id: Optional workspace ID
        
        Returns:
            True if logged successfully, False otherwise
        """
        try:
            # Log to App Insights (real-time monitoring)
            if self.enable_app_insights:
                self._log_to_app_insights(
                    request_id=request_id,
                    model_name=model_name,
                    chain_name=chain_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    cost_usd=cost_usd,
                    job_id=job_id
                )
            
            # Log to PostgreSQL (historical storage)
            if not DATABASE_AVAILABLE:
                logger.warning("database_not_available_skipping_log")
                return True
            
            session = get_database_session()
            try:
                cost_log = CostUsageLog(
                    request_id=request_id,
                    job_id=job_id,
                    user_id=user_id,
                    workspace_id=workspace_id,
                    timestamp=datetime.utcnow(),
                    model_name=model_name,
                    chain_name=chain_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    cost_usd=cost_usd
                )
                session.add(cost_log)
                session.commit()
                logger.info("cost_usage_logged", request_id=str(request_id), cost_usd=cost_usd)
                return True
            except Exception as e:
                session.rollback()
                logger.error("database_logging_error", error=str(e))
                return False
            finally:
                session.close()
                
        except Exception as e:
            logger.error("cost_logging_error", error=str(e))
            return False
    
    def log_recommendation(
        self,
        request_id: UUID,
        job_id: str,
        recommendation: Dict,
        explanation: str,
        pattern_analysis: str,
        risk_assessment: Dict,
        token_usage_analysis: Optional[Dict] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> bool:
        """Log recommendation to history.
        
        Args:
            request_id: Unique request identifier
            job_id: Job ID
            recommendation: Recommendation dictionary
            explanation: Explanation text
            pattern_analysis: Pattern analysis text
            risk_assessment: Risk assessment dictionary
            token_usage_analysis: Token usage analysis dictionary
            user_id: Optional user ID
            workspace_id: Optional workspace ID
        
        Returns:
            True if logged successfully, False otherwise
        """
        if not DATABASE_AVAILABLE:
            logger.warning("database_not_available_skipping_log")
            return True
        
        try:
            session = get_database_session()
            try:
                rec_history = RecommendationHistory(
                    request_id=request_id,
                    job_id=job_id,
                    user_id=user_id,
                    workspace_id=workspace_id,
                    timestamp=datetime.utcnow(),
                    recommendation=recommendation,
                    explanation=explanation,
                    pattern_analysis=pattern_analysis,
                    risk_assessment=risk_assessment,
                    token_usage_analysis=token_usage_analysis
                )
                session.add(rec_history)
                session.commit()
                logger.info("recommendation_logged", request_id=str(request_id), job_id=job_id)
                return True
            except Exception as e:
                session.rollback()
                logger.error("recommendation_logging_error", error=str(e))
                return False
            finally:
                session.close()
        except Exception as e:
            logger.error("recommendation_logging_error", error=str(e))
            return False
    
    def _log_to_app_insights(
        self,
        request_id: UUID,
        model_name: str,
        chain_name: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        cost_usd: float,
        job_id: Optional[str] = None
    ):
        """Log to Azure Application Insights.
        
        Uses structured logging which is automatically sent to App Insights
        when azure-monitor-opentelemetry is configured.
        """
        logger.info(
            "token_usage",
            request_id=str(request_id),
            model_name=model_name,
            chain_name=chain_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            job_id=job_id
        )
    
    def get_daily_summary(self, date: date) -> Optional[Dict]:
        """Get daily cost summary.
        
        Args:
            date: Date to get summary for
        
        Returns:
            Dictionary with daily summary or None
        """
        if not DATABASE_AVAILABLE:
            return None
        
        try:
            session = get_database_session()
            try:
                summary = session.query(DailyCostSummary).filter(
                    DailyCostSummary.date == date
                ).first()
                
                if summary:
                    return {
                        "date": summary.date.isoformat(),
                        "total_requests": summary.total_requests,
                        "total_tokens": summary.total_tokens,
                        "total_cost_usd": float(summary.total_cost_usd),
                        "avg_cost_per_request": float(summary.avg_cost_per_request)
                    }
                return None
            finally:
                session.close()
        except Exception as e:
            logger.error("get_daily_summary_error", error=str(e))
            return None
    
    def get_cost_by_job(self, job_id: str, days: int = 30) -> List[Dict]:
        """Get cost breakdown by job ID.
        
        Args:
            job_id: Job ID to query
            days: Number of days to look back
        
        Returns:
            List of cost log dictionaries
        """
        if not DATABASE_AVAILABLE:
            return []
        
        try:
            session = get_database_session()
            try:
                from datetime import timedelta
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                logs = session.query(CostUsageLog).filter(
                    CostUsageLog.job_id == job_id,
                    CostUsageLog.timestamp >= cutoff_date
                ).order_by(CostUsageLog.timestamp.desc()).all()
                
                return [
                    {
                        "timestamp": log.timestamp.isoformat(),
                        "model_name": log.model_name,
                        "chain_name": log.chain_name,
                        "input_tokens": log.input_tokens,
                        "output_tokens": log.output_tokens,
                        "total_tokens": log.total_tokens,
                        "cost_usd": float(log.cost_usd)
                    }
                    for log in logs
                ]
            finally:
                session.close()
        except Exception as e:
            logger.error("get_cost_by_job_error", error=str(e))
            return []

