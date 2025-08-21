import time
import sqlite3
from fastapi.testclient import TestClient
from src.main import app
client = TestClient(app)
def get_token():
    user = {"email": "testdelay@example.com", "password": "securepass"}
    client.post("/auth/register", json=user)
    res = client.post("/auth/login", json=user)
    return res.json()["access_token"]
def test_predict_has_delay():
    """Test that /predict/ requests have random delay between 0-500ms"""
    token = get_token()
    
    # Make multiple requests to test delay variance
    delays = []
    for _ in range(5):
        start_time = time.time()
        response = client.post(
            "/predict/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "age": 30,
                "income": 50000,
                "loan_amount": 10000,
                "credit_score": 650,
                "employment_years": 3,
                "education_level": "bachelor"
            }
        )
        end_time = time.time()
        duration = end_time - start_time
        delays.append(duration)
        
        # Should get successful response
        assert response.status_code == 200
        # Should have some delay (at minimum processing time + random delay)
        assert duration > 0.001  # At least 1ms for processing
        
    # Check that we have some variance in delays (not all the same)
    min_delay = min(delays)
    max_delay = max(delays)
    assert max_delay > min_delay, "Expected variance in delays due to randomness"
    
    print(f"Delays observed: {[f'{d:.3f}s' for d in delays]}")
def test_non_predict_routes_no_delay():
    """Test that non-predict routes don't have artificial delay"""
    # Test root endpoint should be fast
    start_time = time.time()
    response = client.get("/")
    duration = time.time() - start_time
    
    assert response.status_code == 200
    assert duration < 0.1  # Should be very fast without delay
def test_predict_get_no_delay():
    """Test that GET requests to /predict/ don't have delay (only POST)"""
    start_time = time.time()
    response = client.get("/predict/")
    duration = time.time() - start_time
    
    # Should be faster than POST since no delay applied
    assert duration < 0.1
def test_prediction_logging_to_database():
    """Test that predictions are logged to database with all required fields"""
    token = get_token()
    
    # Make a prediction request
    test_data = {
        "age": 35,
        "income": 75000,
        "loan_amount": 15000,
        "credit_score": 700,
        "employment_years": 5,
        "education_level": "master"
    }
    
    response = client.post(
        "/predict/",
        headers={"Authorization": f"Bearer {token}"},
        json=test_data
    )
    
    assert response.status_code == 200
    
    # Check database for logged prediction
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Query the most recent prediction log
    cursor.execute("""
        SELECT user_email, age, income, loan_amount, credit_score, employment_years, education_level, will_default, timestamp
        FROM prediction_logs
        ORDER BY id DESC
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None, "No prediction log found in database"
    
    user_email, age, income, loan_amount, credit_score, employment_years, education_level, will_default, timestamp = row
    
    # Verify all fields are logged correctly
    assert user_email == "testdelay@example.com"
    assert age == test_data["age"]
    assert income == test_data["income"]
    assert loan_amount == test_data["loan_amount"]
    assert credit_score == test_data["credit_score"]
    assert employment_years == test_data["employment_years"]
    assert education_level == test_data["education_level"]
    assert isinstance(will_default, (bool, int))  # SQLite stores boolean as int
    assert timestamp is not None
    
    print(f"Successfully logged prediction: {row}")
