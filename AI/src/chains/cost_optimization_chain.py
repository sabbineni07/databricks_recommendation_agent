"""Cost optimization chain."""
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from AI.src.services.azure_openai_service import AzureOpenAIService
from shared.utils.logging import get_logger
import json

logger = get_logger(__name__)


class CostOptimizationChain:
    """LangChain for cost optimization recommendations."""
    
    def __init__(self):
        """Initialize cost optimization chain."""
        self.llm = AzureOpenAIService().get_llm()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a cost optimization expert for Databricks clusters.
            Given job metrics and current configuration, recommend optimal:
            1. Node family (D, E, or F)
            2. Number of vCPUs
            3. Min and max workers
            4. Auto-termination settings
            
            Always prioritize conservative recommendations with safety margins.
            Consider budget constraints and performance requirements.
            
            Format your response as JSON with the following structure:
            {{
                "node_family": "D|E|F",
                "vcpus": <number>,
                "min_workers": <number>,
                "max_workers": <number>,
                "auto_termination_minutes": <number or null>,
                "rationale": "<explanation>"
            }}"""),
            ("human", """Current Configuration:
            {current_config}
            
            Job Metrics:
            {job_metrics}
            
            Budget Constraints:
            {budget_constraints}
            
            Pattern Analysis:
            {pattern_analysis}
            
            Use the pattern analysis insights to inform your recommendation, especially for:
            - Workload type classification (helps select node family D/E/F)
            - Resource utilization patterns (helps determine worker configuration)
            - Performance characteristics (helps set min/max workers and auto-termination)
            
            Provide cost optimization recommendation.""")
        ])
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            verbose=True
        )
    
    def optimize(self, current_config: dict, job_metrics: dict, budget_constraints: dict, pattern_analysis: str = "") -> dict:
        """Generate cost optimization recommendation.
        
        Args:
            current_config: Current cluster configuration
            job_metrics: Aggregated job metrics
            budget_constraints: Budget constraints
            pattern_analysis: Pattern analysis from PatternAnalysisChain (optional)
        """
        try:
            result = self.chain.run(
                current_config=str(current_config),
                job_metrics=str(job_metrics),
                budget_constraints=str(budget_constraints),
                pattern_analysis=pattern_analysis if pattern_analysis else "No pattern analysis available."
            )
            # Parse JSON response
            return json.loads(result)
        except json.JSONDecodeError:
            logger.warning("failed_to_parse_json", result=result)
            # Fallback to default
            return {
                "node_family": "E",
                "vcpus": 8,
                "min_workers": 1,
                "max_workers": 8,
                "auto_termination_minutes": None,
                "rationale": "Default conservative recommendation"
            }
        except Exception as e:
            logger.error("cost_optimization_error", error=str(e))
            raise

