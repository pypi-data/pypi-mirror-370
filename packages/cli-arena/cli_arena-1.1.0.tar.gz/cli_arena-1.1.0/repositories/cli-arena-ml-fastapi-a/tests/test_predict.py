import pytest
from fastapi.testclient import TestClient
from src.app.main import app
client = TestClient(app)
def test_predict_with_data_field():
    """Test prediction endpoint with 'data' field"""
    response = client.post(
        "/predict",
        json={"data": [1.0, 2.0, 3.0, 4.0, 5.0]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert isinstance(data["prediction"], int)
    assert isinstance(data["confidence"], float)
    assert 0 <= data["confidence"] <= 1
def test_predict_with_features_field():
    """Test prediction endpoint with 'features' field"""
    response = client.post(
        "/predict",
        json={"features": [0.5, 1.5, 2.5, 3.5, 4.5]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
def test_predict_invalid_features_count():
    """Test prediction with wrong number of features"""
    response = client.post(
        "/predict",
        json={"data": [1.0, 2.0, 3.0]}  # Only 3 features instead of 5
    )
    assert response.status_code == 400
def test_predict_no_data():
    """Test prediction with no data provided"""
    response = client.post(
        "/predict",
        json={}
    )
    assert response.status_code == 400
def test_predict_empty_data():
    """Test prediction with empty data"""
    response = client.post(
        "/predict",
        json={"data": []}
    )
    assert response.status_code == 400
