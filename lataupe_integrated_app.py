#!/usr/bin/env python3
"""
Lataupe Bunker Tech - Integrated Application
A comprehensive underground survival system with microservices architecture,
premium features, Stripe integration, and comprehensive testing.

Author: Kevin Marville
Version: 2.0.0
License: MIT
"""

import os
import sys
import json
import time
import random
import logging
import hashlib
import secrets
import unittest
import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
from dataclasses import dataclass, asdict

# Flask and extensions
from flask import Flask, request, jsonify, session, send_from_directory, g, render_template_string
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# JWT and encryption
try:
    import jwt
    import bcrypt
    from marshmallow import Schema, fields, ValidationError
    from bleach import clean
except ImportError:
    print("Installing required packages...")
    os.system("pip install PyJWT bcrypt marshmallow bleach")
    import jwt
    import bcrypt
    from marshmallow import Schema, fields, ValidationError
    from bleach import clean

# ============================================================================
# SECURITY AND VALIDATION LAYER
# ============================================================================

class SecurityManager:
    """Comprehensive security management"""
    
    ALLOWED_HTML_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    ALLOWED_ATTRIBUTES = {}
    
    @staticmethod
    def sanitize_input(data: str) -> str:
        """Sanitize user input to prevent XSS"""
        if not isinstance(data, str):
            return str(data)
        
        # Remove HTML tags and malicious content
        cleaned = clean(data, tags=SecurityManager.ALLOWED_HTML_TAGS, 
                       attributes=SecurityManager.ALLOWED_ATTRIBUTES, strip=True)
        
        # Remove SQL injection patterns
        sql_patterns = [
            r'(union|select|insert|update|delete|drop|create|alter|exec|execute)',
            r'(\-\-|\/\*|\*\/)',
            r'(script|javascript|vbscript|onload|onerror|onclick)'
        ]
        
        for pattern in sql_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength': 'strong' if len(errors) == 0 else 'weak'
        }
    
    @staticmethod
    def generate_secure_token() -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def rate_limit_check(identifier: str, max_requests: int = 10, window: int = 60) -> bool:
        """Simple rate limiting check"""
        # Implementation would use Redis or similar in production
        # For now, we'll use a simple in-memory store
        if not hasattr(SecurityManager, '_rate_limit_store'):
            SecurityManager._rate_limit_store = {}
        
        now = time.time()
        key = f"{identifier}:{int(now // window)}"
        
        current_count = SecurityManager._rate_limit_store.get(key, 0)
        if current_count >= max_requests:
            return False
        
        SecurityManager._rate_limit_store[key] = current_count + 1
        return True

# ============================================================================
# VALIDATION SCHEMAS
# ============================================================================

class LoginSchema(Schema):
    """Login validation schema"""
    username = fields.Str(required=True, validate=lambda x: len(x) >= 3)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 8)

class RegisterSchema(Schema):
    """Registration validation schema"""
    username = fields.Str(required=True, validate=lambda x: len(x) >= 3)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 8)
    confirm_password = fields.Str(required=True)

class EnvironmentalDataSchema(Schema):
    """Environmental data validation schema"""
    bunker_id = fields.Str(required=True, validate=lambda x: len(x) >= 3)
    temperature = fields.Float(validate=lambda x: -50 <= x <= 50)
    humidity = fields.Float(validate=lambda x: 0 <= x <= 100)
    oxygen_level = fields.Float(validate=lambda x: 0 <= x <= 25)
    co2_level = fields.Float(validate=lambda x: 0 <= x <= 10000)
    radiation_level = fields.Float(validate=lambda x: 0 <= x <= 100)

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'lataupe-bunker-ultra-secret-2025')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-ultra-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///lataupe_bunker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
    
    # Stripe Configuration
    STRIPE_PUBLISHABLE_KEY = 'pk_live_51QrrpyAgNXcbbeAvW0sQk7AKth6aNLyiIGLONux6z07z9oRAt0aCvXwq2d5H5jIwSMOgEDieSaGq08Ksvqvq8dB500qVZIIXrF'
    STRIPE_BUY_BUTTON_ID = 'buy_btn_1Rj3FlAgNXcbbeAvd7p20Qgi'
    
    # Social Links
    SOCIAL_LINKS = {
        'allmylinks': 'https://allmylinks.com/kevinmarville',
        'github': 'https://github.com/Kvnbbg/',
        'matrix': 'https://matrix.to/#/@kvnbbg:matrix.org',
        'telegram': 'https://t.me/kevinmarville',
        'patreon': 'https://patreon.com/kvnbbg',
        'coffee': 'https://coff.ee/kevinmarville',
        'kofi': 'https://ko-fi.com/kvnbbg'
    }
    
    # Railway Configuration
    RAILWAY_REFERRAL = 'https://railway.com?referralCode=74Ni9C'
    RAILWAY_DEPLOY = 'https://railway.com/deploy/lzsD1L?referralCode=74Ni9C'

# ============================================================================
# LOGGING SERVICE
# ============================================================================

