import pytest
from fastapi.testclient import TestClient
from main import app
import asyncio

# Si vous avez des tests asynchrones, vous devez explicitement définir un gestionnaire de boucle d'événements.
@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
client = TestClient(app)


def test_register_user():
    user_data = {
        "nom": "Sisi",
        "prenom": "Mzali",
        "date_naissance": "1990-01-01T00:00:00",
        "telephone": "+21612345678",
        "adresse": "123 Rue Exemple",
        "email": "sisimzali@example.com",
        "username": "sisi",
        "password": "password123"
    }
    response = client.post("/users/register", json=user_data)
    assert response.status_code == 201
    assert "_id" in response.json()

def test_login_user():
    user_data = {
        "email": "sisimzali@example.com",
        "password": "password123"
    }
    response = client.post("/users/login", json=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_my_profile():
    login_data = {
        "email": "sisimzali@example.com",
        "password": "password123"
    }
    login_response = client.post("/users/login", json=login_data)
    access_token = login_response.json()["access_token"]

    profile_response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "sisimzali@example.com"
#pytest tests/
