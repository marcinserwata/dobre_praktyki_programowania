import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from app import app, db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


def test_save_result(client):
    data = {
        'image_url': 'https://example.com/image.jpg',
        'people_count': 5
    }
    response = client.post('/results', json=data)
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['image_url'] == 'https://example.com/image.jpg'
    assert json_data['people_count'] == 5
    assert 'id' in json_data


def test_save_result_without_data(client):
    response = client.post('/results', json=None)
    assert response.status_code in [400, 415]


def test_save_result_missing_fields(client):
    data = {'image_url': 'https://example.com/image.jpg'}
    response = client.post('/results', json=data)
    assert response.status_code == 400


def test_get_results(client):
    data = {
        'image_url': 'https://example.com/image.jpg',
        'people_count': 3
    }
    client.post('/results', json=data)
    
    response = client.get('/results')
    assert response.status_code == 200
    results = response.get_json()
    assert len(results) == 1


def test_get_single_result(client):
    data = {
        'image_url': 'https://example.com/image.jpg',
        'people_count': 7
    }
    post_response = client.post('/results', json=data)
    result_id = post_response.get_json()['id']
    
    response = client.get(f'/results/{result_id}')
    assert response.status_code == 200
    assert response.get_json()['people_count'] == 7


def test_get_nonexistent_result(client):
    response = client.get('/results/999')
    assert response.status_code == 404


def test_delete_result(client):
    data = {
        'image_url': 'https://example.com/image.jpg',
        'people_count': 2
    }
    post_response = client.post('/results', json=data)
    result_id = post_response.get_json()['id']
    
    response = client.delete(f'/results/{result_id}')
    assert response.status_code == 200
    
    # Sprawdzamy czy rzeczywiście usunięto
    get_response = client.get(f'/results/{result_id}')
    assert get_response.status_code == 404


def test_delete_nonexistent_result(client):
    response = client.delete('/results/999')
    assert response.status_code == 404
