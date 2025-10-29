import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.models.database import get_db
from unittest.mock import MagicMock, patch

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Cloud Cost Optimizer Dashboard API"}

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_costs_daily_endpoint():
    # Mock the database session
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = []

    # Override the dependency
    app.dependency_overrides[get_db] = lambda: mock_session

    response = client.get("/costs/daily")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Clean up
    app.dependency_overrides = {}

@patch('src.services.anomaly_detection.AnomalyDetector')
def test_recommendations_endpoint(mock_detector_class):
    # Mock the AnomalyDetector class
    mock_detector = MagicMock()
    mock_detector.get_all_recommendations.return_value = []
    mock_detector_class.return_value = mock_detector

    response = client.get("/recommendations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