class BunkerLogger:
    """Centralized logging service with structured JSON output"""
    
    def __init__(self, name: str = "lataupe_bunker", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        if not self.logger.handlers:
            # Console handler with JSON formatting
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # File handler for persistent logging
            file_handler = logging.FileHandler('lataupe_bunker.log')
            file_handler.setLevel(logging.DEBUG)
            
            # Custom formatter for structured logging
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
    def _format_log_entry(self, level: str, message: str, extra: Optional[Dict] = None) -> Dict[str, Any]:
        """Format log entry as structured JSON"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'service': 'lataupe_bunker_tech',
            'version': '2.0.0'
        }
        
        if extra:
            entry.update(extra)
        
        return entry
    
    def info(self, message: str, extra: Optional[Dict] = None):
        """Log info message"""
        log_entry = self._format_log_entry('INFO', message, extra)
        self.logger.info(json.dumps(log_entry))
    
    def warning(self, message: str, extra: Optional[Dict] = None):
        """Log warning message"""
        log_entry = self._format_log_entry('WARNING', message, extra)
        self.logger.warning(json.dumps(log_entry))
    
    def error(self, message: str, extra: Optional[Dict] = None, exc_info: bool = False):
        """Log error message"""
        log_entry = self._format_log_entry('ERROR', message, extra)
        self.logger.error(json.dumps(log_entry), exc_info=exc_info)
    
    def debug(self, message: str, extra: Optional[Dict] = None):
        """Log debug message"""
        log_entry = self._format_log_entry('DEBUG', message, extra)
        self.logger.debug(json.dumps(log_entry))

# Global logger instance
bunker_logger = BunkerLogger()

# ============================================================================
# DATABASE MODELS
# ============================================================================

# Initialize Flask app and database
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, supports_credentials=True, origins=app.config['CORS_ORIGINS'])

class User(db.Model):
    """User model with authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='resident')
    is_premium = db.Column(db.Boolean, default=False)
    premium_tier = db.Column(db.String(20), default='free')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password: str):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_premium': self.is_premium,
            'premium_tier': self.premium_tier,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class BunkerUser(db.Model):
    """Bunker-specific user data"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bunker_id = db.Column(db.String(50), nullable=False)
    access_level = db.Column(db.String(20), default='basic')
    room_assignment = db.Column(db.String(50))
    emergency_contact = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('bunker_profile', uselist=False))

class EnvironmentalData(db.Model):
    """Environmental monitoring data"""
    id = db.Column(db.Integer, primary_key=True)
    bunker_id = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    oxygen_level = db.Column(db.Float)
    co2_level = db.Column(db.Float)
    radiation_level = db.Column(db.Float)
    air_quality_index = db.Column(db.Integer)
    pressure = db.Column(db.Float)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'bunker_id': self.bunker_id,
            'timestamp': self.timestamp.isoformat(),
            'temperature': self.temperature,
            'humidity': self.humidity,
            'oxygen_level': self.oxygen_level,
            'co2_level': self.co2_level,
            'radiation_level': self.radiation_level,
            'air_quality_index': self.air_quality_index,
            'pressure': self.pressure
        }

class Alert(db.Model):
    """Alert management"""
    id = db.Column(db.Integer, primary_key=True)
    bunker_id = db.Column(db.String(50), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, resolved, acknowledged
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.String(80))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'bunker_id': self.bunker_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by
        }

# ============================================================================
# AUTHENTICATION SERVICE
# ============================================================================

class AuthService:
    """Authentication and authorization service"""
    
    @staticmethod
    def generate_token(user: User) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'is_premium': user.is_premium,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            bunker_logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            bunker_logger.warning("Invalid token")
            return None
    
    @staticmethod
    def require_auth(f):
        """Authentication decorator"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if token and token.startswith('Bearer '):
                token = token[7:]  # Remove 'Bearer ' prefix
                payload = AuthService.verify_token(token)
                if payload:
                    g.current_user = User.query.get(payload['user_id'])
                    return f(*args, **kwargs)
            
            return jsonify({'error': 'Authentication required'}), 401
        return decorated_function
    
    @staticmethod
    def require_premium(f):
        """Premium subscription decorator"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user') or not g.current_user.is_premium:
                return jsonify({
                    'error': 'Premium subscription required',
                    'upgrade_url': f'https://buy.stripe.com/14AeVc0uv3dq7U9fVb2B200'
                }), 403
            return f(*args, **kwargs)
        return decorated_function

# ============================================================================
# ENVIRONMENTAL SERVICE
# ============================================================================

class EnvironmentalService:
    """Environmental monitoring service"""
    
    @staticmethod
    def generate_test_data(bunker_id: str, scenario: str = 'normal') -> bool:
        """Generate test environmental data"""
        try:
            # Define scenario parameters
            scenarios = {
                'normal': {
                    'temp_range': (18, 24),
                    'humidity_range': (40, 60),
                    'oxygen_range': (19, 21),
                    'co2_range': (300, 800),
                    'radiation_range': (0.1, 0.3),
                    'aqi_range': (10, 50)
                },
                'emergency': {
                    'temp_range': (10, 35),
                    'humidity_range': (20, 80),
                    'oxygen_range': (16, 23),
                    'co2_range': (800, 2000),
                    'radiation_range': (0.5, 2.0),
                    'aqi_range': (50, 150)
                },
                'critical': {
                    'temp_range': (5, 40),
                    'humidity_range': (10, 90),
                    'oxygen_range': (14, 25),
                    'co2_range': (1500, 5000),
                    'radiation_range': (2.0, 10.0),
                    'aqi_range': (150, 300)
                }
            }
            
            params = scenarios.get(scenario, scenarios['normal'])
            
            # Generate data
            data = EnvironmentalData(
                bunker_id=bunker_id,
                temperature=random.uniform(*params['temp_range']),
                humidity=random.uniform(*params['humidity_range']),
                oxygen_level=random.uniform(*params['oxygen_range']),
                co2_level=random.uniform(*params['co2_range']),
                radiation_level=random.uniform(*params['radiation_range']),
                air_quality_index=random.randint(*params['aqi_range']),
                pressure=random.uniform(1010, 1030)
            )
            
            db.session.add(data)
            db.session.commit()
            
            # Check for alerts
            AlertService.check_environmental_alerts(data)
            
            bunker_logger.info(f"Test data generated for scenario: {scenario}")
            return True
            
        except Exception as e:
            bunker_logger.error(f"Failed to generate test data: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def get_current_data(bunker_id: str) -> Optional[Dict]:
        """Get current environmental data"""
        try:
            data = EnvironmentalData.query.filter_by(bunker_id=bunker_id)\
                                         .order_by(EnvironmentalData.timestamp.desc())\
                                         .first()
            return data.to_dict() if data else None
        except Exception as e:
            bunker_logger.error(f"Failed to get current data: {str(e)}")
            return None
    
    @staticmethod
    def get_historical_data(bunker_id: str, hours: int = 24) -> List[Dict]:
        """Get historical environmental data"""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            data = EnvironmentalData.query.filter(
                EnvironmentalData.bunker_id == bunker_id,
                EnvironmentalData.timestamp >= since
            ).order_by(EnvironmentalData.timestamp.desc()).all()
            
            return [item.to_dict() for item in data]
        except Exception as e:
            bunker_logger.error(f"Failed to get historical data: {str(e)}")
            return []

# ============================================================================
# ALERT SERVICE
# ============================================================================

class AlertService:
    """Alert management service"""
    
    @staticmethod
    def create_alert(bunker_id: str, alert_type: str, severity: str, 
                    title: str, description: str = None) -> bool:
        """Create a new alert"""
        try:
            alert = Alert(
                bunker_id=bunker_id,
                alert_type=alert_type,
                severity=severity,
                title=title,
                description=description
            )
            
            db.session.add(alert)
            db.session.commit()
            
            bunker_logger.warning(f"Alert created: {title} ({severity})")
            return True
            
        except Exception as e:
            bunker_logger.error(f"Failed to create alert: {str(e)}")
            return False
    
    @staticmethod
    def check_environmental_alerts(data: EnvironmentalData):
        """Check environmental data for alert conditions"""
        alerts_to_create = []
        
        # Temperature alerts
        if data.temperature < 15 or data.temperature > 30:
            severity = 'critical' if data.temperature < 10 or data.temperature > 35 else 'high'
            alerts_to_create.append({
                'type': 'temperature',
                'severity': severity,
                'title': f'Temperature Alert: {data.temperature:.1f}°C',
                'description': f'Temperature is outside safe range in {data.bunker_id}'
            })
        
        # Oxygen alerts
        if data.oxygen_level < 18:
            severity = 'critical' if data.oxygen_level < 16 else 'high'
            alerts_to_create.append({
                'type': 'oxygen',
                'severity': severity,
                'title': f'Low Oxygen: {data.oxygen_level:.1f}%',
                'description': f'Oxygen level is dangerously low in {data.bunker_id}'
            })
        
        # CO2 alerts
        if data.co2_level > 1000:
            severity = 'critical' if data.co2_level > 2000 else 'high'
            alerts_to_create.append({
                'type': 'co2',
                'severity': severity,
                'title': f'High CO2: {data.co2_level:.0f} ppm',
                'description': f'CO2 level is too high in {data.bunker_id}'
            })
        
        # Radiation alerts
        if data.radiation_level > 1.0:
            severity = 'critical' if data.radiation_level > 5.0 else 'high'
            alerts_to_create.append({
                'type': 'radiation',
                'severity': severity,
                'title': f'Radiation Alert: {data.radiation_level:.2f} mSv/h',
                'description': f'Radiation level is elevated in {data.bunker_id}'
            })
        
        # Create alerts
        for alert_data in alerts_to_create:
            AlertService.create_alert(
                data.bunker_id,
                alert_data['type'],
                alert_data['severity'],
                alert_data['title'],
                alert_data['description']
            )
    
    @staticmethod
    def get_active_alerts(bunker_id: str) -> Dict:
        """Get active alerts"""
        try:
            alerts = Alert.query.filter_by(bunker_id=bunker_id, status='active')\
                              .order_by(Alert.created_at.desc()).all()
            
            return {
                'alerts': [alert.to_dict() for alert in alerts],
                'count': len(alerts)
            }
        except Exception as e:
            bunker_logger.error(f"Failed to get active alerts: {str(e)}")
            return {'alerts': [], 'count': 0}
    
    @staticmethod
    def resolve_alert(alert_id: int, resolved_by: str) -> bool:
        """Resolve an alert"""
        try:
            alert = Alert.query.get(alert_id)
            if alert and alert.status == 'active':
                alert.status = 'resolved'
                alert.resolved_at = datetime.utcnow()
                alert.resolved_by = resolved_by
                db.session.commit()
                
                bunker_logger.info(f"Alert {alert_id} resolved by {resolved_by}")
                return True
            return False
        except Exception as e:
            bunker_logger.error(f"Failed to resolve alert: {str(e)}")
            return False

# ============================================================================
# PREMIUM FEATURES SERVICE
# ============================================================================

class PremiumService:
    """Premium features and Stripe integration"""
    
    PREMIUM_TIERS = {
        'free': {
            'name': 'Free',
            'price': 0,
            'features': ['Basic monitoring', 'Standard alerts', 'Community support']
        },
        'tip': {
            'name': 'Taupe Tip+',
            'price': 0.99,
            'features': ['Supporter badge', 'Early access', 'Priority support']
        },
        'pro': {
            'name': 'Taupe Pro+',
            'price': 3.00,
            'features': ['Beta access', 'Priority requests', 'Advanced tools']
        },
        'ultra': {
            'name': 'Taupe Ultra',
            'price': 27.00,
            'features': ['All Pro+ features', 'Secret tools', 'VIP status', 'Personal mention']
        }
    }
    
    @staticmethod
    def get_user_tier_info(user: User) -> Dict:
        """Get user's premium tier information"""
        tier = user.premium_tier if user.is_premium else 'free'
        tier_info = PremiumService.PREMIUM_TIERS.get(tier, PremiumService.PREMIUM_TIERS['free'])
        
        return {
            'current_tier': tier,
            'is_premium': user.is_premium,
            'tier_info': tier_info,
            'upgrade_available': tier != 'ultra'
        }
    
    @staticmethod
    def get_premium_features(user: User) -> List[str]:
        """Get available features for user's tier"""
        if not user.is_premium:
            return PremiumService.PREMIUM_TIERS['free']['features']
        
        tier_info = PremiumService.PREMIUM_TIERS.get(user.premium_tier, PremiumService.PREMIUM_TIERS['free'])
        return tier_info['features']

