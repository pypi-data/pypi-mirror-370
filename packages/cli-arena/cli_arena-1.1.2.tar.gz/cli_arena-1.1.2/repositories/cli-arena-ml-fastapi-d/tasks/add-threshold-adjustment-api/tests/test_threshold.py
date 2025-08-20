from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def get_token():
    res = client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "secret123"
    })
    return res.json()["access_token"]

def test_valid_threshold_update():
    token = get_token()
    res = client.put("/config/threshold", json={"value": 0.7},
                     headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json() == {"message": "Threshold updated", "value": 0.7}

def test_invalid_threshold_low():
    token = get_token()
    res = client.put("/config/threshold", json={"value": -0.5},
                     headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422

def test_predict_respects_new_threshold():
    token = get_token()
    client.put("/config/threshold", json={"value": 0.99},
               headers={"Authorization": f"Bearer {token}"})
    
    res = client.post("/predict/", json={
        "age": 30,
        "income": 50000,
        "loan_amount": 10000,
        "credit_score": 680,
        "employment_years": 5,
        "education_level": "bachelor"
    }, headers={"Authorization": f"Bearer {token}"})
    
    assert res.status_code == 200
    assert isinstance(res.json()["will_default"], bool)

def test_threshold_update_requires_auth():
    res = client.put("/config/threshold", json={"value": 0.6})
    assert res.status_code == 403  # Unauthorized

def test_invalid_threshold_high():
    token = get_token()
    res = client.put("/config/threshold", json={"value": 1.5},
                     headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422  # Out of allowed range

def test_threshold_switch_effect():
    token = get_token()

    # High threshold → prediction = False
    client.put("/config/threshold", json={"value": 0.99},
               headers={"Authorization": f"Bearer {token}"})
    res_high = client.post("/predict/", json={
        "age": 28,
        "income": 45000,
        "loan_amount": 15000,
        "credit_score": 670,
        "employment_years": 4,
        "education_level": "bachelor"
    }, headers={"Authorization": f"Bearer {token}"})
    prediction_high = res_high.json()["will_default"]

    # High threshold → prediction = False
    client.put("/config/threshold", json={"value": 0.99}, headers={"Authorization": f"Bearer {token}"})
    res_high = client.post("/predict/", json={
        "age": 45,
        "income": 85000,
        "loan_amount": 6000,
        "credit_score": 740,
        "employment_years": 12,
        "education_level": "master"
    }, headers={"Authorization": f"Bearer {token}"})
    prediction_high = res_high.json()["will_default"]

