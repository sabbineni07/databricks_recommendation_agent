"""Cost optimization chain."""
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from AI.src.services.azure_openai_service import AzureOpenAIService
from shared.utils.logging import get_logger
import json
from typing import Optional

logger = get_logger(__name__)


class CostOptimizationChain:
    """LangChain for cost optimization recommendations."""
    
    def __init__(self, use_rag: bool = True):
        """Initialize cost optimization chain.
        
        Args:
            use_rag: If True, use RAG to find similar recommendations
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
            ("system", """You are a cost optimization expert for Databricks clusters.
            Given job metrics and current configuration, recommend optimal:
            1. Node family (D, E, or F)
            2. Number of vCPUs
            3. Min and max workers
            4. Auto-termination settings
            
            Always prioritize conservative recommendations with safety margins.
            Consider budget constraints and performance requirements.
            
            CRITICAL INSTRUCTIONS:
            - Historical configurations are for reference only and may be suboptimal
            - Optimize based on utilization patterns, not copy historical configs
            - Use proven recommendations as guidance, but analyze current needs
            - Consider cost optimization opportunities
            
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
            
            Job cluster metrics:
            {job_cluster_metrics}
            
            Budget Constraints:
            {budget_constraints}
            
            Pattern Analysis:
            {pattern_analysis}
            
            {historical_context}
            
            Use the pattern analysis insights to inform your recommendation, especially for:
            - Workload type classification (helps select node family D/E/F)
            - Resource utilization patterns (helps determine worker configuration)
            - Performance characteristics (helps set min/max workers and auto-termination)
            
            IMPORTANT: Historical data is for pattern matching only. Optimize based on
            actual utilization needs, not by copying historical configurations.
            
            Provide cost optimization recommendation.""")
        ])
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            verbose=True
        )
    
    def optimize(self, current_config: dict, job_cluster_metrics: dict, budget_constraints: dict, pattern_analysis: str = "") -> dict:
        """Generate cost optimization recommendation.
        
        Args:
            current_config: Current cluster configuration
            job_cluster_metrics: Aggregated job cluster metrics
            budget_constraints: Budget constraints
            pattern_analysis: Pattern analysis from PatternAnalysisChain (optional)
        """
        try:
            historical_context = ""
            
            # Use RAG to find similar recommendations if enabled
            if self.use_rag and self.search_service:
                try:
                    # First, try to find similar successful recommendations
                    # Only use validated optimal recommendations by default
                    similar_recommendations = self.search_service.search_similar(
                        pattern_analysis if pattern_analysis else str(job_cluster_metrics),
                        top_k=3,
                        filter_quality=True  # Only use optimal recommendations
                    )
                    
                    # Filter to only recommendations (not raw metrics)
                    recommendations = [
                        r for r in similar_recommendations 
                        if r.get("is_recommendation", False) or r.get("document_type") == "recommendation"
                    ]
                    
                    if recommendations:
                        # Build context from successful recommendations
                        rec_contexts = []
                        for rec in recommendations[:3]:  # Top 3
                            rec_data = rec.get("recommendation", {})
                            rec_contexts.append(
                                f"- Recommended: {rec_data.get('node_family', 'N/A')} family, "
                                f"{rec_data.get('vcpus', 'N/A')} vCPUs, "
                                f"{rec_data.get('min_workers', 'N/A')}-{rec_data.get('max_workers', 'N/A')} workers. "
                                f"Rationale: {rec_data.get('rationale', 'N/A')[:100]}"
                            )
                        
                        historical_context = f"""
                        
                        Similar Successful Recommendations Found ({len(recommendations)}):
                        {chr(10).join(rec_contexts)}
                        
                        Use these as guidance, but optimize based on current job's actual needs.
                        """
                    else:
                        # Fallback: find similar job patterns for context
                        similar_jobs = self.search_service.search_similar_jobs(
                            job_cluster_metrics,
                            top_k=3,
                            filter_recommendations=False
                        )
                        
                        if similar_jobs:
                            # Extract patterns only (not configs)
                            patterns = []
                            for job in similar_jobs:
                                metrics = job.get("metrics", {})
                                patterns.append({
                                    "cpu": metrics.get("avg_cpu_utilization_pct", 0),
                                    "memory": metrics.get("avg_memory_utilization_pct", 0),
                                    "nodes": metrics.get("avg_nodes_consumed", 0)
                                })
                            
                            if patterns:
                                avg_cpu = sum(p["cpu"] for p in patterns) / len(patterns)
                                avg_memory = sum(p["memory"] for p in patterns) / len(patterns)
                                avg_nodes = sum(p["nodes"] for p in patterns) / len(patterns)
                                
                                historical_context = f"""
                                
                                Similar Workload Patterns Found ({len(patterns)} jobs):
                                - Average CPU: {avg_cpu:.1f}%
                                - Average Memory: {avg_memory:.1f}%
                                - Average Nodes: {avg_nodes:.1f}
                                
                                NOTE: These are utilization patterns for context only.
                                Historical configurations may be suboptimal. Optimize based on
                                utilization needs, not by copying historical configs.
                                """
                except Exception as e:
                    logger.warning("rag_search_failed", error=str(e))
                    # Continue without RAG context
            
            result = self.chain.run(
                current_config=str(current_config),
                job_cluster_metrics=str(job_cluster_metrics),
                budget_constraints=str(budget_constraints),
                pattern_analysis=pattern_analysis if pattern_analysis else "No pattern analysis available.",
                historical_context=historical_context
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

