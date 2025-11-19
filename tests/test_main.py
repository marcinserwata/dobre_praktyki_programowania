from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from database import Base, get_db

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Tests for Movies
def test_create_movie():
    response = client.post(
        "/movies",
        json={"movieId": 100000, "title": "Test Movie", "genres": "Test|Genre"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["movieId"] == 100000
    assert data["title"] == "Test Movie"

def test_read_movie():
    response = client.get("/movies/100000")
    assert response.status_code == 200
    data = response.json()
    assert data["movieId"] == 100000
    assert data["title"] == "Test Movie"

def test_read_movie_not_found():
    response = client.get("/movies/999999")
    assert response.status_code == 404

def test_update_movie():
    response = client.put(
        "/movies/100000",
        json={"movieId": 100000, "title": "Updated Movie", "genres": "Test|Genre"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Movie"

def test_delete_movie():
    response = client.delete("/movies/100000")
    assert response.status_code == 204
    response = client.get("/movies/100000")
    assert response.status_code == 404

# Tests for Links
def test_create_link():
    response = client.post(
        "/links",
        json={"movieId": 100000, "imdbId": "123456", "tmdbId": "654321"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["movieId"] == 100000
    assert data["imdbId"] == "123456"

def test_read_link():
    response = client.get("/links/100000")
    assert response.status_code == 200
    data = response.json()
    assert data["imdbId"] == "123456"

def test_update_link():
    response = client.put(
        "/links/100000",
        json={"movieId": 100000, "imdbId": "654321", "tmdbId": "123456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imdbId"] == "654321"

def test_delete_link():
    response = client.delete("/links/100000")
    assert response.status_code == 204
    response = client.get("/links/100000")
    assert response.status_code == 404

# Tests for Ratings
def test_create_rating():
    response = client.post(
        "/ratings",
        json={"userId": 1, "movieId": 1, "rating": 5.0, "timestamp": 123456789},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5.0

def test_read_rating():
    response = client.get("/ratings")
    data = response.json()
    assert len(data) > 0
    last_rating = data[-1]
    rating_id = last_rating["id"]
    
    response = client.get(f"/ratings/{rating_id}")
    assert response.status_code == 200
    assert response.json()["rating"] == 5.0

def test_update_rating():
    response = client.get("/ratings")
    data = response.json()
    last_rating = data[-1]
    rating_id = last_rating["id"]

    response = client.put(
        f"/ratings/{rating_id}",
        json={"userId": 1, "movieId": 1, "rating": 4.0, "timestamp": 123456789},
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 4.0

def test_delete_rating():
    response = client.get("/ratings")
    data = response.json()
    last_rating = data[-1]
    rating_id = last_rating["id"]

    response = client.delete(f"/ratings/{rating_id}")
    assert response.status_code == 204
    response = client.get(f"/ratings/{rating_id}")
    assert response.status_code == 404

# Tests for Tags
def test_create_tag():
    response = client.post(
        "/tags",
        json={"userId": 1, "movieId": 1, "tag": "funny", "timestamp": 123456789},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tag"] == "funny"

def test_read_tag():
    response = client.get("/tags")
    data = response.json()
    last_tag = data[-1]
    tag_id = last_tag["id"]
    
    response = client.get(f"/tags/{tag_id}")
    assert response.status_code == 200
    assert response.json()["tag"] == "funny"

def test_update_tag():
    response = client.get("/tags")
    data = response.json()
    last_tag = data[-1]
    tag_id = last_tag["id"]

    response = client.put(
        f"/tags/{tag_id}",
        json={"userId": 1, "movieId": 1, "tag": "very funny", "timestamp": 123456789},
    )
    assert response.status_code == 200
    assert response.json()["tag"] == "very funny"

def test_delete_tag():
    response = client.get("/tags")
    data = response.json()
    last_tag = data[-1]
    tag_id = last_tag["id"]

    response = client.delete(f"/tags/{tag_id}")
    assert response.status_code == 204
    response = client.get(f"/tags/{tag_id}")
    assert response.status_code == 404
