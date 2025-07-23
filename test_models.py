from main_railway import User, BunkerMetric, Alert

def test_new_user():
    user = User(username='testuser', email='test@test.com', password_hash='hashed')
    assert user.username == 'testuser'
    assert user.email == 'test@test.com'

def test_new_metric():
    metric = BunkerMetric(metric_type='temperature', value=21.5, unit='C')
    assert metric.metric_type == 'temperature'
    assert metric.value == 21.5
