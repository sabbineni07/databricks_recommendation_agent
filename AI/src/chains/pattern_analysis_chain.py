"""Pattern analysis chain."""
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from AI.src.services.azure_openai_service import AzureOpenAIService
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class PatternAnalysisChain:
    """LangChain for analyzing workload patterns."""
    
    def __init__(self):
        """Initialize pattern analysis chain."""
        self.llm = AzureOpenAIService().get_llm()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at analyzing Databricks workload patterns.
            Analyze the provided job metrics and identify:
            1. Workload type (ETL, JSON Processing, Complex Aggregations, etc.)
            2. Resource utilization patterns
            3. Performance characteristics
            4. Optimization opportunities
            
            Be specific and data-driven in your analysis."""),
            ("human", """Job Metrics:
            {job_metrics}
            
            Please analyze this workload and provide insights.""")
        ])
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            verbose=True
        )
    
    def analyze(self, job_metrics: dict) -> str:
        """Analyze job metrics and return pattern analysis."""
        try:
            result = self.chain.run(job_metrics=str(job_metrics))
            logger.info("pattern_analysis_complete")
            return result
        except Exception as e:
            logger.error("pattern_analysis_error", error=str(e))
            raise

