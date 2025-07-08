# Guide d'Intégration d'API - Lataupe Bunker Tech

## Vue d'Ensemble

Ce guide détaille les possibilités d'intégration d'API externes avec le MVP Lataupe Bunker Tech. L'architecture modulaire permet de remplacer facilement les services de simulation par de vraies API pour créer un système de production complet.

## Architecture d'Intégration

### Pattern Adapter

L'application utilise le pattern Adapter pour encapsuler les API externes :

```python
class WeatherAPIAdapter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, location):
        # Implémentation de l'API OpenWeatherMap
        response = requests.get(f"{self.base_url}/weather", params={
            'q': location,
            'appid': self.api_key,
            'units': 'metric'
        })
        return self._normalize_data(response.json())
    
    def _normalize_data(self, raw_data):
        # Normalisation vers le format interne
        return {
            'temperature': raw_data['main']['temp'],
            'humidity': raw_data['main']['humidity'],
            'pressure': raw_data['main']['pressure']
        }
```

## APIs Recommandées

### 1. Données Météorologiques

**OpenWeatherMap API**
- URL: https://openweathermap.org/api
- Fonctionnalités: Météo actuelle, prévisions, données historiques
- Coût: Gratuit jusqu'à 1000 appels/jour

**AccuWeather API**
- URL: https://developer.accuweather.com/
- Fonctionnalités: Météo précise, alertes météo, indices de qualité de l'air
- Coût: Gratuit jusqu'à 50 appels/jour

### 2. Qualité de l'Air

**AirVisual API**
- URL: https://www.iqair.com/air-pollution-data-api
- Fonctionnalités: Qualité de l'air en temps réel, prévisions pollution
- Données: PM2.5, PM10, O3, NO2, SO2, CO

**EPA AirNow API**
- URL: https://www.airnow.gov/index.cfm?action=webservices.index
- Fonctionnalités: Données officielles EPA, indices de qualité de l'air
- Couverture: États-Unis principalement

### 3. Communication SMS

**Twilio API**
- URL: https://www.twilio.com/docs/sms
- Fonctionnalités: SMS, MMS, WhatsApp, appels vocaux
- Fiabilité: 99.95% uptime SLA

```python
class TwilioSMSAdapter:
    def __init__(self, account_sid, auth_token):
        self.client = Client(account_sid, auth_token)
    
    def send_sms(self, to_number, message, from_number):
        try:
            message = self.client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            return {
                'status': 'sent',
                'message_id': message.sid,
                'cost': message.price
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
```

### 4. Communication Email

**SendGrid API**
- URL: https://sendgrid.com/docs/api-reference/
- Fonctionnalités: Email transactionnel, templates, analytics
- Gratuit: 100 emails/jour

**Amazon SES**
- URL: https://aws.amazon.com/ses/
- Fonctionnalités: Email haute délivrabilité, bounce handling
- Coût: $0.10 pour 1000 emails

### 5. Capteurs IoT

**ThingSpeak API**
- URL: https://thingspeak.com/docs
- Fonctionnalités: Collecte de données IoT, visualisation, analytics
- Gratuit: 3 millions messages/an

**Arduino IoT Cloud**
- URL: https://docs.arduino.cc/arduino-cloud/
- Fonctionnalités: Gestion d'appareils, données temps réel
- Intégration: Arduino, ESP32, Raspberry Pi

## Implémentation des Intégrations

### 1. Service de Données Environnementales Réelles

```python
# src/services/real_data_service.py
import requests
from datetime import datetime
from ..models.bunker import EnvironmentalData

class RealEnvironmentalDataService:
    def __init__(self, weather_api, air_quality_api):
        self.weather_api = weather_api
        self.air_quality_api = air_quality_api
    
    def collect_current_data(self, location):
        # Collecte depuis APIs externes
        weather_data = self.weather_api.get_current_weather(location)
        air_data = self.air_quality_api.get_air_quality(location)
        
        # Création de l'enregistrement
        env_data = EnvironmentalData(
            temperature=weather_data['temperature'],
            humidity=weather_data['humidity'],
            air_quality=air_data['aqi'],
            oxygen_level=self._calculate_oxygen(air_data),
            co2_level=air_data.get('co2', 400),
            uv_radiation=weather_data.get('uv_index', 0),
            timestamp=datetime.utcnow()
        )
        
        return env_data
    
    def _calculate_oxygen(self, air_data):
        # Calcul du niveau d'oxygène basé sur la qualité de l'air
        base_oxygen = 20.9  # Niveau normal d'oxygène
        pollution_factor = air_data['aqi'] / 100
        return max(16.0, base_oxygen - (pollution_factor * 2))
```

### 2. Service de Communication Réelle

