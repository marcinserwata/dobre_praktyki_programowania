import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from app import app
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


def test_analyze_without_data(client):
    response = client.post('/analyze', json=None)
    assert response.status_code in [400, 415]


def test_analyze_missing_image_url(client):
    response = client.post('/analyze', json={'other_field': 'value'})
    assert response.status_code == 400
    assert 'image_url' in response.get_json()['error']


@patch('app.get_rabbitmq_connection')
def test_analyze_success(mock_connection, client):
    mock_channel = MagicMock()
    mock_conn = MagicMock()
    mock_conn.channel.return_value = mock_channel
    mock_connection.return_value = mock_conn
    
    data = {'image_url': 'https://example.com/image.jpg'}
    response = client.post('/analyze', json=data)
    
    assert response.status_code == 202
    json_data = response.get_json()
    assert 'kolejki' in json_data['message']
    assert json_data['image_url'] == 'https://example.com/image.jpg'
    
    mock_channel.basic_publish.assert_called_once()


@patch('app.get_rabbitmq_connection')
def test_analyze_rabbitmq_error(mock_connection, client):
    mock_connection.side_effect = Exception("Connection failed")
    
    data = {'image_url': 'https://example.com/image.jpg'}
    response = client.post('/analyze', json=data)
    
    assert response.status_code == 500
    assert 'Błąd' in response.get_json()['error']
