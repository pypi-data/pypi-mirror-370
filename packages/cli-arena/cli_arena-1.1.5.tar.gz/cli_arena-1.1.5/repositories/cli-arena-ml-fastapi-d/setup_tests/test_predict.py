from fastapi.testclient import TestClient
from src.main import app
from src.middleware import rate_limiter

client = TestClient(app)

def get_token():
    user = {"email": "predictuser@example.com", "password": "securepass"}
    client.post("/auth/register", json=user)
    res = client.post("/auth/login", json=user)
    return res.json()["access_token"]


def test_predict_default_false():
    """High income, low loan — expect no default"""
    token = get_token()
    response = client.post(
        "/predict/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "age": 30,
            "income": 80000,
            "loan_amount": 10000,
            "credit_score": 720,
            "employment_years": 5,
            "education_level": "bachelor"
        }
    )
    assert response.status_code == 200
    assert response.json()["will_default"] is False


def test_predict_default_true():
    """Low income, high loan, poor credit — expect default"""
    token = get_token()
    response = client.post(
        "/predict/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "age": 22,
            "income": 15000,
            "loan_amount": 20000,
            "credit_score": 400,
            "employment_years": 0,
            "education_level": "none"
        }
    )
    assert response.status_code == 200
    assert response.json()["will_default"] is True


def test_predict_all_zero_values():
    """Edge case: All zero values — expect default"""
    token = get_token()
    response = client.post(
        "/predict/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "age": 0,
            "income": 0,
            "loan_amount": 0,
            "credit_score": 0,
            "employment_years": 0,
            "education_level": "highschool"
        }
    )
    assert response.status_code == 200
    assert response.json()["will_default"] is True


def test_predict_extreme_values():
    """Edge case: Very high values — expect no default"""
    token = get_token()
    response = client.post(
        "/predict/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "age": 75,
            "income": 500000,
            "loan_amount": 5000,
            "credit_score": 850,
            "employment_years": 40,
            "education_level": "phd"
        }
    )
    assert response.status_code == 200
    assert response.json()["will_default"] is False


def test_missing_field():
    """Invalid input: Missing 'loan_amount' — expect validation error"""
    token = get_token()
    response = client.post(
        "/predict/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "age": 30,
            "income": 40000,
            # "loan_amount" is missing
            "credit_score": 600,
            "employment_years": 3,
            "education_level": "bachelor"
        }
    )
    assert response.status_code == 422


def test_invalid_data_type():
    """Invalid input: Wrong data types — expect validation error"""
    rate_limiter.clients.clear()
    token = get_token()
    response = client.post(
        "/predict/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "age": "thirty",
            "income": "forty thousand",
            "loan_amount": "ten thousand",
            "credit_score": "bad",
            "employment_years": "five",
            "education_level": 2  # should be str
        }
    )
    assert response.status_code == 422
