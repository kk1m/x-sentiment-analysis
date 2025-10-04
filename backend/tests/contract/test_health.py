"""
Contract Test: GET /health
Validates the health check endpoint returns expected schema
"""
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)


def test_health_endpoint_returns_200():
    """Health endpoint should return 200 OK"""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_correct_schema():
    """Health endpoint should return status and service fields"""
    response = client.get("/health")
    data = response.json()
    
    assert "status" in data
    assert "service" in data
    assert data["status"] == "healthy"
    assert data["service"] == "x-sentiment-analysis"


def test_health_endpoint_content_type():
    """Health endpoint should return JSON"""
    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"