# ============================================================================
# TESTING FRAMEWORK
# ============================================================================

class IntegratedTestSuite(unittest.TestCase):
    """Comprehensive test suite for the integrated application"""
    
    def setUp(self):
        """Set up test environment"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            self._create_test_data()
    
    def tearDown(self):
        """Clean up test environment"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _create_test_data(self):
        """Create test data"""
        # Create test user
        user = User(username='testuser', email='test@example.com', role='admin')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        
        # Create test environmental data
        env_data = EnvironmentalData(
            bunker_id='test-bunker',
            temperature=22.5,
            humidity=45.0,
            oxygen_level=20.9,
            co2_level=400,
            radiation_level=0.2,
            air_quality_index=25
        )
        db.session.add(env_data)
        db.session.commit()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_authentication(self):
        """Test authentication flow"""
        # Test login
        response = self.app.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
    
    def test_environmental_data(self):
        """Test environmental data endpoints"""
        response = self.app.get('/api/environmental/current?bunker_id=test-bunker')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('temperature', data)
    
    def test_premium_features(self):
        """Test premium features"""
        response = self.app.get('/api/premium/tiers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('tiers', data)

def run_tests():
    """Run the integrated test suite"""
    bunker_logger.info("Running integrated test suite")
    
    with app.app_context():
        suite = unittest.TestLoader().loadTestsFromTestCase(IntegratedTestSuite)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        bunker_logger.info(f"Tests completed: {result.testsRun} run, {len(result.failures)} failures, {len(result.errors)} errors")
        return result.wasSuccessful()

# ============================================================================
# WEB INTERFACE TEMPLATES
# ============================================================================

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- SEO Meta Tags -->
    <title>La Taupe Bunker Premium | Go Underground</title>
    <meta name="description" content="Unlock exclusive features, early updates, and secret tools with La Taupe+ starting at just €0.99/month. Join the underground tech revolution." />
    <meta name="keywords" content="La Taupe, premium, tech, underground, developer tools, mole, subscription, Stripe, supporter, GitHub" />
    <meta name="author" content="Kevin Marville" />
    
    <!-- Open Graph for Facebook / LinkedIn -->
    <meta property="og:title" content="La Taupe Bunker Premium" />
    <meta property="og:description" content="Go full bunker mode with La Taupe+. From €0.99/month, unlock secret features and support indie tech development." />
    <meta property="og:url" content="https://kvnbbg.github.io/lataupe-bunker-tech" />
    <meta property="og:type" content="website" />
    <meta property="og:image" content="https://kvnbbg.github.io/lataupe-bunker-tech/assets/banner.jpg" />
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="La Taupe Bunker Premium" />
    <meta name="twitter:description" content="Join the mole elite. Premium features start at €0.99. Access secret tools and early drops." />
    <meta name="twitter:image" content="https://kvnbbg.github.io/lataupe-bunker-tech/assets/banner.jpg" />
    <meta name="twitter:creator" content="@kvnbbg" />
    
    <!-- Styles -->
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1"></script>
    
    <!-- Stripe -->
    <script async src="https://js.stripe.com/v3/buy-button.js"></script>
    
    <style>
        .bunker-bg { background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); }
        .glow { box-shadow: 0 0 20px rgba(59, 130, 246, 0.5); }
        .pulse-glow { animation: pulse-glow 2s infinite; }
        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.5); }
            50% { box-shadow: 0 0 30px rgba(59, 130, 246, 0.8); }
        }
        .mobile-menu { transform: translateX(-100%); transition: transform 0.3s ease; }
        .mobile-menu.open { transform: translateX(0); }
    </style>