```python
# src/services/real_communication_service.py
from twilio.rest import Client
import sendgrid
from sendgrid.helpers.mail import Mail

class RealCommunicationService:
    def __init__(self, twilio_config, sendgrid_config):
        self.twilio_client = Client(
            twilio_config['account_sid'],
            twilio_config['auth_token']
        )
        self.sendgrid_client = sendgrid.SendGridAPIClient(
            api_key=sendgrid_config['api_key']
        )
    
    def send_emergency_sms(self, phone_number, message):
        try:
            message = self.twilio_client.messages.create(
                body=f"🚨 URGENCE BUNKER: {message}",
                from_='+1234567890',  # Votre numéro Twilio
                to=phone_number
            )
            return {
                'status': 'sent',
                'message_id': message.sid,
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
    
    def send_emergency_email(self, email, subject, content):
        try:
            message = Mail(
                from_email='bunker@emergency.com',
                to_emails=email,
                subject=f"🚨 {subject}",
                html_content=f"""
                <h2>Alerte d'Urgence - Bunker</h2>
                <p><strong>Heure:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                <p><strong>Message:</strong></p>
                <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545;">
                    {content}
                </div>
                <p><em>Message automatique du système de surveillance bunker</em></p>
                """
            )
            
            response = self.sendgrid_client.send(message)
            return {
                'status': 'sent',
                'status_code': response.status_code,
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
```

### 3. Intégration MQTT pour Capteurs IoT

```python
# src/services/mqtt_sensor_service.py
import paho.mqtt.client as mqtt
import json
from datetime import datetime

class MQTTSensorService:
    def __init__(self, broker_host, broker_port, username=None, password=None):
        self.client = mqtt.Client()
        self.broker_host = broker_host
        self.broker_port = broker_port
        
        if username and password:
            self.client.username_pw_set(username, password)
        
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.data_callback = None
    
    def _on_connect(self, client, userdata, flags, rc):
        print(f"Connecté au broker MQTT avec le code {rc}")
        # S'abonner aux topics des capteurs
        client.subscribe("bunker/sensors/+/data")
    
    def _on_message(self, client, userdata, msg):
        try:
            # Décoder le message JSON
            sensor_data = json.loads(msg.payload.decode())
            topic_parts = msg.topic.split('/')
            sensor_id = topic_parts[2]
            
            # Traiter les données selon le type de capteur
            processed_data = self._process_sensor_data(sensor_id, sensor_data)
            
            # Callback vers l'application principale
            if self.data_callback:
                self.data_callback(processed_data)
                
        except Exception as e:
            print(f"Erreur traitement message MQTT: {e}")
    
    def _process_sensor_data(self, sensor_id, raw_data):
        # Normalisation des données selon le capteur
        sensor_mapping = {
            'temp_hum_01': {
                'temperature': raw_data.get('temp'),
                'humidity': raw_data.get('hum')
            },
            'air_quality_01': {
                'air_quality': raw_data.get('aqi'),
                'co2_level': raw_data.get('co2')
            },
            'oxygen_01': {
                'oxygen_level': raw_data.get('o2_percent')
            }
        }
        
        return {
            'sensor_id': sensor_id,
            'timestamp': datetime.utcnow(),
            'data': sensor_mapping.get(sensor_id, raw_data)
        }
    
    def start_monitoring(self, data_callback):
        self.data_callback = data_callback
        self.client.connect(self.broker_host, self.broker_port, 60)
        self.client.loop_start()
    
    def stop_monitoring(self):
        self.client.loop_stop()
        self.client.disconnect()
```

## Configuration des API

### Variables d'Environnement

```bash
# APIs Météo
OPENWEATHER_API_KEY=your_openweather_api_key
ACCUWEATHER_API_KEY=your_accuweather_api_key

# APIs Communication
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
SENDGRID_API_KEY=your_sendgrid_api_key

# APIs Qualité de l'Air
AIRVISUAL_API_KEY=your_airvisual_api_key

# MQTT Broker
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=bunker_user
MQTT_PASSWORD=secure_password

# Configuration Bunker
BUNKER_LOCATION=Paris,FR
EMERGENCY_CONTACTS=+33123456789,admin@bunker.com
```

### Fichier de Configuration

```python
# src/config/api_config.py
import os

class APIConfig:
    # Météo
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
    OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5'
    
    # Communication
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'bunker@emergency.com')
    
    # MQTT
    MQTT_BROKER_HOST = os.environ.get('MQTT_BROKER_HOST', 'localhost')
    MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT', 1883))
    MQTT_USERNAME = os.environ.get('MQTT_USERNAME')
    MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
    
    # Bunker
    BUNKER_LOCATION = os.environ.get('BUNKER_LOCATION', 'Paris,FR')
    EMERGENCY_CONTACTS = os.environ.get('EMERGENCY_CONTACTS', '').split(',')
```

## Migration vers les API Réelles

### Étape 1: Installation des Dépendances

```bash
pip install twilio sendgrid paho-mqtt requests python-dotenv
```

### Étape 2: Modification du Service Principal

