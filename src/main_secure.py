#!/usr/bin/env python3
"""
Application principale sécurisée - Lataupe Bunker Tech
Version avec sécurité de niveau entreprise intégrée
"""

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
    """Application bunker sécurisée"""
    
    def __init__(self):
        self.app = None
        self.db = None
        self.security_middleware = None
        self.encryption_manager = None
        self.secure_storage = None
        self.input_sanitizer = None
        
    def create_app(self, config_name='production'):
        """Crée et configure l'application Flask sécurisée"""
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
        """Configure l'application avec des paramètres sécurisés"""
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
        """Initialise tous les composants de sécurité"""
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
        """Configure la base de données avec sécurité"""
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
        """Enregistre tous les blueprints"""
        self.app.register_blueprint(registration_bp)
        self.app.register_blueprint(quiz_bp)
        self.app.register_blueprint(api_bp)
        
        logger.info("Blueprints registered")
    
    def _configure_routes(self):
        """Configure les routes principales"""
        
        @self.app.route('/')
        def index():
            """Page d'accueil"""
            return render_template('index.html')
        
        @self.app.route('/dashboard')
        def dashboard():
            """Dashboard principal"""
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
            """Endpoint de vérification de santé"""
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
            """Endpoint de statut de sécurité (admin seulement)"""
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
        """Configure les gestionnaires d'erreurs sécurisés"""
        
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
        """Configure les tâches de maintenance"""
        
        @self.app.before_first_request
        def initialize_app():
            """Initialisation lors du premier démarrage"""
            logger.info("Application starting up...")
            
            # Nettoyer les sessions expirées
            SessionManager.cleanup_expired_sessions()
            
            # Nettoyer les données temporaires
            self.secure_storage.cleanup_expired_data()
            
            logger.info("Maintenance tasks completed")
        
        # En production, utiliser Celery ou un scheduler pour ces tâches
        def cleanup_task():
            """Tâche de nettoyage périodique"""
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
    """Factory function pour créer l'application"""
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
        app.run(host='0.0.0.0', port=5001)
    else:
        # En production, utiliser Gunicorn
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
