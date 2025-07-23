#!/usr/bin/env python3
"""
Script d'intégration sécurisée pour lataupe-bunker-tech
Intègre tous les systèmes de sécurité dans l'application principale
"""

import os
import json
from pathlib import Path

def create_secure_main_app():
    """Crée l'application principale sécurisée"""
    
    main_app_code = """#!/usr/bin/env python3
\"\"\"
Application principale sécurisée - Lataupe Bunker Tech
Version avec sécurité de niveau entreprise intégrée
\"\"\"

import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Imports des modules de sécurité
from src.security.middleware import SecurityMiddleware, ThreatDetection
from src.security.sanitization import InputSanitizer, SecurityHeaders, VALIDATION_SCHEMAS
from src.security.encryption import EncryptionManager, SecureStorage, DataMasking
from src.utils.security import SecurityValidator, RateLimiter, SessionManager
from src.utils.email import EmailService

# Imports des modèles et routes
from src.models.advanced_models import db, User, BunkerUser, EnvironmentalData, Alert, AuditLog
from src.routes.registration import registration_bp
from src.routes.quiz import quiz_bp
from src.routes.api import api_bp

# Configuration de logging sécurisé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/security.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SecureBunkerApp:
    \"\"\"Application bunker sécurisée\"\"\"
    
    def __init__(self):
        self.app = None
        self.db = None
        self.security_middleware = None
        self.encryption_manager = None
        self.secure_storage = None
        self.input_sanitizer = None
        
    def create_app(self, config_name='production'):
        \"\"\"Crée et configure l'application Flask sécurisée\"\"\"
        self.app = Flask(__name__)
        
        # Configuration sécurisée
        self._configure_app(config_name)
        
        # Initialiser les composants de sécurité
        self._initialize_security()
        
        # Configurer la base de données
        self._configure_database()
        
        # Enregistrer les blueprints
        self._register_blueprints()
        
        # Configurer les routes principales
        self._configure_routes()
        
        # Configurer les gestionnaires d'erreurs
        self._configure_error_handlers()
        
        # Tâches de maintenance
        self._configure_maintenance_tasks()
        
        logger.info("Secure Bunker App initialized successfully")
        return self.app
    
    def _configure_app(self, config_name):
        \"\"\"Configure l'application avec des paramètres sécurisés\"\"\"
        # Configuration de base sécurisée
        self.app.config.update({
            'SECRET_KEY': os.environ.get('SECRET_KEY') or os.urandom(32),
            'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL') or 'postgresql://localhost/lataupe_bunker',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'pool_timeout': 20,
                'max_overflow': 0
            },
            'WTF_CSRF_ENABLED': True,
            'WTF_CSRF_TIME_LIMIT': 3600,
            'SESSION_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
            'PERMANENT_SESSION_LIFETIME': timedelta(hours=24),
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max
            'UPLOAD_FOLDER': 'uploads',
            'ALLOWED_EXTENSIONS': {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'},
            'RATELIMIT_STORAGE_URL': 'memory://',
            'MAIL_SERVER': os.environ.get('SMTP_SERVER', 'localhost'),
            'MAIL_PORT': int(os.environ.get('SMTP_PORT', '587')),
            'MAIL_USE_TLS': True,
            'MAIL_USERNAME': os.environ.get('SMTP_USERNAME'),
            'MAIL_PASSWORD': os.environ.get('SMTP_PASSWORD'),
            'MASTER_KEY': os.environ.get('MASTER_KEY') or 'default_dev_key_change_in_production'
        })
        
        # Configuration spécifique à l'environnement
        if config_name == 'development':
            self.app.config.update({
                'DEBUG': True,
                'SESSION_COOKIE_SECURE': False,
                'SQLALCHEMY_ECHO': True
            })
        elif config_name == 'production':
            self.app.config.update({
                'DEBUG': False,
                'TESTING': False,
                'SESSION_COOKIE_SECURE': True,
                'PREFERRED_URL_SCHEME': 'https'
            })
        
        # Middleware pour les proxies
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    def _initialize_security(self):
        \"\"\"Initialise tous les composants de sécurité\"\"\"
        # Middleware de sécurité
        self.security_middleware = SecurityMiddleware(self.app)
        
        # Gestionnaire de chiffrement
        self.encryption_manager = EncryptionManager(self.app.config['MASTER_KEY'])
        
        # Stockage sécurisé
        self.secure_storage = SecureStorage(self.encryption_manager)
        
        # Sanitizer d'entrées
        self.input_sanitizer = InputSanitizer()
        
        # CORS sécurisé
        CORS(self.app, 
             origins=['http://localhost:3000', 'https://bunker.tech'],
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
        
        logger.info("Security components initialized")
    
    def _configure_database(self):
        \"\"\"Configure la base de données avec sécurité\"\"\"
        db.init_app(self.app)
        migrate = Migrate(self.app, db)
        
        # Créer les tables si nécessaire
        with self.app.app_context():
            try:
                db.create_all()
                logger.info("Database tables created/verified")
            except Exception as e:
                logger.error(f"Database initialization error: {e}")
    
    def _register_blueprints(self):
        \"\"\"Enregistre tous les blueprints\"\"\"
        self.app.register_blueprint(registration_bp)
        self.app.register_blueprint(quiz_bp)
        self.app.register_blueprint(api_bp)
        
        logger.info("Blueprints registered")
    
    def _configure_routes(self):
        \"\"\"Configure les routes principales\"\"\"
        
        @self.app.route('/')
        def index():
            \"\"\"Page d'accueil\"\"\"
            return render_template('index.html')
        
        @self.app.route('/dashboard')
        def dashboard():
            \"\"\"Dashboard principal\"\"\"
            if 'user_id' not in session:
                return redirect(url_for('registration.login'))
            
            user = User.query.get(session['user_id'])
            if not user:
                session.clear()
                return redirect(url_for('registration.login'))
            
            # Données du dashboard
            bunker_profile = user.bunker_profile
            recent_alerts = Alert.query.filter_by(
                bunker_id=bunker_profile.bunker_id
            ).order_by(Alert.created_at.desc()).limit(5).all()
            
            environmental_data = EnvironmentalData.query.filter_by(
                bunker_id=bunker_profile.bunker_id
            ).order_by(EnvironmentalData.timestamp.desc()).first()
            
            return render_template('dashboard.html',
                                 user=user,
                                 bunker_profile=bunker_profile,
                                 recent_alerts=recent_alerts,
                                 environmental_data=environmental_data)
        
        @self.app.route('/health')
        def health_check():
            \"\"\"Endpoint de vérification de santé\"\"\"
            try:
                # Vérifier la base de données
                db.session.execute('SELECT 1')
                
                # Vérifier les composants critiques
                health_status = {
                    'status': 'healthy',
                    'timestamp': datetime.utcnow().isoformat(),
                    'database': 'connected',
                    'security': 'active',
                    'version': '2.0.0'
                }
                
                return jsonify(health_status), 200
                
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return jsonify({
                    'status': 'unhealthy',
                    'error': 'Database connection failed'
                }), 503
        
        @self.app.route('/security-status')
        def security_status():
            \"\"\"Endpoint de statut de sécurité (admin seulement)\"\"\"
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            user = User.query.get(session['user_id'])
            if not user or user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            # Statistiques de sécurité
            security_stats = {
                'blocked_ips': len(self.security_middleware.blocked_ips),
                'suspicious_activities': len(self.security_middleware.suspicious_activities),
                'active_sessions': len([s for s in self.security_middleware.rate_limits.keys()]),
                'last_threat_detection': datetime.utcnow().isoformat()
            }
            
            return jsonify(security_stats)
    
    def _configure_error_handlers(self):
        \"\"\"Configure les gestionnaires d'erreurs sécurisés\"\"\"
        
        @self.app.errorhandler(400)
        def bad_request(error):
            logger.warning(f"Bad request from {request.remote_addr}: {error}")
            return jsonify({'error': 'Bad request'}), 400
        
        @self.app.errorhandler(401)
        def unauthorized(error):
            logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
            return jsonify({'error': 'Authentication required'}), 401
        
        @self.app.errorhandler(403)
        def forbidden(error):
            logger.warning(f"Forbidden access attempt from {request.remote_addr}")
            return jsonify({'error': 'Access forbidden'}), 403
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Resource not found'}), 404
        
        @self.app.errorhandler(429)
        def rate_limit_exceeded(error):
            logger.warning(f"Rate limit exceeded from {request.remote_addr}")
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {error}")
            db.session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.errorhandler(Exception)
        def handle_exception(e):
            logger.error(f"Unhandled exception: {e}", exc_info=True)
            return jsonify({'error': 'An unexpected error occurred'}), 500
    
    def _configure_maintenance_tasks(self):
        \"\"\"Configure les tâches de maintenance\"\"\"
        
        @self.app.before_first_request
        def initialize_app():
            \"\"\"Initialisation lors du premier démarrage\"\"\"
            logger.info("Application starting up...")
            
            # Nettoyer les sessions expirées
            SessionManager.cleanup_expired_sessions()
            
            # Nettoyer les données temporaires
            self.secure_storage.cleanup_expired_data()
            
            logger.info("Maintenance tasks completed")
        
        # En production, utiliser Celery ou un scheduler pour ces tâches
        def cleanup_task():
            \"\"\"Tâche de nettoyage périodique\"\"\"
            with self.app.app_context():
                # Nettoyer les sessions expirées
                expired_count = SessionManager.cleanup_expired_sessions()
                logger.info(f"Cleaned up {expired_count} expired sessions")
                
                # Nettoyer les données temporaires
                temp_count = self.secure_storage.cleanup_expired_data()
                logger.info(f"Cleaned up {temp_count} temporary data items")
                
                # Nettoyer les logs d'audit anciens (> 90 jours)
                old_logs = AuditLog.query.filter(
                    AuditLog.timestamp < datetime.utcnow() - timedelta(days=90)
                ).delete()
                
                if old_logs > 0:
                    db.session.commit()
                    logger.info(f"Cleaned up {old_logs} old audit logs")

def create_app(config_name='production'):
    \"\"\"Factory function pour créer l'application\"\"\"
    secure_app = SecureBunkerApp()
    return secure_app.create_app(config_name)

# Point d'entrée principal
if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs('logs', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    # Déterminer l'environnement
    config_name = os.environ.get('FLASK_ENV', 'production')
    
    # Créer l'application
    app = create_app(config_name)
    
    # Démarrer l'application
    if config_name == 'development':
        app.run(host='0.0.0.0', port=5001, debug=True)
    else:
        # En production, utiliser Gunicorn
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
"""
    
    return main_app_code

