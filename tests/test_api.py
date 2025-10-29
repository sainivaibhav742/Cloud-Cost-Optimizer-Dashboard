import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.models.database import get_db
from src.api.auth_routes import get_current_user
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
    # Mock the database session and auth
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = []

    # Override the dependencies
    app.dependency_overrides[get_db] = lambda: mock_session
    app.dependency_overrides[get_current_user] = lambda: MagicMock(username="test")

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

    # Mock auth
    app.dependency_overrides[get_current_user] = lambda: MagicMock(username="test")

    response = client.get("/recommendations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Clean up
    app.dependency_overrides = {}

@patch('src.services.auth_service.pwd_context')
def test_auth_service(mock_context):
    from src.services.auth_service import AuthService

    mock_context.hash.return_value = "$2b$12$abcdefghijklmnopqrstuvwx"
    mock_context.verify.return_value = True

    # Test password hashing
    hashed = AuthService.get_password_hash("test")
    assert hashed == "$2b$12$abcdefghijklmnopqrstuvwx"
    assert AuthService.verify_password("test", "$2b$12$abcdefghijklmnopqrstuvwx")

def test_aws_cost_service():
    from src.services.aws_cost_service import AWSCostService

    # Mock the service to avoid real AWS calls
    service = AWSCostService()
    # This would require mocking boto3, but for now just test instantiation
    assert service is not None

@patch('src.services.aws_cost_service.AWSCostService.get_yesterday_costs')
def test_costs_fetch_endpoint(mock_get_costs):
    # Mock the AWS service
    mock_get_costs.return_value = [
        {'date': '2023-01-01', 'service': 'EC2', 'cost': 10.0, 'usage': 5.0, 'account_id': '123456789'}
    ]

    # Mock the database session and auth
    mock_session = MagicMock()
    mock_session.add.return_value = None
    mock_session.commit.return_value = None

    # Override the dependencies
    app.dependency_overrides[get_db] = lambda: mock_session
    app.dependency_overrides[get_current_user] = lambda: MagicMock(username="test")

    response = client.post("/costs/fetch")
    assert response.status_code == 200
    assert "Successfully fetched" in response.json()["message"]

    # Clean up
    app.dependency_overrides = {}
