from fastapi.testclient import TestClient
from app.main import app  # Ensure this points correctly to your FastAPI 'app' object

client = TestClient(app)

def test_read_root():
    # Tests your "/" (Read Root) route
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_claims():
    # Tests your GET "/claims/" route
    response = client.get("/claims/")
    assert response.status_code == 200
    # Verifies that it returns a list (even if empty)
    assert isinstance(response.json(), list)

def test_read_root():
    # This 'hits' the root endpoint of your API
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

