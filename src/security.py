import hashlib
import secrets
import re
import time
from datetime import datetime, timedelta
from flask import request, session
from functools import wraps
import ipaddress

class SecurityValidator:
    """Validateur de sécurité pour l'enregistrement"""
    
    def __init__(self):
        self.suspicious_ips = set()
        self.failed_attempts = {}
    
    def is_suspicious_ip(self, ip_address):
        """Vérifie si une IP est suspecte"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Bloquer les IP privées en production (sauf pour les tests)
            if ip.is_private and not self._is_development():
                return False
            
            # Vérifier la liste noire
            if ip_address in self.suspicious_ips:
                return True
            
            # Vérifier les tentatives échouées récentes
            if ip_address in self.failed_attempts:
                attempts = self.failed_attempts[ip_address]
                recent_attempts = [t for t in attempts if time.time() - t < 3600]  # 1 heure
                if len(recent_attempts) > 10:
                    return True
            
            return False
            
        except ValueError:
            return True  # IP invalide = suspecte
    
    def record_failed_attempt(self, ip_address):
        """Enregistre une tentative échouée"""
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = []
        
        self.failed_attempts[ip_address].append(time.time())
        
        # Nettoyer les anciennes tentatives
        self.failed_attempts[ip_address] = [
            t for t in self.failed_attempts[ip_address] 
            if time.time() - t < 3600
        ]
    
    def _is_development(self):
        """Vérifie si on est en mode développement"""
        import os
        return os.environ.get('FLASK_ENV') == 'development'
    
    @staticmethod
    def validate_password_strength(password):
        """Valide la force d'un mot de passe"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        # Vérifier les mots de passe communs
        common_passwords = [
            'password', '12345678', 'qwerty123', 'bunker123',
            'admin123', 'password123', 'letmein', 'welcome'
        ]
        
        if password.lower() in common_passwords:
            return False, "Password is too common"
        
        return True, "Password is strong"
    
    @staticmethod
    def generate_secure_token(length=32):
        """Génère un token sécurisé"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_sensitive_data(data):
        """Hash des données sensibles pour les logs"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

class RateLimiter:
    """Limiteur de taux pour les requêtes"""
    
    _requests = {}
    
    @classmethod
    def limit(cls, rate_string):
        """Décorateur pour limiter le taux de requêtes"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Parser le taux (ex: "5 per minute")
                parts = rate_string.split()
                limit = int(parts[0])
                period = parts[2]  # minute, hour, etc.
                
                # Calculer la fenêtre de temps
                if period == 'minute':
                    window = 60
                elif period == 'hour':
                    window = 3600
                else:
                    window = 60  # défaut: minute
                
                # Identifier le client
                client_id = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
                key = f"{f.__name__}:{client_id}"
                
                now = time.time()
                
                # Nettoyer les anciennes requêtes
                if key in cls._requests:
                    cls._requests[key] = [
                        req_time for req_time in cls._requests[key]
                        if now - req_time < window
                    ]
                else:
                    cls._requests[key] = []
                
                # Vérifier la limite
                if len(cls._requests[key]) >= limit:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': f'Maximum {limit} requests per {period}'
                    }), 429
                
                # Enregistrer cette requête
                cls._requests[key].append(now)
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator

class SessionManager:
    """Gestionnaire de sessions sécurisé"""
    
    @staticmethod
    def create_secure_session(user_id, remember_me=False):
        """Crée une session sécurisée"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(
            days=30 if remember_me else 1
        )
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expires_at.isoformat(),
            'ip_address': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            'user_agent': request.headers.get('User-Agent')
        }
        
        return session_data
    
    @staticmethod
    def validate_session(session_id, user_id):
        """Valide une session"""
        from src.models.advanced_models import UserSession
        
        user_session = UserSession.query.filter_by(
            session_id=session_id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if not user_session:
            return False
        
        if user_session.is_expired():
            user_session.is_active = False
            return False
        
        # Mettre à jour l'activité
        user_session.last_activity = datetime.utcnow()
        
        return True
    
    @staticmethod
    def cleanup_expired_sessions():
        """Nettoie les sessions expirées"""
        from src.models.advanced_models import UserSession, db
        
        expired_sessions = UserSession.query.filter(
            UserSession.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            session.is_active = False
        
        db.session.commit()
        return len(expired_sessions)

def require_auth(f):
    """Décorateur pour exiger une authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_id = session['user_id']
        session_id = session.get('session_id')
        
        if not SessionManager.validate_session(session_id, user_id):
            session.clear()
            return jsonify({'error': 'Session expired'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(required_role):
    """Décorateur pour exiger un rôle spécifique"""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user_role = session.get('role')
            
            if user_role != required_role and user_role != 'admin':
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
