# Sample Data for Local Development

This directory contains sample CSV data for local development and testing of the Databricks Recommendation Agent.

## Files

- `sample_job_metrics.csv` - Sample job metrics data with 5 different jobs and multiple runs per job

## Sample Job IDs

The CSV file contains data for the following job IDs:
- `job-001` - ETL workload (Standard_E8s_v3, 1-16 workers)
- `job-002` - CPU Intensive workload (Standard_E4s_v3, 1-8 workers)
- `job-003` - Memory Intensive workload (Standard_E16s_v3, 2-32 workers)
- `job-004` - Balanced workload (Standard_E4s_v3, 1-8 workers)
- `job-005` - Large ETL workload (Standard_E32s_v3, 4-64 workers)

## Using Local Data

To use the local CSV data instead of connecting to Databricks:

1. **Set environment variable:**
   ```bash
   export USE_LOCAL_DATA=true
   ```

2. **Or update your `.env` file:**
   ```
   USE_LOCAL_DATA=true
   LOCAL_DATA_PATH=data/sample_job_metrics.csv  # Optional, defaults to this path
   ```

3. **Or programmatically in Python:**
   ```python
   from shared.config.settings import settings
   settings.use_local_data = True
   ```

## Testing the Agent Locally

Run the test script:
```bash
python scripts/test_local_agent.py
```

Or use the agent directly:
```python
from AI.src.agents.cluster_config_agent import ClusterConfigAgent
from shared.config.settings import settings

settings.use_local_data = True

agent = ClusterConfigAgent()
result = await agent.generate_recommendation(
    job_id="job-001",
    start_date="2024-01-15",
    end_date="2024-01-18"
)
```

## CSV Format

The CSV file must contain the following columns matching the `JobMetrics` model:
- `date` - Date in YYYY-MM-DD format
- `workspace_id` - Workspace identifier
- `job_id` - Job identifier
- `job_run_id` - Individual run identifier
- `job_duration_seconds` - Duration in seconds
- `task_count` - Number of tasks
- `parallelism_ratio` - Parallelism ratio (0-1)
- `avg_cpu_utilization_pct` - Average CPU utilization percentage
- `avg_memory_utilization_pct` - Average memory utilization percentage
- `peak_cpu_utilization_pct` - Peak CPU utilization percentage
- `peak_memory_utilization_pct` - Peak memory utilization percentage
- `avg_nodes_consumed` - Average number of nodes consumed
- `p95_nodes_consumed` - 95th percentile nodes consumed
- `p99_nodes_consumed` - 99th percentile nodes consumed
- `total_cost_usd` - Total cost in USD
- `cost_per_hour_usd` - Cost per hour in USD
- `rows_added` - Number of rows added (optional)
- `num_of_tables` - Number of tables (optional)
- `workload_type` - Workload type classification (optional)
- `current_node_type` - Current node type (e.g., Standard_E8s_v3)
- `current_min_workers` - Current minimum workers
- `current_max_workers` - Current maximum workers

