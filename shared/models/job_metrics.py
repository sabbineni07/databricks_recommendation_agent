"""Job metrics data model."""
from pydantic import BaseModel, Field
from typing import Optional


class JobMetrics(BaseModel):
    """Job execution metrics model."""
    
    date: str
    workspace_id: str
    job_id: str
    job_run_id: str
    
    # Execution metrics
    job_duration_seconds: float
    task_count: int
    parallelism_ratio: float
    
    # Resource metrics
    avg_cpu_utilization_pct: float
    avg_memory_utilization_pct: float
    peak_cpu_utilization_pct: float
    peak_memory_utilization_pct: float
    avg_nodes_consumed: float
    p95_nodes_consumed: float
    p99_nodes_consumed: float
    
    # Cost metrics
    total_cost_usd: float
    cost_per_hour_usd: float
    
    # Workload characteristics
    rows_added: Optional[int] = None
    num_of_tables: Optional[int] = None
    workload_type: Optional[str] = None
    
    # Current configuration
    current_node_type: str
    current_min_workers: int
    current_max_workers: int
    
    class Config:
        from_attributes = True

