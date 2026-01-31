"""Explanation generation chain."""
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from AI.src.services.azure_openai_service import AzureOpenAIService
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class ExplanationChain:
    """LangChain for generating detailed explanations."""
    
    def __init__(self):
        """Initialize explanation chain."""
        self.llm = AzureOpenAIService().get_llm()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at explaining technical recommendations.
            Generate a detailed, clear explanation that includes:
            1. Rationale: Why this recommendation was made
            2. Evidence: Supporting data and metrics
            3. Comparison: Current vs recommended configuration
            4. Impact: Expected outcomes (cost savings, performance)
            5. Risks: Potential issues and mitigations
            6. Alternatives: Other options considered
            
            Be specific, data-driven, and actionable."""),
            ("human", """Recommendation:
            {recommendation}
            
            Job Metrics:
            {job_metrics}
            
            Pattern Analysis:
            {pattern_analysis}
            
            Risk Assessment:
            {risk_assessment}
            
            Provide a detailed explanation.""")
        ])
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            verbose=True
        )
    
    def explain(
        self,
        recommendation: dict,
        job_metrics: dict,
        pattern_analysis: str,
        risk_assessment: dict
    ) -> str:
        """Generate detailed explanation."""
        try:
            result = self.chain.run(
                recommendation=str(recommendation),
                job_metrics=str(job_metrics),
                pattern_analysis=pattern_analysis,
                risk_assessment=str(risk_assessment)
            )
            logger.info("explanation_generated")
            return result
        except Exception as e:
            logger.error("explanation_error", error=str(e))
            raise

