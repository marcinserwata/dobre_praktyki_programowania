from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from database import Base, get_db, User
import auth

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    admin_user = User(
        username="admin",
        hashed_password=auth.hash_password("admin123"),
        roles=["ROLE_ADMIN", "ROLE_USER"]
    )
    db.add(admin_user)
    db.commit()
    db.close()
    
    yield
    
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(setup_database):
    return TestClient(app)


@pytest.fixture(scope="module")
def admin_token(client):
    response = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"}
    )
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


class TestLogin:
    
    def test_login_success(self, client):
        response = client.post(
            "/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_username(self, client):
        response = client.post(
            "/login",
            json={"username": "nonexistent", "password": "admin123"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"
    
    def test_login_invalid_password(self, client):
        response = client.post(
            "/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"
    
    def test_login_empty_credentials(self, client):
        response = client.post(
            "/login",
            json={"username": "", "password": ""}
        )
        assert response.status_code == 401


class TestUserCreation:
    
    def test_create_user_as_admin(self, client, auth_headers):
        response = client.post(
            "/users",
            json={"username": "newuser", "password": "password123"},
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "ROLE_USER" in data["roles"]
    
    def test_create_user_without_auth(self, client):
        response = client.post(
            "/users",
            json={"username": "anotheruser", "password": "password123"}
        )
        assert response.status_code == 403
    
    def test_create_user_without_admin_role(self, client, auth_headers):
        client.post(
            "/users",
            json={"username": "regularuser", "password": "password123"},
            headers=auth_headers
        )
        
        login_response = client.post(
            "/login",
            json={"username": "regularuser", "password": "password123"}
        )
        regular_token = login_response.json()["access_token"]
        regular_headers = {"Authorization": f"Bearer {regular_token}"}
        
        response = client.post(
            "/users",
            json={"username": "shouldfail", "password": "password123"},
            headers=regular_headers
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Admin access required"
    
    def test_create_duplicate_user(self, client, auth_headers):
        client.post(
            "/users",
            json={"username": "duplicateuser", "password": "password123"},
            headers=auth_headers
        )
        
        response = client.post(
            "/users",
            json={"username": "duplicateuser", "password": "password123"},
            headers=auth_headers
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already exists"


class TestUserDetails:
    
    def test_get_user_details_success(self, client, auth_headers):
        response = client.get("/user_details", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert "ROLE_ADMIN" in data["roles"]
    
    def test_get_user_details_without_token(self, client):
        response = client.get("/user_details")
        assert response.status_code == 403
    
    def test_get_user_details_invalid_token(self, client):
        response = client.get(
            "/user_details",
            headers={"Authorization": "Bearer invalidtoken123"}
        )
        assert response.status_code == 401


class TestProtectedMovieEndpoints:
    
    def test_get_movies_with_auth(self, client, auth_headers):
        response = client.get("/movies", headers=auth_headers)
        assert response.status_code == 200
    
    def test_get_movies_without_auth(self, client):
        response = client.get("/movies")
        assert response.status_code == 403
    
    def test_create_movie_with_auth(self, client, auth_headers):
        response = client.post(
            "/movies",
            json={"movieId": 999999, "title": "Auth Test Movie", "genres": "Test"},
            headers=auth_headers
        )
        assert response.status_code == 201
    
    def test_create_movie_without_auth(self, client):
        response = client.post(
            "/movies",
            json={"movieId": 999998, "title": "Unauth Test Movie", "genres": "Test"}
        )
        assert response.status_code == 403
    
    def test_get_single_movie_with_auth(self, client, auth_headers):
        response = client.get("/movies/999999", headers=auth_headers)
        assert response.status_code == 200
    
    def test_update_movie_with_auth(self, client, auth_headers):
        response = client.put(
            "/movies/999999",
            json={"movieId": 999999, "title": "Updated Auth Test Movie", "genres": "Test"},
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_delete_movie_with_auth(self, client, auth_headers):
        response = client.delete("/movies/999999", headers=auth_headers)
        assert response.status_code == 204


class TestProtectedLinkEndpoints:
    
    def test_get_links_with_auth(self, client, auth_headers):
        response = client.get("/links", headers=auth_headers)
        assert response.status_code == 200
    
    def test_get_links_without_auth(self, client):
        response = client.get("/links")
        assert response.status_code == 403
    
    def test_create_link_with_auth(self, client, auth_headers):
        response = client.post(
            "/links",
            json={"movieId": 888888, "imdbId": "tt123456", "tmdbId": "123456"},
            headers=auth_headers
        )
        assert response.status_code == 201
    
    def test_delete_link_with_auth(self, client, auth_headers):
        response = client.delete("/links/888888", headers=auth_headers)
        assert response.status_code == 204


class TestProtectedRatingEndpoints:
    
    def test_get_ratings_with_auth(self, client, auth_headers):
        response = client.get("/ratings", headers=auth_headers)
        assert response.status_code == 200
    
    def test_get_ratings_without_auth(self, client):
        response = client.get("/ratings")
        assert response.status_code == 403
    
    def test_create_rating_with_auth(self, client, auth_headers):
        response = client.post(
            "/ratings",
            json={"userId": 1, "movieId": 1, "rating": 4.5, "timestamp": 123456789},
            headers=auth_headers
        )
        assert response.status_code == 201


class TestProtectedTagEndpoints:
    
    def test_get_tags_with_auth(self, client, auth_headers):
        response = client.get("/tags", headers=auth_headers)
        assert response.status_code == 200
    
    def test_get_tags_without_auth(self, client):
        response = client.get("/tags")
        assert response.status_code == 403
    
    def test_create_tag_with_auth(self, client, auth_headers):
        response = client.post(
            "/tags",
            json={"userId": 1, "movieId": 1, "tag": "test tag", "timestamp": 123456789},
            headers=auth_headers
        )
        assert response.status_code == 201


class TestTokenValidation:
    
    def test_expired_token(self, client):
        from datetime import datetime, timedelta, timezone
        import jwt
        
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "admin",
            "roles": ["ROLE_ADMIN"],
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1)
        }
        expired_token = jwt.encode(payload, auth.SECRET_KEY, algorithm=auth.ALGORITHM)
        
        response = client.get(
            "/movies",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    
    def test_malformed_token(self, client):
        response = client.get(
            "/movies",
            headers={"Authorization": "Bearer not.a.valid.token"}
        )
        assert response.status_code == 401
    
    def test_token_with_wrong_secret(self, client):
        from datetime import datetime, timedelta, timezone
        import jwt
        
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "admin",
            "roles": ["ROLE_ADMIN"],
            "iat": now,
            "exp": now + timedelta(hours=1)
        }
        wrong_token = jwt.encode(payload, "wrong_secret", algorithm="HS256")
        
        response = client.get(
            "/movies",
            headers={"Authorization": f"Bearer {wrong_token}"}
        )
        assert response.status_code == 401
