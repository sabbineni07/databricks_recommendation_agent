"""Pattern analysis chain."""
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from AI.src.services.azure_openai_service import AzureOpenAIService
from shared.utils.logging import get_logger
from typing import Optional

logger = get_logger(__name__)


class PatternAnalysisChain:
    """LangChain for analyzing workload patterns."""
    
    def __init__(self, use_rag: bool = True):
        """Initialize pattern analysis chain.
        
        Args:
            use_rag: If True, use RAG to find similar historical jobs
        """
        self.llm = AzureOpenAIService().get_llm()
        self.use_rag = use_rag
        self.search_service = None
        
        if self.use_rag:
            try:
                from AI.src.services.azure_search_service import AzureSearchService
                self.search_service = AzureSearchService()
            except Exception as e:
                logger.warning("azure_search_not_available", error=str(e))
                self.use_rag = False
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at analyzing Databricks workload patterns.
            Analyze the provided job metrics and identify:
            1. Workload type (ETL, JSON Processing, Complex Aggregations, etc.)
            2. Resource utilization patterns
            3. Performance characteristics
            4. Optimization opportunities
            
            Be specific and data-driven in your analysis.
            
            If historical patterns are provided, use them for context but remember:
            - Historical configurations may be suboptimal
            - Focus on utilization patterns, not copying configs
            - Analyze what the patterns tell you about workload needs"""),
            ("human", """Job cluster metrics:
            {job_cluster_metrics}
            
            {historical_context}
            
            Please analyze this workload and provide insights.""")
        ])
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            verbose=True
        )
    
    def analyze(self, job_cluster_metrics: dict) -> str:
        """Analyze job cluster metrics and return pattern analysis.
        
        Args:
            job_cluster_metrics: Dictionary with job cluster metrics
            
        Returns:
            Pattern analysis text
        """
        try:
            historical_context = ""
            
            # Use RAG to find similar jobs if enabled
            if self.use_rag and self.search_service:
                try:
                    similar_jobs = self.search_service.search_similar_jobs(
                        job_cluster_metrics, 
                        top_k=5,
                        filter_recommendations=False
                    )
                    
                    if similar_jobs:
                        # Extract utilization patterns from similar jobs
                        patterns = []
                        for job in similar_jobs:
                            metrics = job.get("metrics", {})
                            patterns.append({
                                "cpu": metrics.get("avg_cpu_utilization_pct", 0),
                                "memory": metrics.get("avg_memory_utilization_pct", 0),
                                "nodes": metrics.get("avg_nodes_consumed", 0),
                                "workload_type": job.get("workload_type", "Unknown")
                            })
                        
                        # Build historical context
                        if patterns:
                            avg_cpu = sum(p["cpu"] for p in patterns) / len(patterns)
                            avg_memory = sum(p["memory"] for p in patterns) / len(patterns)
                            avg_nodes = sum(p["nodes"] for p in patterns) / len(patterns)
                            workload_types = [p["workload_type"] for p in patterns]
                            most_common_workload = max(set(workload_types), key=workload_types.count)
                            
                            historical_context = f"""
                            
                            Similar Historical Workload Patterns Found ({len(patterns)} jobs):
                            - Most common workload type: {most_common_workload}
                            - Average CPU utilization: {avg_cpu:.1f}%
                            - Average Memory utilization: {avg_memory:.1f}%
                            - Average nodes consumed: {avg_nodes:.1f}
                            
                            IMPORTANT: These are utilization patterns from similar jobs for context.
                            Historical configurations may be suboptimal. Focus on analyzing the
                            utilization patterns to understand workload needs, not copying historical configs.
                            """
                except Exception as e:
                    logger.warning("rag_search_failed", error=str(e))
                    # Continue without RAG context
            
            result = self.chain.run(
                job_cluster_metrics=str(job_cluster_metrics),
                historical_context=historical_context
            )
            logger.info("pattern_analysis_complete", used_rag=self.use_rag)
            return result
        except Exception as e:
            logger.error("pattern_analysis_error", error=str(e))
            raise

