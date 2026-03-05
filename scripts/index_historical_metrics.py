#!/usr/bin/env python3
"""Script to index historical job metrics for RAG."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from DE.src.collectors.local_data_collector import LocalDataCollector
from AI.src.services.azure_search_service import AzureSearchService
from shared.utils.logging import get_logger
from shared.config.settings import settings

logger = get_logger(__name__)


def index_historical_metrics(csv_path: str = None, limit: int = None):
    """Index historical job metrics from CSV.
    
    Args:
        csv_path: Path to CSV file. Defaults to settings.local_data_path
        limit: Maximum number of records to index (for testing). None for all.
    """
    try:
        # Initialize services
        collector = LocalDataCollector(csv_path=csv_path)
        search_service = AzureSearchService()
        
        logger.info("starting_historical_indexing", csv_path=csv_path or settings.local_data_path)
        
        # Collect all metrics
        # Use a wide date range to get all data
        metrics = collector.collect_job_cluster_metrics(
            start_date="2020-01-01",
            end_date="2030-12-31",
            job_ids=None
        )
        
        if limit:
            metrics = metrics[:limit]
        
        logger.info("collected_metrics", count=len(metrics))
        
        # Index each metric
        indexed = 0
        failed = 0
        
        for metric in metrics:
            try:
                success = search_service.index_job_cluster_metrics(metric)
                if success:
                    indexed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error("indexing_failed", job_id=metric.job_id, error=str(e))
                failed += 1
        
        logger.info("indexing_complete", indexed=indexed, failed=failed, total=len(metrics))
        print(f"✅ Indexed {indexed} job metrics")
        if failed > 0:
            print(f"⚠️  Failed to index {failed} metrics")
        
    except Exception as e:
        logger.error("historical_indexing_error", error=str(e))
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Index historical job metrics for RAG")
    parser.add_argument(
        "--csv-path",
        type=str,
        default=None,
        help="Path to CSV file (defaults to settings.local_data_path)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of records to index (for testing)"
    )
    
    args = parser.parse_args()
    
    index_historical_metrics(csv_path=args.csv_path, limit=args.limit)


if __name__ == "__main__":
    main()