</head>
<body class="bunker-bg text-white min-h-screen">
    <!-- Navigation -->
    <nav class="bg-gray-900 shadow-lg">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center space-x-4">
                    <i class="fas fa-underground text-blue-400 text-2xl"></i>
                    <h1 class="text-xl font-bold">Lataupe Bunker Tech</h1>
                </div>
                
                <!-- Desktop Menu -->
                <div class="hidden md:flex items-center space-x-6">
                    <a href="#dashboard" class="hover:text-blue-400 transition-colors">Dashboard</a>
                    <a href="#environmental" class="hover:text-blue-400 transition-colors">Environmental</a>
                    <a href="#alerts" class="hover:text-blue-400 transition-colors">Alerts</a>
                    <a href="#premium" class="hover:text-blue-400 transition-colors">Premium</a>
                    <button id="loginBtn" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition-colors">Login</button>
                </div>
                
                <!-- Mobile Menu Button -->
                <button id="mobileMenuBtn" class="md:hidden">
                    <i class="fas fa-bars text-xl"></i>
                </button>
            </div>
        </div>
        
        <!-- Mobile Menu -->
        <div id="mobileMenu" class="mobile-menu fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 shadow-lg md:hidden">
            <div class="p-4">
                <button id="closeMobileMenu" class="float-right">
                    <i class="fas fa-times text-xl"></i>
                </button>
                <div class="clear-both pt-8 space-y-4">
                    <a href="#dashboard" class="block hover:text-blue-400 transition-colors">Dashboard</a>
                    <a href="#environmental" class="block hover:text-blue-400 transition-colors">Environmental</a>
                    <a href="#alerts" class="block hover:text-blue-400 transition-colors">Alerts</a>
                    <a href="#premium" class="block hover:text-blue-400 transition-colors">Premium</a>
                </div>
            </div>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <!-- Hero Section -->
        <section class="text-center py-16">
            <h1 class="text-5xl font-bold mb-6 glow">Welcome to the Underground</h1>
            <p class="text-xl mb-8 text-gray-300">Advanced bunker management for the post-ozone world</p>
            <div class="flex justify-center space-x-4">
                <button id="startBtn" class="bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded-lg text-lg font-semibold transition-colors pulse-glow">
                    Enter Bunker
                </button>
                <button id="premiumBtn" class="bg-yellow-600 hover:bg-yellow-700 px-8 py-3 rounded-lg text-lg font-semibold transition-colors">
                    Go Premium
                </button>
            </div>
        </section>
        
        <!-- Dashboard Section -->
        <section id="dashboard" class="mb-16">
            <h2 class="text-3xl font-bold mb-8 text-center">Bunker Dashboard</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <!-- Status Cards -->
                <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-400">Temperature</p>
                            <p id="temperature" class="text-2xl font-bold text-green-400">--°C</p>
                        </div>
                        <i class="fas fa-thermometer-half text-3xl text-green-400"></i>
                    </div>
                </div>
                
                <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-400">Oxygen Level</p>
                            <p id="oxygen" class="text-2xl font-bold text-blue-400">--%</p>
                        </div>
                        <i class="fas fa-wind text-3xl text-blue-400"></i>
                    </div>
                </div>
                
                <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-400">Radiation</p>
                            <p id="radiation" class="text-2xl font-bold text-yellow-400">-- mSv/h</p>
                        </div>
                        <i class="fas fa-radiation text-3xl text-yellow-400"></i>
                    </div>
                </div>
                
                <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-400">Active Alerts</p>
                            <p id="alertCount" class="text-2xl font-bold text-red-400">--</p>
                        </div>
                        <i class="fas fa-exclamation-triangle text-3xl text-red-400"></i>
                    </div>
                </div>
            </div>
            
            <!-- Charts -->
            <div class="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                    <h3 class="text-xl font-bold mb-4">Environmental Trends</h3>
                    <canvas id="environmentalChart"></canvas>
                </div>
                
                <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                    <h3 class="text-xl font-bold mb-4">System Status</h3>
                    <canvas id="statusChart"></canvas>
                </div>
            </div>
        </section>
        
        <!-- Premium Section -->
        <section id="premium" class="mb-16">
            <h2 class="text-3xl font-bold mb-8 text-center">Premium Features</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Free Tier -->
                <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                    <h3 class="text-xl font-bold mb-4">Free</h3>
                    <p class="text-3xl font-bold mb-4">€0<span class="text-sm">/month</span></p>
                    <ul class="space-y-2 mb-6">
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Basic monitoring</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Standard alerts</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Community support</li>
                    </ul>
                    <button class="w-full bg-gray-600 py-2 rounded">Current Plan</button>
                </div>
                
                <!-- Pro Tier -->
                <div class="bg-gray-800 p-6 rounded-lg shadow-lg border-2 border-blue-500">
                    <h3 class="text-xl font-bold mb-4">Taupe Pro+</h3>
                    <p class="text-3xl font-bold mb-4">€3<span class="text-sm">/month</span></p>
                    <ul class="space-y-2 mb-6">
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Beta access</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Priority requests</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Advanced tools</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Premium support</li>
                    </ul>
                    <stripe-buy-button
                        buy-button-id="buy_btn_1Rj3FlAgNXcbbeAvd7p20Qgi"
                        publishable-key="pk_live_51QrrpyAgNXcbbeAvW0sQk7AKth6aNLyiIGLONux6z07z9oRAt0aCvXwq2d5H5jIwSMOgEDieSaGq08Ksvqvq8dB500qVZIIXrF">
                    </stripe-buy-button>
                </div>
                
                <!-- Ultra Tier -->
                <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                    <h3 class="text-xl font-bold mb-4">Taupe Ultra</h3>
                    <p class="text-3xl font-bold mb-4">€27<span class="text-sm">/month</span></p>
                    <ul class="space-y-2 mb-6">
                        <li><i class="fas fa-check text-green-400 mr-2"></i>All Pro+ features</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Secret tools</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>VIP status</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Personal mention</li>
                    </ul>
                    <button class="w-full bg-yellow-600 hover:bg-yellow-700 py-2 rounded transition-colors">Coming Soon</button>
                </div>
            </div>
        </section>
        
        <!-- Support Section -->
        <section class="mb-16">
            <h2 class="text-3xl font-bold mb-8 text-center">Support the Project</h2>
            <div class="text-center space-y-4">
                <p class="text-gray-300">Help maintain and improve Lataupe Bunker Tech</p>
                <div class="flex justify-center space-x-4 flex-wrap">
                    <a href="https://patreon.com/kvnbbg" class="bg-orange-600 hover:bg-orange-700 px-4 py-2 rounded transition-colors">
                        <i class="fab fa-patreon mr-2"></i>Patreon
                    </a>
                    <a href="https://ko-fi.com/kvnbbg" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition-colors">
                        <i class="fas fa-coffee mr-2"></i>Ko-fi
                    </a>
                    <a href="https://coff.ee/kevinmarville" class="bg-yellow-600 hover:bg-yellow-700 px-4 py-2 rounded transition-colors">
                        <i class="fas fa-coffee mr-2"></i>Buy Coffee
                    </a>
                </div>
            </div>
        </section>
        
        <!-- Social Links -->
        <section class="mb-16">
            <h2 class="text-3xl font-bold mb-8 text-center">Connect</h2>
            <div class="text-center space-y-4">
                <div class="flex justify-center space-x-4 flex-wrap">
                    <a href="https://allmylinks.com/kevinmarville" class="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded transition-colors">
                        <i class="fas fa-link mr-2"></i>All Links
                    </a>
                    <a href="https://github.com/Kvnbbg/" class="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded transition-colors">
                        <i class="fab fa-github mr-2"></i>GitHub
                    </a>
                    <a href="https://t.me/kevinmarville" class="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded transition-colors">
                        <i class="fab fa-telegram mr-2"></i>Telegram
                    </a>
                    <a href="https://matrix.to/#/@kvnbbg:matrix.org" class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded transition-colors">
                        <i class="fas fa-comments mr-2"></i>Matrix
                    </a>
                </div>
            </div>
        </section>
    </main>
    
    <!-- Footer -->
    <footer class="bg-gray-900 py-8">
        <div class="container mx-auto px-4 text-center">
            <p class="text-gray-400 mb-4">© 2025 Lataupe Bunker Tech - Underground Survival System</p>
            <p class="text-sm text-gray-500">
                Deploy your own: 
                <a href="https://railway.com/deploy/lzsD1L?referralCode=74Ni9C" class="text-blue-400 hover:text-blue-300">
                    <img src="https://railway.com/button.svg" alt="Deploy on Railway" class="inline h-6">
                </a>
            </p>
        </div>
    </footer>
    
    <!-- JavaScript -->
    <script>
        // Mobile menu functionality
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const mobileMenu = document.getElementById('mobileMenu');
        const closeMobileMenu = document.getElementById('closeMobileMenu');
        
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.add('open');
        });
        
        closeMobileMenu.addEventListener('click', () => {
            mobileMenu.classList.remove('open');
        });
        
        // API functions
        async function fetchData(endpoint) {
            try {
                const response = await fetch(`/api/${endpoint}`);
                return await response.json();
            } catch (error) {
                console.error('API Error:', error);
                return null;
            }
        }
        
        // Update dashboard
        async function updateDashboard() {
            const envData = await fetchData('environmental/current?bunker_id=bunker-01');
            const alerts = await fetchData('alerts/active?bunker_id=bunker-01');
            
            if (envData) {
                document.getElementById('temperature').textContent = `${envData.temperature?.toFixed(1) || '--'}°C`;
                document.getElementById('oxygen').textContent = `${envData.oxygen_level?.toFixed(1) || '--'}%`;
                document.getElementById('radiation').textContent = `${envData.radiation_level?.toFixed(2) || '--'} mSv/h`;
            }
            
            if (alerts) {
                document.getElementById('alertCount').textContent = alerts.count || '0';
            }
        }
        
        // Initialize charts
        function initCharts() {
            // Environmental Chart
            const envCtx = document.getElementById('environmentalChart').getContext('2d');
            new Chart(envCtx, {
                type: 'line',
                data: {
                    labels: ['6h ago', '5h ago', '4h ago', '3h ago', '2h ago', '1h ago', 'Now'],
                    datasets: [{
                        label: 'Temperature',
                        data: [22, 21.5, 22.2, 21.8, 22.1, 21.9, 22.0],
                        borderColor: 'rgb(34, 197, 94)',
                        tension: 0.1
                    }, {
                        label: 'Oxygen',
                        data: [20.9, 20.8, 20.9, 20.7, 20.8, 20.9, 20.8],
                        borderColor: 'rgb(59, 130, 246)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: 'white' }
                        }
                    },
                    scales: {
                        x: { ticks: { color: 'white' } },
                        y: { ticks: { color: 'white' } }
                    }
                }
            });
            
            // Status Chart
            const statusCtx = document.getElementById('statusChart').getContext('2d');
            new Chart(statusCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Operational', 'Warning', 'Critical'],
                    datasets: [{
                        data: [85, 12, 3],
                        backgroundColor: ['rgb(34, 197, 94)', 'rgb(251, 191, 36)', 'rgb(239, 68, 68)']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: 'white' }
                        }
                    }
                }
            });
        }
        
        // Initialize app
        document.addEventListener('DOMContentLoaded', () => {
            updateDashboard();
            initCharts();
            
            // Update dashboard every 30 seconds
            setInterval(updateDashboard, 30000);
        });
        
        // Button handlers
        document.getElementById('startBtn').addEventListener('click', () => {
            document.getElementById('dashboard').scrollIntoView({ behavior: 'smooth' });
        });
        
        document.getElementById('premiumBtn').addEventListener('click', () => {
            document.getElementById('premium').scrollIntoView({ behavior: 'smooth' });
        });
    </script>
