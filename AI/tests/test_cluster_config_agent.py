"""Tests for cluster config agent."""
import pytest
from AI.src.agents.cluster_config_agent import ClusterConfigAgent


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires Azure OpenAI and Databricks")
async def test_generate_recommendation():
    """Test recommendation generation."""
    agent = ClusterConfigAgent()
    result = await agent.generate_recommendation(
        job_id="test-job-123",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    assert "recommendation" in result
    assert "explanation" in result

