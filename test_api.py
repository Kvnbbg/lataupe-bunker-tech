import json

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_api_metrics(client):
    response = client.get('/api/metrics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'oxygen_level' in data