</body>
</html>
"""

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main application"""
    bunker_logger.info("Serving main application")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health')
def health_check():
    """Enhanced health check endpoint"""
    try:
        # Check database connectivity
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0',
            'environment': app.config['ENVIRONMENT'],
            'database': 'connected',
            'services': {
                'auth': 'operational',
                'environmental': 'operational',
                'alerts': 'operational',
                'logging': 'operational',
                'premium': 'operational'
            }
        }
        
        bunker_logger.info("Health check completed", health_data)
        return jsonify(health_data)
        
    except Exception as e:
        bunker_logger.error("Health check failed", exc_info=True)
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User authentication"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            token = AuthService.generate_token(user)
            
            bunker_logger.info(f"User logged in: {username}")
            return jsonify({
                'token': token,
                'user': user.to_dict(),
                'premium_info': PremiumService.get_user_tier_info(user)
            })
        else:
            bunker_logger.warning(f"Failed login attempt: {username}")
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        bunker_logger.error("Login error", exc_info=True)
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration with enhanced validation"""
    try:
        # Rate limiting
        client_ip = request.remote_addr
        if not SecurityManager.rate_limit_check(f"register_{client_ip}", max_requests=5, window=300):
            bunker_logger.warning(f"Rate limit exceeded for registration from {client_ip}")
            return jsonify({'error': 'Too many registration attempts. Please try again later.'}), 429
        
        # Validate input
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        schema = RegisterSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            bunker_logger.warning(f"Registration validation failed: {err.messages}")
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Sanitize inputs
        username = SecurityManager.sanitize_input(validated_data['username'])
        email = SecurityManager.sanitize_input(validated_data['email'])
        password = validated_data['password']
        confirm_password = validated_data['confirm_password']
        
        # Additional validation
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        if not SecurityManager.validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        password_validation = SecurityManager.validate_password(password)
        if not password_validation['valid']:
            return jsonify({
                'error': 'Password does not meet requirements',
                'details': password_validation['errors']
            }), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            username=username,
            email=email,
            role='resident',
            is_premium=False,
            premium_tier='free'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = AuthService.generate_token(user)
        
        bunker_logger.info(f"New user registered: {username}")
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        bunker_logger.error("Registration error", exc_info=True)
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/environmental/current')
def get_current_environmental():
    """Get current environmental data"""
    try:
        bunker_id = request.args.get('bunker_id', 'bunker-01')
        data = EnvironmentalService.get_current_data(bunker_id)
        
        if data:
            bunker_logger.info(f"Current environmental data retrieved for {bunker_id}")
            return jsonify(data)
        else:
            # Generate sample data if none exists
            EnvironmentalService.generate_test_data(bunker_id, 'normal')
            data = EnvironmentalService.get_current_data(bunker_id)
            return jsonify(data) if data else jsonify({'error': 'No data available'}), 404
            
    except Exception as e:
        bunker_logger.error("Error getting current environmental data", exc_info=True)
        return jsonify({'error': 'Failed to get environmental data'}), 500

@app.route('/api/environmental/history')
def get_environmental_history():
    """Get historical environmental data"""
    try:
        bunker_id = request.args.get('bunker_id', 'bunker-01')
        hours = int(request.args.get('hours', 24))
        
        data = EnvironmentalService.get_historical_data(bunker_id, hours)
        bunker_logger.info(f"Environmental history retrieved for {bunker_id} ({hours} hours)")
        
        return jsonify({
            'data': data,
            'period_hours': hours,
            'count': len(data)
        })
        
    except Exception as e:
        bunker_logger.error("Error getting environmental history", exc_info=True)
        return jsonify({'error': 'Failed to get environmental history'}), 500

@app.route('/api/alerts/active')
def get_active_alerts():
    """Get active alerts"""
    try:
        bunker_id = request.args.get('bunker_id', 'bunker-01')
        alerts = AlertService.get_active_alerts(bunker_id)
        bunker_logger.info(f"Active alerts retrieved for {bunker_id}: {alerts['count']} alerts")
        return jsonify(alerts)
        
    except Exception as e:
        bunker_logger.error("Error getting active alerts", exc_info=True)
        return jsonify({'error': 'Failed to get alerts'}), 500

@app.route('/api/premium/tiers')
def get_premium_tiers():
    """Get premium tier information"""
    try:
        return jsonify({
            'tiers': PremiumService.PREMIUM_TIERS,
            'stripe_config': {
                'publishable_key': app.config['STRIPE_PUBLISHABLE_KEY'],
                'buy_button_id': app.config['STRIPE_BUY_BUTTON_ID']
            }
        })
    except Exception as e:
        bunker_logger.error("Error getting premium tiers", exc_info=True)
        return jsonify({'error': 'Failed to get premium tiers'}), 500

@app.route('/api/premium/status')
@AuthService.require_auth
def get_premium_status():
    """Get user's premium status"""
    try:
        user = g.current_user
        tier_info = PremiumService.get_user_tier_info(user)
        features = PremiumService.get_premium_features(user)
        
        bunker_logger.info(f"Premium status checked for user: {user.username}")
        return jsonify({
            'tier_info': tier_info,
            'features': features,
            'social_links': app.config['SOCIAL_LINKS'],
            'support_links': {
                'patreon': 'https://patreon.com/kvnbbg',
                'kofi': 'https://ko-fi.com/kvnbbg',
                'coffee': 'https://coff.ee/kevinmarville'
            }
        })
        
    except Exception as e:
        bunker_logger.error("Error getting premium status", exc_info=True)
        return jsonify({'error': 'Failed to get premium status'}), 500

