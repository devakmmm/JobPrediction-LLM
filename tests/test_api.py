"""
Tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.main import app

client = TestClient(app)


def test_health():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True


def test_series_endpoint():
    """Test series endpoint."""
    response = client.get("/series?role=Software Engineer&location=New York, NY")
    
    # Should succeed if data exists, or 404 if not
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "role" in data
        assert "location" in data
        assert "series" in data
        assert isinstance(data["series"], list)


def test_forecast_endpoint():
    """Test forecast endpoint."""
    response = client.get("/forecast?role=Software Engineer&location=New York, NY&horizon=8")
    
    # Should succeed if model exists, or 404/400 if not
    assert response.status_code in [200, 400, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "role" in data
        assert "location" in data
        assert "history" in data
        assert "forecast" in data
        assert "model" in data
        assert len(data["forecast"]) == 8  # horizon


def test_forecast_horizon_validation():
    """Test forecast horizon validation."""
    # Too large
    response = client.get("/forecast?role=Test&location=Test&horizon=100")
    assert response.status_code == 422  # Validation error
    
    # Too small
    response = client.get("/forecast?role=Test&location=Test&horizon=0")
    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
