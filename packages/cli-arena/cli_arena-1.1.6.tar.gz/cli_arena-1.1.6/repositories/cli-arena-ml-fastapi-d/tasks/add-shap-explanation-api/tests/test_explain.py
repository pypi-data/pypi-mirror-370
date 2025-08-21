from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def get_token():
    res = client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "secret123"
    })
    return res.json()["access_token"]

def test_shap_returns_success():
    token = get_token()
    res = client.post("/explain/", json=valid_payload(), headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "explanation" in res.json()

def test_shap_keys_match_input_features():
    token = get_token()
    res = client.post("/explain/", json=valid_payload(), headers={"Authorization": f"Bearer {token}"})
    explanation = res.json()["explanation"]
    expected_keys = ["age", "income", "loan_amount", "credit_score", "employment_years", "education_level"]
    assert sorted(explanation.keys()) == sorted(expected_keys)

def test_shap_values_are_numeric():
    token = get_token()
    res = client.post("/explain/", json=valid_payload(), headers={"Authorization": f"Bearer {token}"})
    explanation = res.json()["explanation"]
    assert all(isinstance(v, (int, float)) for v in explanation.values())

def test_invalid_token_rejected():
    res = client.post("/explain/", json=valid_payload(), headers={"Authorization": "Bearer invalidtoken"})
    assert res.status_code == 401 or res.status_code == 403

def test_missing_field_rejected():
    token = get_token()
    bad_payload = valid_payload()
    del bad_payload["income"]
    res = client.post("/explain/", json=bad_payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422

def test_shap_explanation_is_stable_for_same_input():
    token = get_token()
    input_data = valid_payload()

    res1 = client.post("/explain/", json=input_data, headers={"Authorization": f"Bearer {token}"})
    res2 = client.post("/explain/", json=input_data, headers={"Authorization": f"Bearer {token}"})

    values1 = res1.json()["explanation"]
    values2 = res2.json()["explanation"]

    # Not exact, but close — same input should give near-identical explanation
    diffs = [abs(values1[k] - values2[k]) for k in values1]
    assert all(d < 1e-3 for d in diffs)

def valid_payload():
    return {
        "age": 40,
        "income": 70000,
        "loan_amount": 10000,
        "credit_score": 730,
        "employment_years": 8,
        "education_level": "master"
    }