@app.route('/api/test/run')
def run_api_tests():
    """Run integrated tests via API"""
    try:
        success = run_tests()
        return jsonify({
            'test_status': 'passed' if success else 'failed',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        bunker_logger.error("Test execution failed", exc_info=True)
        return jsonify({'error': 'Test execution failed'}), 500

@app.route('/api/translate', methods=['GET'])
def translate_text():
    """Translation service for multi-language support"""
    try {
        lang = request.args.get('lang', 'en');
        
        # Translation dictionaries
        translations = {
            'en': {
                'welcome': 'Welcome to the Underground',
                'dashboard': 'Bunker Dashboard',
                'temperature': 'Temperature',
                'oxygen': 'Oxygen Level',
                'radiation': 'Radiation',
                'alerts': 'Active Alerts',
                'premium': 'Premium Features',
                'login': 'Login',
                'register': 'Register',
                'username': 'Username',
                'password': 'Password',
                'email': 'Email',
                'confirm_password': 'Confirm Password',
                'enter_bunker': 'Enter Bunker',
                'go_premium': 'Go Premium',
                'support_project': 'Support the Project',
                'connect': 'Connect',
                'environmental_trends': 'Environmental Trends',
                'system_status': 'System Status',
                'operational': 'Operational',
                'warning': 'Warning',
                'critical': 'Critical',
                'current_plan': 'Current Plan',
                'upgrade': 'Upgrade',
                'coming_soon': 'Coming Soon',
                'free_tier': 'Free',
                'pro_tier': 'Taupe Pro+',
                'ultra_tier': 'Taupe Ultra'
            },
            'fr': {
                'welcome': 'Bienvenue dans le Souterrain',
                'dashboard': 'Tableau de Bord du Bunker',
                'temperature': 'Température',
                'oxygen': 'Niveau d\'Oxygène',
                'radiation': 'Radiation',
                'alerts': 'Alertes Actives',
                'premium': 'Fonctionnalités Premium',
                'login': 'Connexion',
                'register': 'S\'inscrire',
                'username': 'Nom d\'utilisateur',
                'password': 'Mot de passe',
                'email': 'Email',
                'confirm_password': 'Confirmer le mot de passe',
                'enter_bunker': 'Entrer dans le Bunker',
                'go_premium': 'Passer Premium',
                'support_project': 'Soutenir le Projet',
                'connect': 'Se Connecter',
                'environmental_trends': 'Tendances Environnementales',
                'system_status': 'État du Système',
                'operational': 'Opérationnel',
                'warning': 'Avertissement',
                'critical': 'Critique',
                'current_plan': 'Plan Actuel',
                'upgrade': 'Mettre à niveau',
                'coming_soon': 'Bientôt Disponible',
                'free_tier': 'Gratuit',
                'pro_tier': 'Taupe Pro+',
                'ultra_tier': 'Taupe Ultra'
            }
        };
        
        selected_translations = translations.get(lang, translations['en']);
        
        bunker_logger.info(f"Translation requested for language: {lang}");
        return jsonify({
            'success': True,
            'language': lang,
            'translations': selected_translations
        });
        
    } catch (Exception e) {
        bunker_logger.error("Translation error", exc_info=True);
        return jsonify({'error': 'Translation failed'}), 500;
    }

@app.route('/api/alerts/resolve/<int:alert_id>', methods=['POST'])
@AuthService.require_auth
def resolve_alert(alert_id):
    """Resolve an alert with authentication required"""
    try:
        user = g.current_user
        
        # Validate input
        if not alert_id or alert_id <= 0:
            return jsonify({'error': 'Invalid alert ID'}), 400
        
        success = AlertService.resolve_alert(alert_id, user.username)
        
        if success:
            bunker_logger.info(f"Alert {alert_id} resolved by {user.username}")
            return jsonify({
                'success': True,
                'message': 'Alert resolved successfully'
            })
        else:
            return jsonify({'error': 'Alert not found or already resolved'}), 404
            
    except Exception as e:
        bunker_logger.error("Error resolving alert", exc_info=True)
        return jsonify({'error': 'Failed to resolve alert'}), 500

@app.route('/api/user/profile', methods=['GET'])
@AuthService.require_auth
def get_user_profile():
    """Get user profile with gamification data"""
    try:
        user = g.current_user
        
        # Calculate gamification stats
        gamification_data = {
            'level': min(1 + (user.id * 7) % 20, 50),  # Mock level calculation
            'xp': (user.id * 123) % 1000,
            'next_level_xp': 1000,
            'badges': [
                {'name': 'Bunker Resident', 'earned': True, 'icon': 'fas fa-home'},
                {'name': 'Temperature Monitor', 'earned': True, 'icon': 'fas fa-thermometer-half'},
                {'name': 'Alert Resolver', 'earned': user.id % 3 == 0, 'icon': 'fas fa-bell'},
                {'name': 'Premium Member', 'earned': user.is_premium, 'icon': 'fas fa-crown'}
            ]
        }
        
        bunker_logger.info(f"Profile retrieved for user: {user.username}")
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'gamification': gamification_data,
            'premium_info': PremiumService.get_user_tier_info(user)
        })
        
    except Exception as e:
        bunker_logger.error("Error getting user profile", exc_info=True)
        return jsonify({'error': 'Failed to get profile'}), 500

