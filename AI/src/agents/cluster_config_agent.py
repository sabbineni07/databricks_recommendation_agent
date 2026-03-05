"""Cluster configuration recommendation agent using LangGraph."""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, List, Any
from shared.utils.logging import get_logger
from shared.config.settings import settings
from AI.src.services.azure_openai_service import AzureOpenAIService
from AI.src.chains.pattern_analysis_chain import PatternAnalysisChain
from AI.src.chains.cost_optimization_chain import CostOptimizationChain
from AI.src.chains.explanation_chain import ExplanationChain
from AI.src.tools.databricks_tools import get_job_cluster_metrics, get_cost_analysis
from AI.src.tools.cost_calculator_tools import calculate_cluster_cost, calculate_cost_savings
from AI.src.tools.validation_tools import validate_performance, assess_risks, parse_vcpus_from_node_type
from AI.src.utils.token_usage import TokenUsageTracker
from shared.services.cost_logging_service import CostLoggingService
from uuid import uuid4

logger = get_logger(__name__)


class RecommendationState(TypedDict):
    """State for recommendation generation graph."""
    job_id: str
    start_date: str
    end_date: str
    job_cluster_metrics: Dict
    resource_utilization: Dict
    cost_analysis: Dict
    pattern_analysis: str
    cost_optimization: Dict
    performance_validation: Dict
    risk_assessment: Dict
    recommendation: Dict
    explanation: str
    token_tracker: Any  # TokenUsageTracker instance


