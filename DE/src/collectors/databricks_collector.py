"""Databricks system tables data collector."""
from databricks import sql
from typing import List, Optional, Dict
from shared.config.settings import settings
from shared.models.job_metrics import JobMetrics
from shared.utils.logging import get_logger
import pandas as pd

logger = get_logger(__name__)


class DatabricksCollector:
    """Collects data from Databricks system tables."""
    
    def __init__(self):
        self.connection_params = {
            "server_hostname": settings.databricks_server_hostname,
            "http_path": settings.databricks_http_path,
            "access_token": settings.databricks_token,
        }
    
    def collect_job_metrics(
        self, 
        start_date: str, 
        end_date: str,
        job_ids: Optional[List[str]] = None,
        workspace_id: Optional[str] = None
    ) -> List[JobMetrics]:
        """Collect job metrics from Databricks system tables.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            job_ids: Optional list of job IDs to filter
            workspace_id: Optional workspace ID to filter
            
        Returns:
            List of JobMetrics objects
        """
        logger.info(
            "collecting_job_metrics",
            start_date=start_date,
            end_date=end_date,
            job_count=len(job_ids) if job_ids else None
        )
        
        query = self._build_job_metrics_query(start_date, end_date, job_ids, workspace_id)
        
        try:
            with sql.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    columns = [desc[0] for desc in cursor.description]
                    results = cursor.fetchall()
                    
                    # Convert to JobMetrics objects
                    metrics = []
                    for row in results:
                        row_dict = dict(zip(columns, row))
                        try:
                            metric = JobMetrics(**row_dict)
                            metrics.append(metric)
                        except Exception as e:
                            logger.warning("failed_to_parse_metric", error=str(e), row=row_dict)
                    
                    logger.info("collected_job_metrics", count=len(metrics))
                    return metrics
                    
        except Exception as e:
            logger.error("databricks_collection_error", error=str(e))
            raise
    
    def _build_job_metrics_query(
        self,
        start_date: str,
        end_date: str,
        job_ids: Optional[List[str]] = None,
        workspace_id: Optional[str] = None
    ) -> str:
        """Build SQL query for job metrics."""
        job_filter = ""
        if job_ids:
            job_list = ",".join([f"'{j}'" for j in job_ids])
            job_filter = f"AND jr.job_id IN ({job_list})"
        
        workspace_filter = ""
        if workspace_id:
            workspace_filter = f"AND jr.workspace_id = '{workspace_id}'"
        
        # Simplified query - extend with full metrics from your existing queries
        query = f"""
        SELECT 
            DATE(jr.period_start_time) AS date,
            jr.workspace_id,
            jr.job_id,
            jr.job_run_id,
            TIMESTAMPDIFF(SECOND, jr.period_start_time, jr.period_end_time) AS job_duration_seconds,
            0 AS task_count,
            1.0 AS parallelism_ratio,
            0.0 AS avg_cpu_utilization_pct,
            0.0 AS avg_memory_utilization_pct,
            0.0 AS peak_cpu_utilization_pct,
            0.0 AS peak_memory_utilization_pct,
            1.0 AS avg_nodes_consumed,
            1.0 AS p95_nodes_consumed,
            1.0 AS p99_nodes_consumed,
            0.0 AS total_cost_usd,
            0.0 AS cost_per_hour_usd,
            NULL AS rows_added,
            NULL AS num_of_tables,
            NULL AS workload_type,
            'Standard_E8s_v3' AS current_node_type,
            1 AS current_min_workers,
            16 AS current_max_workers
        FROM system.lakeflow.job_run_timeline jr
        WHERE jr.period_start_time >= '{start_date}'
            AND jr.period_start_time < '{end_date}'
            AND size(jr.compute_ids) > 0
            {job_filter}
            {workspace_filter}
        LIMIT 1000
        """
        return query
    
    def collect_resource_utilization(
        self,
        start_date: str,
        end_date: str,
        job_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """Collect resource utilization metrics."""
        # Implementation using your existing resource utilization queries
        logger.info("collecting_resource_utilization", start_date=start_date, end_date=end_date)
        # Placeholder - implement with your actual query
        return []
    
    def collect_cost_data(
        self,
        start_date: str,
        end_date: str,
        job_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """Collect cost and usage data."""
        # Implementation using your existing cost queries
        logger.info("collecting_cost_data", start_date=start_date, end_date=end_date)
        # Placeholder - implement with your actual query
        return []