@app.route('/api/slides/story', methods=['GET'])
def get_story_slides():
    """Get story slides for onboarding"""
    try:
        slides = [
            {
                'id': 1,
                'title': 'The Ozone Crisis',
                'content': 'The ozone layer has been severely damaged. Surface life is no longer safe.',
                'image': '/static/images/ozone_crisis.jpg',
                'audio': '/static/music/background.mp3'
            },
            {
                'id': 2,
                'title': 'Underground Living',
                'content': 'Humanity has moved underground. Bunkers provide safety and survival.',
                'image': '/static/images/underground_bunker_view.webp',
                'audio': '/static/music/success.wav'
            },
            {
                'id': 3,
                'title': 'Technology Failure',
                'content': 'Environmental systems can fail. Constant monitoring is essential.',
                'image': '/static/images/tech_failure.jpg',
                'audio': '/static/music/error.wav'
            },
            {
                'id': 4,
                'title': 'Scorched Earth',
                'content': 'The surface world is hostile. Only the prepared survive.',
                'image': '/static/images/scorched_earth.jpg',
                'audio': '/static/music/victory.wav'
            },
            {
                'id': 5,
                'title': 'Your Mission',
                'content': 'Monitor, survive, and thrive in the underground world.',
                'image': '/static/images/mission.jpg',
                'audio': '/static/music/lauch.wav'
            }
        ]
        
        bunker_logger.info("Story slides retrieved")
        return jsonify({
            'success': True,
            'slides': slides,
            'total_slides': len(slides)
        })
        
    except Exception as e:
        bunker_logger.error("Error getting story slides", exc_info=True)
        return jsonify({'error': 'Failed to get story slides'}), 500

