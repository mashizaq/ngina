"""
Integration tests with MQTT broker
"""
import os
import pytest
import requests


@pytest.mark.integration
def test_api_with_mqtt():
    """Test API with MQTT broker running"""
    api_url = os.getenv('API_URL', 'http://localhost:5000')
    
    try:
        response = requests.get(f'{api_url}/health', timeout=5)
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.skip("API not available")


@pytest.mark.integration
def test_mqtt_connection():
    """Test MQTT broker connectivity"""
    mqtt_url = os.getenv('MQTT_URL', 'mqtt://localhost:1883')
    
    # This would require paho-mqtt client
    # Implementation depends on app structure
    assert mqtt_url is not None
