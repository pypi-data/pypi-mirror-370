from fastapi.testclient import TestClient
from src.main import app
import uuid

client = TestClient(app)

def get_token():
    unique_email = f"user_{uuid.uuid4().hex}@example.com"
    password = "securepass"
    client.post("/auth/register", json={"email": unique_email, "password": password})
    res = client.post("/auth/login", json={"email": unique_email, "password": password})
    assert res.status_code == 200, f"Login failed: {res.status_code}, {res.text}"
    return res.json()["access_token"]


def test_register_and_login_and_predict():
    """Valid registration, login, and prediction"""
    email = "testuser@example.com"
    password = "testpass"

    # Register
    res = client.post("/auth/register", json={"email": email, "password": password})
    assert res.status_code in (200, 400)  # Already registered case OK

    # Login
    res = client.post("/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    token = res.json()["access_token"]

    # Access prediction
    predict_input = {
        "age": 35,
        "income": 60000,
        "loan_amount": 12000,
        "credit_score": 700,
        "employment_years": 4,
        "education_level": "bachelor"
    }
    res = client.post("/predict/", json=predict_input, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "will_default" in res.json()


def test_invalid_token():
    """Should return 401 or 403 for bad token"""
    res = client.post(
        "/predict/",
        json={
            "age": 30, "income": 50000, "loan_amount": 10000,
            "credit_score": 600, "employment_years": 3, "education_level": "bachelor"
        },
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert res.status_code in (401, 403), f"Expected 401 or 403, got {res.status_code}"

def test_missing_fields():
    """Missing loan_amount should raise validation error"""
    token = get_token()
    res = client.post(
        "/predict/",
        json={
            "age": 30,
            "income": 50000,
            # missing loan_amount
            "credit_score": 600,
            "employment_years": 3,
            "education_level": "bachelor"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 422


def test_invalid_data_type():
    """Invalid data types should raise 422"""
    token = get_token()
    res = client.post(
        "/predict/",
        json={
            "age": "thirty",  # should be int
            "income": "fifty thousand",  # should be float
            "loan_amount": "ten",  # should be float
            "credit_score": "high",  # should be float
            "employment_years": "five",  # should be int
            "education_level": 123  # should be str
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 422

def test_duplicate_registration():
    """Registering the same user twice should return 400"""
    import uuid
    email = f"dupuser_{uuid.uuid4().hex}@example.com"
    password = "mypassword"

    # First registration
    res1 = client.post("/auth/register", json={"email": email, "password": password})
    assert res1.status_code == 200, f"First registration failed: {res1.status_code}"

    # Duplicate registration
    res2 = client.post("/auth/register", json={"email": email, "password": password})
    assert res2.status_code == 400, f"Expected 400 for duplicate, got {res2.status_code}"

def test_high_risk_prediction():
    """Low income, high loan — expect default = True"""
    token = get_token()
    res = client.post(
        "/predict/",
        json={
            "age": 22,
            "income": 10000,
            "loan_amount": 50000,
            "credit_score": 400,
            "employment_years": 0,
            "education_level": "none"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["will_default"] is True
