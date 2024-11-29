import pytest
from httpx import AsyncClient  

# Configuration du client asynchrone pour les tests
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_register_user(async_client):
    """Test pour l'inscription d'un utilisateur."""
    user_data = {
        "nom": "sisi",
        "prenom": "mzali",
        "date_naissance": "1990-01-01T00:00:00",
        "telephone": "+21612345678",
        "adresse": "123 Rue Exemple",
        "email": "sisimzali@example.com",
        "username": "sisi",
        "password": "password123"
    }

    # Requête POST pour l'inscription
    response = await async_client.post("/users/register", json=user_data)

    # Vérifications
    assert response.status_code == 201
    response_data = response.json()
    assert "_id" in response_data  # Vérifie que l'ID est retourné
    assert response_data["message"] == "User created successfully"


@pytest.mark.asyncio
async def test_login_user(async_client):
    """Test pour la connexion d'un utilisateur."""
    user_data = {
        "email": "sisimzali@example.com",
        "password": "password123"
    }

    # Requête POST pour la connexion
    response = await async_client.post("/users/login", json=user_data)

    # Vérifications
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_my_profile(async_client):
    """Test pour récupérer le profil de l'utilisateur connecté."""
    login_data = {
        "email": "sisimzali@example.com",
        "password": "password123"
    }

    # Connexion de l'utilisateur pour récupérer le token
    login_response = await async_client.post("/users/login", json=login_data)
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Requête GET pour récupérer le profil
    profile_response = await async_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Vérifications
    assert profile_response.status_code == 200
    response_data = profile_response.json()
    assert response_data["email"] == "sisimzali@example.com"
