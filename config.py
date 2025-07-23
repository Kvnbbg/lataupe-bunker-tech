#!/usr/bin/env python3
"""
Configuration de sécurité pour lataupe-bunker-tech
Centralise tous les paramètres de sécurité
"""

import os
from datetime import timedelta

class SecurityConfig:
    """Configuration de sécurité centralisée"""
    
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
            r"\.\.\\",
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
        """Retourne la configuration pour un environnement spécifique"""
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
        """Valide que toutes les variables d'environnement requises sont présentes"""
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
