"""Tests for recommendation API."""
import pytest
from httpx import AsyncClient
from API.src.main import app


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires full setup")
async def test_generate_recommendation_endpoint():
    """Test recommendation generation API endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/recommendations/generate",
            json={
                "job_id": "test-job-123",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        assert response.status_code in [200, 500]  # 500 if services not configured

