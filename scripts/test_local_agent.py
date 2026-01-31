#!/usr/bin/env python3
"""Test script for running cluster_config_agent locally with CSV data."""
import asyncio
import sys
import os
from pathlib import Path

# Set environment variable for local data mode before importing settings
os.environ["USE_LOCAL_DATA"] = "true"

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after setting environment variable
from AI.src.agents.cluster_config_agent import ClusterConfigAgent
from shared.config.settings import settings

# Ensure local data mode is enabled
settings.use_local_data = True


async def test_agent():
    """Test the cluster config agent with local data."""
    print("=" * 60)
    print("Testing Cluster Config Agent with Local CSV Data")
    print("=" * 60)
    
    # Initialize agent
    print("\n1. Initializing ClusterConfigAgent...")
    agent = ClusterConfigAgent()
    
    # Test with one of the sample job IDs from the CSV
    job_id = "job-001"
    start_date = "2024-01-15"
    end_date = "2024-01-18"
    
    print(f"\n2. Generating recommendation for job: {job_id}")
    print(f"   Date range: {start_date} to {end_date}")
    
    try:
        result = await agent.generate_recommendation(
            job_id=job_id,
            start_date=start_date,
            end_date=end_date
        )
        
        print("\n3. Recommendation Results:")
        print("-" * 60)
        print(f"Recommendation: {result.get('recommendation', {})}")
        print(f"\nExplanation:\n{result.get('explanation', 'N/A')}")
        print(f"\nPattern Analysis:\n{result.get('pattern_analysis', 'N/A')}")
        print(f"\nRisk Assessment: {result.get('risk_assessment', {})}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_agent())