@app.route('/api/logs/security', methods=['GET'])
@AuthService.require_auth
def get_security_logs():
    """Get security logs for admin users"""
    try:
        user = g.current_user
        
        if user.role != 'admin':
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Mock security logs - in production, this would query actual logs
        logs = [
            {
                'timestamp': (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                'level': 'WARNING',
                'event': 'Failed login attempt',
                'ip': '192.168.1.100',
                'user_agent': 'Mozilla/5.0...',
                'details': 'Invalid credentials for user: testuser'
            },
            {
                'timestamp': (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
                'level': 'INFO',
                'event': 'User login',
                'ip': '192.168.1.101',
                'user_agent': 'Mozilla/5.0...',
                'details': 'Successful login for user: admin'
            },
            {
                'timestamp': (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                'level': 'ERROR',
                'event': 'Rate limit exceeded',
                'ip': '192.168.1.102',
                'user_agent': 'Python-requests/2.28.1',
                'details': 'Too many requests from IP'
            }
        ]
        
        bunker_logger.info(f"Security logs accessed by admin: {user.username}")
        return jsonify({
            'success': True,
            'logs': logs,
            'count': len(logs)
        })
        
    except Exception as e:
        bunker_logger.error("Error getting security logs", exc_info=True)
        return jsonify({'error': 'Failed to get security logs'}), 500

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def create_tables():
    """Initialize database with sample data"""
    bunker_logger.info("Initializing database tables")
    
    try:
        db.create_all()
        
        # Add sample users if none exist
        if User.query.count() == 0:
            bunker_logger.info("Creating sample users")
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@bunker.tech',
                role='admin',
                is_premium=True,
                premium_tier='ultra'
            )
            admin.set_password('admin123')
            
            # Create resident user
            resident = User(
                username='resident',
                email='resident@bunker.tech',
                role='resident'
            )
            resident.set_password('resident123')
            
            db.session.add(admin)
            db.session.add(resident)
            db.session.commit()
            
            bunker_logger.info("Sample users created successfully")
            
            # Create bunker profiles
            admin_bunker = BunkerUser(
                user_id=admin.id,
                bunker_id='bunker-01',
                access_level='admin',
                room_assignment='Control Room',
                emergency_contact='Command Center'
            )
            
            resident_bunker = BunkerUser(
                user_id=resident.id,
                bunker_id='bunker-01',
                access_level='basic',
                room_assignment='Living Quarter A-12',
                emergency_contact='+1-555-0123'
            )
            
            db.session.add(admin_bunker)
            db.session.add(resident_bunker)
            
            # Generate initial environmental data
            bunker_logger.info("Generating initial environmental data")
            for i in range(24):
                EnvironmentalService.generate_test_data('bunker-01', 'normal')
            
            db.session.commit()
            bunker_logger.info("Database initialization completed successfully")
            
    except Exception as e:
        bunker_logger.error("Database initialization failed", exc_info=True)
        raise

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    bunker_logger.info("Starting Lataupe Bunker Tech Integrated Application")
    
    with app.app_context():
        create_tables()
    
    # Run tests if requested
    if '--test' in sys.argv:
        bunker_logger.info("Running integrated test suite")
        with app.app_context():
            success = run_tests()
            sys.exit(0 if success else 1)
    
    port = int(os.environ.get('PORT', 5001))
    debug = app.config['ENVIRONMENT'] == 'development'
    
    bunker_logger.info(f"Application starting on port {port} (debug={debug})")
    bunker_logger.info("Features enabled: Microservices, Logging, Testing, Premium, Stripe, Telegram")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