def create_security_config():
    """Crée la configuration de sécurité"""
    
    config_code = """#!/usr/bin/env python3
\"\"\"
Configuration de sécurité pour lataupe-bunker-tech
Centralise tous les paramètres de sécurité
\"\"\"

import os
from datetime import timedelta

class SecurityConfig:
    \"\"\"Configuration de sécurité centralisée\"\"\"
    
    # Clés et secrets
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    MASTER_KEY = os.environ.get('MASTER_KEY') or 'change_this_in_production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    
    # Configuration des sessions
    SESSION_CONFIG = {
        'PERMANENT_SESSION_LIFETIME': timedelta(hours=24),
        'SESSION_COOKIE_SECURE': True,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'SESSION_REFRESH_EACH_REQUEST': True
    }
    
    # Configuration CSRF
    CSRF_CONFIG = {
        'WTF_CSRF_ENABLED': True,
        'WTF_CSRF_TIME_LIMIT': 3600,
        'WTF_CSRF_SSL_STRICT': True
    }
    
    # Limites de sécurité
    SECURITY_LIMITS = {
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
        'MAX_LOGIN_ATTEMPTS': 5,
        'ACCOUNT_LOCKOUT_DURATION': 30,  # minutes
        'PASSWORD_MIN_LENGTH': 8,
        'SESSION_TIMEOUT': 24 * 60 * 60,  # 24 heures en secondes
        'RATE_LIMIT_PER_MINUTE': 100,
        'RATE_LIMIT_PER_HOUR': 1000
    }
    
    # En-têtes de sécurité
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
    }
    
    # Content Security Policy
    CSP_DIRECTIVES = {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
        'style-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
        'img-src': ["'self'", "data:", "https:"],
        'font-src': ["'self'", "https://fonts.gstatic.com"],
        'connect-src': ["'self'"],
        'media-src': ["'self'"],
        'object-src': ["'none'"],
        'child-src': ["'none'"],
        'frame-ancestors': ["'none'"],
        'form-action': ["'self'"],
        'base-uri': ["'self'"],
        'manifest-src': ["'self'"]
    }
    
    # Configuration CORS
    CORS_CONFIG = {
        'origins': [
            'http://localhost:3000',
            'https://bunker.tech',
            'https://*.bunker.tech'
        ],
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'allow_headers': [
            'Content-Type',
            'Authorization',
            'X-Requested-With',
            'X-CSRF-Token'
        ],
        'supports_credentials': True,
        'max_age': 86400
    }
    
    # Patterns de détection de menaces
    THREAT_PATTERNS = {
        'sql_injection': [
            r"union\s+select",
            r"drop\s+table",
            r"insert\s+into",
            r"delete\s+from",
            r"update\s+set",
            r"create\s+table",
            r"alter\s+table",
            r"exec\s*\(",
            r"sp_executesql",
            r"xp_cmdshell"
        ],
        'xss': [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"expression\s*\(",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<form[^>]*>",
            r"<input[^>]*>"
        ],
        'command_injection': [
            r";\s*(ls|cat|pwd|whoami|id|uname)",
            r"\|\s*(ls|cat|pwd|whoami|id|uname)",
            r"&&\s*(ls|cat|pwd|whoami|id|uname)",
            r"`.*`",
            r"\$\(.*\)",
            r"eval\s*\(",
            r"exec\s*\(",
            r"system\s*\(",
            r"shell_exec\s*\(",
            r"passthru\s*\("
        ],
        'path_traversal': [
            r"\.\./",
            r"\.\.\\\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"..%2f",
            r"..%5c"
        ]
    }
    
    # Configuration de logging sécurisé
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'security': {
                'format': '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'formatter': 'detailed'
            },
            'security_file': {
                'level': 'WARNING',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/security.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 10,
                'formatter': 'security'
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'detailed'
            }
        },
        'loggers': {
            '': {
                'handlers': ['file', 'console'],
                'level': 'INFO',
                'propagate': False
            },
            'security': {
                'handlers': ['security_file', 'console'],
                'level': 'WARNING',
                'propagate': False
            }
        }
    }
    
    # Configuration de base de données sécurisée
    DATABASE_CONFIG = {
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 20,
            'max_overflow': 0,
            'echo': False  # Désactiver en production pour éviter les logs de requêtes
        },
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
    
    # Configuration email sécurisée
    EMAIL_CONFIG = {
        'MAIL_SERVER': os.environ.get('SMTP_SERVER', 'localhost'),
        'MAIL_PORT': int(os.environ.get('SMTP_PORT', '587')),
        'MAIL_USE_TLS': True,
        'MAIL_USE_SSL': False,
        'MAIL_USERNAME': os.environ.get('SMTP_USERNAME'),
        'MAIL_PASSWORD': os.environ.get('SMTP_PASSWORD'),
        'MAIL_DEFAULT_SENDER': os.environ.get('FROM_EMAIL', 'noreply@bunker.tech'),
        'MAIL_MAX_EMAILS': 100,
        'MAIL_SUPPRESS_SEND': False
    }
    
    # Extensions de fichiers autorisées
    ALLOWED_EXTENSIONS = {
        'images': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
        'documents': {'pdf', 'txt', 'doc', 'docx'},
        'data': {'json', 'csv', 'xlsx'},
        'all': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'txt', 'doc', 'docx', 'json', 'csv', 'xlsx'}
    }
    
    # Configuration de chiffrement
    ENCRYPTION_CONFIG = {
        'ALGORITHM': 'AES-256-GCM',
        'KEY_DERIVATION': 'PBKDF2',
        'ITERATIONS': 100000,
        'SALT_LENGTH': 32,
        'IV_LENGTH': 16
    }
    
    @classmethod
    def get_config_for_environment(cls, environment='production'):
        \"\"\"Retourne la configuration pour un environnement spécifique\"\"\"
        base_config = {
            'SECRET_KEY': cls.SECRET_KEY,
            'MASTER_KEY': cls.MASTER_KEY,
            **cls.SESSION_CONFIG,
            **cls.CSRF_CONFIG,
            **cls.DATABASE_CONFIG,
            **cls.EMAIL_CONFIG
        }
        
        if environment == 'development':
            base_config.update({
                'DEBUG': True,
                'SESSION_COOKIE_SECURE': False,
                'SQLALCHEMY_ECHO': True,
                'MAIL_SUPPRESS_SEND': True
            })
        elif environment == 'testing':
            base_config.update({
                'TESTING': True,
                'WTF_CSRF_ENABLED': False,
                'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
                'MAIL_SUPPRESS_SEND': True
            })
        else:  # production
            base_config.update({
                'DEBUG': False,
                'TESTING': False,
                'SESSION_COOKIE_SECURE': True,
                'PREFERRED_URL_SCHEME': 'https'
            })
        
        return base_config
    
    @classmethod
    def validate_environment_variables(cls):
        \"\"\"Valide que toutes les variables d'environnement requises sont présentes\"\"\"
        required_vars = [
            'SECRET_KEY',
            'DATABASE_URL',
            'MASTER_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
"""
    
    return config_code

