"""Metrics processing and aggregation."""
from typing import List, Dict
from shared.models.job_metrics import JobMetrics
from shared.utils.logging import get_logger
import pandas as pd

logger = get_logger(__name__)


class MetricsProcessor:
    """Process and aggregate job metrics."""
    
    def aggregate_by_job(self, metrics: List[JobMetrics]) -> Dict[str, Dict]:
        """Aggregate metrics by job_id.
        
        Args:
            metrics: List of JobMetrics objects
            
        Returns:
            Dictionary keyed by job_id with aggregated metrics
        """
        if not metrics:
            return {}
        
        df = pd.DataFrame([m.dict() for m in metrics])
        
        aggregated = {}
        for job_id in df['job_id'].unique():
            job_df = df[df['job_id'] == job_id]
            
            aggregated[job_id] = {
                'avg_duration_seconds': job_df['job_duration_seconds'].mean(),
                'avg_cost_usd': job_df['total_cost_usd'].mean(),
                'avg_cpu_utilization': job_df['avg_cpu_utilization_pct'].mean(),
                'avg_memory_utilization': job_df['avg_memory_utilization_pct'].mean(),
                'peak_cpu_utilization': job_df['peak_cpu_utilization_pct'].max(),
                'peak_memory_utilization': job_df['peak_memory_utilization_pct'].max(),
                'p95_nodes_consumed': job_df['p95_nodes_consumed'].quantile(0.95),
                'p99_nodes_consumed': job_df['p99_nodes_consumed'].quantile(0.99),
                'total_runs': len(job_df),
                'current_node_type': job_df['current_node_type'].iloc[0],
                'current_min_workers': job_df['current_min_workers'].iloc[0],
                'current_max_workers': job_df['current_max_workers'].iloc[0],
            }
        
        logger.info("aggregated_metrics", job_count=len(aggregated))
        return aggregated
    
    def identify_workload_pattern(self, metrics: JobMetrics) -> str:
        """Identify workload pattern from metrics.
        
        Args:
            metrics: JobMetrics object
            
        Returns:
            Workload type string
        """
        # Simple pattern identification logic
        if metrics.rows_added and metrics.rows_added > 10000000:
            if metrics.num_of_tables and metrics.num_of_tables <= 3:
                return "Large_ETL"
            return "Complex_ETL"
        
        if metrics.avg_cpu_utilization_pct > 70:
            return "CPU_Intensive"
        
        if metrics.avg_memory_utilization_pct > 70:
            return "Memory_Intensive"
        
        return "Balanced"