```python
# src/services/service_factory.py
from .data_simulator import DataSimulator
from .real_data_service import RealEnvironmentalDataService
from .message_sender import MessageSender
from .real_communication_service import RealCommunicationService

class ServiceFactory:
    @staticmethod
    def create_data_service(use_real_apis=False):
        if use_real_apis:
            return RealEnvironmentalDataService(
                weather_api=WeatherAPIAdapter(),
                air_quality_api=AirQualityAPIAdapter()
            )
        else:
            return DataSimulator()
    
    @staticmethod
    def create_communication_service(use_real_apis=False):
        if use_real_apis:
            return RealCommunicationService(
                twilio_config={
                    'account_sid': APIConfig.TWILIO_ACCOUNT_SID,
                    'auth_token': APIConfig.TWILIO_AUTH_TOKEN
                },
                sendgrid_config={
                    'api_key': APIConfig.SENDGRID_API_KEY
                }
            )
        else:
            return MessageSender()
```

### Étape 3: Configuration du Mode Production

```python
# src/main.py
import os
from .services.service_factory import ServiceFactory

# Déterminer le mode selon l'environnement
USE_REAL_APIS = os.environ.get('USE_REAL_APIS', 'false').lower() == 'true'

# Initialiser les services
data_service = ServiceFactory.create_data_service(USE_REAL_APIS)
communication_service = ServiceFactory.create_communication_service(USE_REAL_APIS)
```

## Tests d'Intégration

### Test des API Externes

```python
# tests/test_api_integration.py
import unittest
from unittest.mock import patch, Mock
from src.services.real_data_service import RealEnvironmentalDataService

class TestAPIIntegration(unittest.TestCase):
    
    @patch('requests.get')
    def test_weather_api_integration(self, mock_get):
        # Mock de la réponse API
        mock_response = Mock()
        mock_response.json.return_value = {
            'main': {
                'temp': 22.5,
                'humidity': 65
            }
        }
        mock_get.return_value = mock_response
        
        # Test du service
        service = RealEnvironmentalDataService(
            weather_api=WeatherAPIAdapter('test_key'),
            air_quality_api=Mock()
        )
        
        data = service.collect_current_data('Paris,FR')
        
        self.assertEqual(data.temperature, 22.5)
        self.assertEqual(data.humidity, 65)
    
    def test_communication_service_sms(self):
        # Test avec vraies API (nécessite configuration)
        if os.environ.get('TWILIO_ACCOUNT_SID'):
            service = RealCommunicationService(
                twilio_config={
                    'account_sid': os.environ.get('TWILIO_ACCOUNT_SID'),
                    'auth_token': os.environ.get('TWILIO_AUTH_TOKEN')
                },
                sendgrid_config={}
            )
            
            # Test SMS (remplacer par un vrai numéro de test)
            result = service.send_emergency_sms(
                '+33123456789',
                'Test message from bunker system'
            )
            
            self.assertEqual(result['status'], 'sent')
```

## Monitoring et Observabilité

### Métriques d'API

```python
# src/monitoring/api_metrics.py
import time
from functools import wraps
from collections import defaultdict

class APIMetrics:
    def __init__(self):
        self.call_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_counts = defaultdict(int)
    
    def track_api_call(self, api_name):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    self.call_counts[api_name] += 1
                    response_time = time.time() - start_time
                    self.response_times[api_name].append(response_time)
                    return result
                except Exception as e:
                    self.error_counts[api_name] += 1
                    raise
            return wrapper
        return decorator
    
    def get_metrics(self):
        return {
            'call_counts': dict(self.call_counts),
            'avg_response_times': {
                api: sum(times) / len(times) if times else 0
                for api, times in self.response_times.items()
            },
            'error_rates': {
                api: self.error_counts[api] / max(1, self.call_counts[api])
                for api in self.call_counts.keys()
            }
        }
```

## Sécurité des API

### Gestion Sécurisée des Clés

```python
# src/security/api_security.py
import os
import hashlib
from cryptography.fernet import Fernet

class APIKeyManager:
    def __init__(self):
        self.encryption_key = os.environ.get('API_ENCRYPTION_KEY')
        if self.encryption_key:
            self.cipher = Fernet(self.encryption_key.encode())
    
    def encrypt_api_key(self, api_key):
        if self.cipher:
            return self.cipher.encrypt(api_key.encode()).decode()
        return api_key
    
    def decrypt_api_key(self, encrypted_key):
        if self.cipher:
            return self.cipher.decrypt(encrypted_key.encode()).decode()
        return encrypted_key
    
    def validate_api_key_format(self, api_key, expected_pattern):
        import re
        return bool(re.match(expected_pattern, api_key))
```

Ce guide fournit une base complète pour intégrer des API réelles dans le MVP Lataupe Bunker Tech, transformant le système de simulation en une solution de production robuste et fonctionnelle.