def main():
    """Fonction principale pour créer l'intégration sécurisée"""
    project_path = "/home/ubuntu/lataupe-bunker-tech"
    
    print("🔐 Création de l'intégration sécurisée principale...")
    print("=" * 60)
    
    # Créer le nouveau main.py sécurisé
    main_file = os.path.join(project_path, 'main_secure.py')
    with open(main_file, 'w') as f:
        f.write(create_secure_main_app())
    
    # Créer la configuration de sécurité
    config_file = os.path.join(project_path, 'src', 'security', 'config.py')
    with open(config_file, 'w') as f:
        f.write(create_security_config())
    
    # Créer le fichier requirements.txt mis à jour
    requirements_content = """# Core Flask dependencies
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-WTF==1.1.1
Flask-CORS==4.0.0
WTForms==3.0.1

# Database
psycopg2-binary==2.9.10
SQLAlchemy==2.0.21

# Security
cryptography==45.0.5
bleach==6.2.0
markupsafe==3.0.2
bcrypt==4.0.1

# Email
Flask-Mail==0.9.1

# Utilities
python-dotenv==1.0.0
requests==2.31.0
Werkzeug==2.3.7

# Production
gunicorn==21.2.0
"""
    
    requirements_file = os.path.join(project_path, 'requirements_secure.txt')
    with open(requirements_file, 'w') as f:
        f.write(requirements_content)
    
    # Créer un script de démarrage sécurisé
    startup_script = """#!/bin/bash
# Script de démarrage sécurisé pour lataupe-bunker-tech

echo "🚀 Démarrage de Lataupe Bunker Tech (Mode Sécurisé)"
echo "=================================================="

# Vérifier les variables d'environnement
if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  Génération d'une clé secrète temporaire..."
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi

if [ -z "$MASTER_KEY" ]; then
    echo "⚠️  Génération d'une clé maître temporaire..."
    export MASTER_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi

# Créer les dossiers nécessaires
mkdir -p logs uploads static/uploads

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip3 install -r requirements_secure.txt

# Initialiser la base de données
echo "🗄️  Initialisation de la base de données..."
python3 -c "
from main_secure import create_app
from src.models.advanced_models import db
app = create_app('development')
with app.app_context():
    db.create_all()
    print('Base de données initialisée')
"

# Démarrer l'application
echo "🔒 Démarrage de l'application sécurisée..."
export FLASK_ENV=development
python3 main_secure.py
"""
    
    startup_file = os.path.join(project_path, 'start_secure.sh')
    with open(startup_file, 'w') as f:
        f.write(startup_script)
    
    # Rendre le script exécutable
    os.chmod(startup_file, 0o755)
    
    print("\\n✅ Intégration sécurisée créée avec succès!")
    print("\\n📋 Fichiers créés:")
    print(f"   • Application principale sécurisée: {main_file}")
    print(f"   • Configuration de sécurité: {config_file}")
    print(f"   • Dépendances sécurisées: {requirements_file}")
    print(f"   • Script de démarrage: {startup_file}")
    
    print("\\n🔒 Fonctionnalités intégrées:")
    print("   • Middleware de sécurité complet")
    print("   • Sanitization automatique des entrées")
    print("   • Chiffrement des données sensibles")
    print("   • Détection de menaces en temps réel")
    print("   • Audit logging complet")
    print("   • Gestion sécurisée des sessions")
    print("   • Protection CSRF et XSS")
    print("   • Rate limiting et IP blocking")
    
    print("\\n🚀 Pour démarrer l'application:")
    print(f"   cd {project_path}")
    print("   ./start_secure.sh")
    
    print("\\n⚠️  Variables d'environnement recommandées:")
    print("   export SECRET_KEY='your-secret-key'")
    print("   export MASTER_KEY='your-master-key'")
    print("   export DATABASE_URL='postgresql://user:pass@host/db'")
    print("   export SMTP_SERVER='smtp.gmail.com'")
    print("   export SMTP_USERNAME='your-email@gmail.com'")
    print("   export SMTP_PASSWORD='your-app-password'")
    
    return True

if __name__ == "__main__":
    main()

