#!/usr/bin/env python3
"""
Application principale pour déploiement Railway
Version optimisée pour la production sur Railway
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Configuration de base
class Config:
    # Configuration Railway
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///bunker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # Configuration Redis (optionnel sur Railway)
    REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_TYPE = 'redis' if REDIS_URL else 'simple'
    CACHE_REDIS_URL = REDIS_URL
    
    # Configuration email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuration Sentry (monitoring)
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    # Configuration de sécurité
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuration Railway spécifique
    PORT = int(os.environ.get('PORT', 8080))
    HOST = '0.0.0.0'

def create_app():
    """Factory pour créer l'application Flask"""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialiser Sentry pour le monitoring
    if app.config['SENTRY_DSN']:
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration()
            ],
            traces_sample_rate=0.1,
            environment=os.environ.get('FLASK_ENV', 'production')
        )
    
    # Configuration des logs
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    
    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cache.init_app(app)
    
    # Configuration CORS pour Railway
    CORS(app, origins=['*'], supports_credentials=True)
    
    # Rate limiting
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Routes principales
    @app.route('/')
    def index():
        """Page d'accueil"""
        return render_template('dashboard_mobile.html')
    
    @app.route('/health')
    def health():
        """Endpoint de santé pour Railway"""
        try:
            # Vérifier la base de données
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except Exception as e:
            logging.error(f"Database health check failed: {e}")
            db_status = 'unhealthy'
        # Vérifier le cache
        try:
            cache.set('health_check', 'ok', timeout=10)
            cache_status = 'healthy' if cache.get('health_check') == 'ok' else 'unhealthy'
        except Exception as e:
            logging.error(f"Cache health check failed: {e}")
            cache_status = 'unhealthy'
        status = {
            'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0',
            'environment': os.environ.get('FLASK_ENV', 'production'),
            'database': db_status,
            'cache': cache_status,
            'port': app.config['PORT']
        }
        
        return jsonify(status), 200 if status['status'] == 'healthy' else 503
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard principal"""
        return render_template('dashboard_mobile.html')
    
    @app.route('/quiz')
    def quiz():
        """Page quiz"""
        return render_template('quiz_dashboard.html')
    
    @app.route('/api/metrics')
    @limiter.limit("30 per minute")
    def api_metrics():
        """API pour les métriques du bunker"""
        metrics = {
            'oxygen_level': 98,
            'temperature': 21,
            'humidity': 45,
            'energy_level': 87,
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify(metrics)
    
    @app.route('/api/alerts')
    @limiter.limit("20 per minute")
    def api_alerts():
        """API pour les alertes"""
        alerts = [
            {
                'id': 1,
                'type': 'success',
                'message': 'Système de ventilation fonctionnel',
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'id': 2,
                'type': 'warning',
                'message': 'Niveau d\'eau à 75%',
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        return jsonify(alerts)
    
    # Gestionnaires d'erreurs
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': str(e.description)
        }), 429
    
    # Middleware pour les logs de requêtes
    @app.before_request
    def log_request_info():
        if not app.debug:
            app.logger.info(f'{request.method} {request.url} - {request.remote_addr}')
    
    @app.after_request
    def log_response_info(response):
        if not app.debug:
            app.logger.info(f'Response: {response.status_code}')
        return response
    
    return app

# Initialiser les extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cache = Cache()

# Configuration du login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    # Ici, vous chargeriez l'utilisateur depuis la base de données
    return None

# Créer l'application
app = create_app()

# Modèles de base de données (simplifiés pour Railway)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class BunkerMetric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    unit = db.Column(db.String(20))

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Démarrage de l'application sur le port {port}")
    print(f"🌍 Environnement: {os.environ.get('FLASK_ENV', 'production')}")
    print(f"🔧 Debug: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