class ClusterConfigAgent:
    """Cluster configuration recommendation agent."""
    
    def __init__(self):
        """Initialize the agent."""
        self.graph = self._create_recommendation_graph()
        logger.info("cluster_config_agent_initialized")
    
    def _create_recommendation_graph(self) -> StateGraph:
        """Create LangGraph for recommendation generation."""
        
        # Initialize chains
        pattern_chain = PatternAnalysisChain()
        cost_chain = CostOptimizationChain()
        explanation_chain = ExplanationChain()
        
        # Get model name from settings
        model_name = settings.azure_openai_deployment_name or "gpt-4o"
        
        # Define graph nodes
        def collect_data(state: RecommendationState) -> RecommendationState:
            """Collect job data."""
            logger.info("collecting_job_data", job_id=state["job_id"])
            
            # Collect metrics
            state["job_cluster_metrics"] = get_job_cluster_metrics.invoke({
                "job_id": state["job_id"],
                "start_date": state["start_date"],
                "end_date": state["end_date"]
            })
            # Derive resource_utilization from job_cluster_metrics (same data, avoid extra collector call)
            jcm = state["job_cluster_metrics"]
            state["resource_utilization"] = {
                "peak_cpu_utilization_pct": jcm.get("peak_cpu_utilization_pct", jcm.get("peak_cpu_utilization", 0)),
                "peak_memory_utilization_pct": jcm.get("peak_memory_utilization_pct", jcm.get("peak_memory_utilization", 0)),
                "avg_nodes_consumed": jcm.get("avg_nodes_consumed", jcm.get("p95_nodes_consumed", 4)),
            }

            state["cost_analysis"] = get_cost_analysis.invoke({
                "job_id": state["job_id"],
                "start_date": state["start_date"],
                "end_date": state["end_date"]
            })
            
            return state
        
        def analyze_patterns(state: RecommendationState) -> RecommendationState:
            """Analyze workload patterns."""
            logger.info("analyzing_patterns", job_id=state["job_id"])
            result = pattern_chain.analyze(state["job_cluster_metrics"])
            state["pattern_analysis"] = result
            
            # Track token usage
            if "token_tracker" in state and state["token_tracker"]:
                state["token_tracker"].estimate_chain_usage(
                    chain_name="pattern_analysis",
                    model=model_name,
                    input_text=state["job_cluster_metrics"],
                    output_text=result
                )
            
            return state
        
        def optimize_costs(state: RecommendationState) -> RecommendationState:
            """Optimize costs."""
            logger.info("optimizing_costs", job_id=state["job_id"])
            
            current_config = {
                "node_type": state["job_cluster_metrics"].get("current_node_type", "Standard_E8s_v3"),
                "min_workers": state["job_cluster_metrics"].get("current_min_workers", 1),
                "max_workers": state["job_cluster_metrics"].get("current_max_workers", 16),
            }
            
            budget_constraints = {
                "monthly_budget": 10000,  # Get from database
                "current_spend": state["cost_analysis"].get("monthly_cost", 0)
            }
            
            result = cost_chain.optimize(
                current_config,
                state["job_cluster_metrics"],
                budget_constraints,
                pattern_analysis=state["pattern_analysis"]
            )
            state["cost_optimization"] = result
            
            # Track token usage
            if "token_tracker" in state and state["token_tracker"]:
                # Build input text for cost optimization
                input_data = {
                    "current_config": current_config,
                    "job_cluster_metrics": state["job_cluster_metrics"],
                    "budget_constraints": budget_constraints,
                    "pattern_analysis": state["pattern_analysis"]
                }
                state["token_tracker"].estimate_chain_usage(
                    chain_name="cost_optimization",
                    model=model_name,
                    input_text=input_data,
                    output_text=result
                )
            
            return state
        
        def validate_performance_node(state: RecommendationState) -> RecommendationState:
            """Validate performance impact."""
            logger.info("validating_performance", job_id=state["job_id"])
            
            current_peak_cpu = state["resource_utilization"].get("peak_cpu_utilization_pct", 0)
            current_peak_memory = state["resource_utilization"].get("peak_memory_utilization_pct", 0)
            
            # Extract vCPUs from node type
            current_node_type = state["job_cluster_metrics"].get("current_node_type", "Standard_E8s_v3")
            current_vcpus = parse_vcpus_from_node_type(current_node_type)
            current_max_workers = state["job_cluster_metrics"].get("current_max_workers", 16)
            
            recommended_vcpus = state["cost_optimization"].get("vcpus", 8)
            recommended_max_workers = state["cost_optimization"].get("max_workers", 8)
            
            state["performance_validation"] = validate_performance.invoke({
                "current_peak_cpu": current_peak_cpu,
                "current_peak_memory": current_peak_memory,
                "recommended_vcpus": recommended_vcpus,
                "recommended_max_workers": recommended_max_workers,
                "current_vcpus": current_vcpus,
                "current_max_workers": current_max_workers
            })
            return state
        
        def assess_risks_node(state: RecommendationState) -> RecommendationState:
            """Assess risks."""
            logger.info("assessing_risks", job_id=state["job_id"])
            
            # Calculate configuration change magnitude
            current_capacity = state["job_cluster_metrics"].get("current_max_workers", 16) * 8  # Simplified
            recommended_capacity = state["cost_optimization"].get("max_workers", 8) * state["cost_optimization"].get("vcpus", 8)
            change_magnitude = abs((current_capacity - recommended_capacity) / current_capacity * 100) if current_capacity > 0 else 0
            
            state["risk_assessment"] = assess_risks.invoke({
                "configuration_change_magnitude": change_magnitude,
                "performance_validation": state["performance_validation"],
                "cost_savings_pct": 0  # Will be calculated next
            })
            return state
        
        def generate_recommendation(state: RecommendationState) -> RecommendationState:
            """Generate final recommendation."""
            logger.info("generating_recommendation", job_id=state["job_id"])
            
            # Calculate costs
            current_node_type = state["job_cluster_metrics"].get("current_node_type", "Standard_E8s_v3")
            current_cost = calculate_cluster_cost.invoke({
                "node_type": current_node_type,
                "min_workers": state["job_cluster_metrics"].get("current_min_workers", 1),
                "max_workers": state["job_cluster_metrics"].get("current_max_workers", 16),
                "avg_nodes": state["resource_utilization"].get("avg_nodes_consumed", 4),
                "hours_per_month": 730
            })
            
            recommended_node_type = f"Standard_{state['cost_optimization']['node_family']}{state['cost_optimization']['vcpus']}s_v3"
            recommended_cost = calculate_cluster_cost.invoke({
                "node_type": recommended_node_type,
                "min_workers": state["cost_optimization"]["min_workers"],
                "max_workers": state["cost_optimization"]["max_workers"],
                "avg_nodes": state["resource_utilization"].get("avg_nodes_consumed", 4),
                "hours_per_month": 730
            })
            
            savings = calculate_cost_savings.invoke({
                "current_cost": current_cost["monthly_cost"],
                "recommended_cost": recommended_cost["monthly_cost"]
            })
            
            state["recommendation"] = {
                **state["cost_optimization"],
                "current_cost": current_cost["monthly_cost"],
                "recommended_cost": recommended_cost["monthly_cost"],
                "savings_usd": savings["savings_usd"],
                "savings_pct": savings["savings_pct"],
                "risk_level": state["risk_assessment"]["risk_level"],
                "confidence_score": 0.85
            }
            return state
        
        def generate_explanation_node(state: RecommendationState) -> RecommendationState:
            """Generate detailed explanation."""
            logger.info("generating_explanation", job_id=state["job_id"])
            
            result = explanation_chain.explain(
                recommendation=state["recommendation"],
                job_cluster_metrics=state["job_cluster_metrics"],
                pattern_analysis=state["pattern_analysis"],
                risk_assessment=state["risk_assessment"]
            )
            state["explanation"] = result
            
            # Track token usage
            if "token_tracker" in state and state["token_tracker"]:
                # Build input text for explanation
                input_data = {
                    "recommendation": state["recommendation"],
                    "job_cluster_metrics": state["job_cluster_metrics"],
                    "pattern_analysis": state["pattern_analysis"],
                    "risk_assessment": state["risk_assessment"]
                }
                state["token_tracker"].estimate_chain_usage(
                    chain_name="explanation",
                    model=model_name,
                    input_text=input_data,
                    output_text=result
                )
            
            return state
        
        # Build graph
        workflow = StateGraph(RecommendationState)
        
        # Add nodes
        workflow.add_node("collect_data", collect_data)
        workflow.add_node("analyze_patterns", analyze_patterns)
        workflow.add_node("optimize_costs", optimize_costs)
        workflow.add_node("validate_performance", validate_performance_node)
        workflow.add_node("assess_risks", assess_risks_node)
        workflow.add_node("generate_recommendation", generate_recommendation)
        workflow.add_node("generate_explanation", generate_explanation_node)
        
        # Define edges
        workflow.set_entry_point("collect_data")
        workflow.add_edge("collect_data", "analyze_patterns")
        workflow.add_edge("analyze_patterns", "optimize_costs")
        workflow.add_edge("optimize_costs", "validate_performance")
        workflow.add_edge("validate_performance", "assess_risks")
        workflow.add_edge("assess_risks", "generate_recommendation")
        workflow.add_edge("generate_recommendation", "generate_explanation")
        workflow.add_edge("generate_explanation", END)
        
        return workflow.compile()
    
    async def generate_recommendation(
        self,
        job_id: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """Generate recommendation for a job.
        
        Args:
            job_id: Databricks job ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary with recommendation and explanation
        """
        logger.info("generating_recommendation", job_id=job_id)
        
        # Initialize token tracker and cost logging
        token_tracker = TokenUsageTracker()
        cost_logger = CostLoggingService()
        request_id = uuid4()
        
        # Initialize state
        initial_state: RecommendationState = {
            "job_id": job_id,
            "start_date": start_date,
            "end_date": end_date,
            "job_cluster_metrics": {},
            "resource_utilization": {},
            "cost_analysis": {},
            "pattern_analysis": "",
            "cost_optimization": {},
            "performance_validation": {},
            "risk_assessment": {},
            "recommendation": {},
            "explanation": "",
            "token_tracker": token_tracker
        }
        
        # Run graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Get token usage summary
        token_usage_summary = token_tracker.get_summary()
        
        # Log token usage to database and App Insights
        try:
            model_name = settings.azure_openai_deployment_name or "gpt-4o"
            for chain_name, chain_data in token_usage_summary["cost_estimate"]["breakdown_by_chain"].items():
                cost_logger.log_token_usage(
                    request_id=request_id,
                    model_name=chain_data["model"],
                    chain_name=chain_name,
                    input_tokens=chain_data["input_tokens"],
                    output_tokens=chain_data["output_tokens"],
                    total_tokens=chain_data["input_tokens"] + chain_data["output_tokens"],
                    cost_usd=chain_data["total_cost_usd"],
                    job_id=job_id
                )
        except Exception as e:
            logger.warning("cost_logging_failed", error=str(e))
        
        # Log recommendation to history
        try:
            cost_logger.log_recommendation(
                request_id=request_id,
                job_id=job_id,
                recommendation=final_state["recommendation"],
                explanation=final_state["explanation"],
                pattern_analysis=final_state["pattern_analysis"],
                risk_assessment=final_state["risk_assessment"],
                token_usage_analysis=token_usage_summary
            )
        except Exception as e:
            logger.warning("recommendation_logging_failed", error=str(e))
        
        # Index recommendation for RAG (if Azure AI Search is available)
        try:
            from AI.src.services.azure_search_service import AzureSearchService
            search_service = AzureSearchService()
            
            # Build recommendation document for indexing
            recommendation_doc = {
                "recommendation_id": str(request_id),
                "job_id": job_id,
                "workload_type": final_state["job_cluster_metrics"].get("workload_type", 
                    final_state["job_cluster_metrics"].get("current_workload_type", "Unknown")),
                "rationale": final_state["recommendation"].get("rationale", ""),
                "detailed_explanation": final_state["explanation"],
                **final_state["recommendation"]
            }
            
            search_service.index_recommendation(recommendation_doc)
            
            # Link recommendation to job metrics (if job metrics were indexed)
            search_service.link_recommendation_to_job(str(request_id), job_id)
            
            logger.info("recommendation_indexed", request_id=str(request_id))
        except Exception as e:
            logger.warning("recommendation_indexing_failed", error=str(e))
            # Continue without indexing - not critical for recommendation generation
        
        return {
            "request_id": str(request_id),
            "recommendation": final_state["recommendation"],
            "explanation": final_state["explanation"],
            "pattern_analysis": final_state["pattern_analysis"],
            "risk_assessment": final_state["risk_assessment"],
            "token_usage_analysis": token_usage_summary
        }

