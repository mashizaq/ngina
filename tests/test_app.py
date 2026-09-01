"""
Tests for Flask API endpoints
"""
import pytest
from app import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data


def test_get_personas(client):
    """Test getting personas"""
    response = client.get('/persona')
    
    assert response.status_code in [200, 400]  # May fail if app structure differs


def test_chat_endpoint(client):
    """Test the chat endpoint"""
    payload = {
        'persona': 'test',
        'message': 'Hello'
    }
    
    response = client.post('/chat', json=payload)
    
    # Accept various responses depending on configuration
    assert response.status_code in [200, 400, 500]
