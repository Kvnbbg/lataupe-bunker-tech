#!/usr/bin/env python3
"""
Système avancé de sécurisation et sanitization pour lataupe-bunker-tech
Implémente des mesures de sécurité de niveau entreprise et sanitization complète
"""

import os
import json
import re
import html
import bleach
from pathlib import Path

def create_input_sanitization_system():
    """Crée le système de sanitization des entrées"""
    
    sanitization_code = """import re
import html
import bleach
import urllib.parse
from markupsafe import Markup, escape
from flask import request, jsonify
from functools import wraps
import logging

class InputSanitizer:
    \"\"\"Système de sanitization des entrées utilisateur\"\"\"
    
    # Configuration des tags HTML autorisés
    ALLOWED_TAGS = {
        'basic': [],  # Aucun tag HTML autorisé
        'text': ['b', 'i', 'u', 'em', 'strong'],  # Tags de formatage basique
        'rich': ['b', 'i', 'u', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li']  # Tags riches
    }
    
    ALLOWED_ATTRIBUTES = {
        '*': ['class'],
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'width', 'height']
    }
    
    # Patterns de validation
    PATTERNS = {
        'username': r'^[a-zA-Z0-9_-]{3,80}$',
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'bunker_id': r'^bunker-[0-9]{2}$',
        'room_assignment': r'^[a-zA-Z0-9\s\-]{1,100}$',
        'sensor_id': r'^[a-zA-Z0-9_-]{1,50}$',
        'numeric': r'^-?[0-9]+(\.[0-9]+)?$',
        'alphanumeric': r'^[a-zA-Z0-9\s]{1,200}$',
        'safe_text': r'^[a-zA-Z0-9\s\.\,\!\?\-\(\)]{1,1000}$'
    }
    
    # Mots interdits et patterns suspects
    FORBIDDEN_WORDS = [
        'script', 'javascript', 'vbscript', 'onload', 'onerror', 'onclick',
        'eval', 'expression', 'document.cookie', 'window.location',
        'alert(', 'confirm(', 'prompt(', '<script', '</script>',
        'union select', 'drop table', 'delete from', 'insert into',
        'update set', 'create table', 'alter table', 'exec(',
        'system(', 'shell_exec', 'passthru', 'file_get_contents'
    ]
    
    SUSPICIOUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Scripts
        r'javascript:',  # JavaScript URLs
        r'on\w+\s*=',  # Event handlers
        r'expression\s*\(',  # CSS expressions
        r'@import',  # CSS imports
        r'url\s*\(',  # CSS URLs
        r'\\x[0-9a-fA-F]{2}',  # Hex encoding
        r'%[0-9a-fA-F]{2}',  # URL encoding
        r'&#x?[0-9a-fA-F]+;',  # HTML entities
        r'(union|select|insert|update|delete|drop|create|alter)\s+',  # SQL
        r'(eval|exec|system|shell_exec|passthru)\s*\(',  # Code execution
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def sanitize_string(self, value, sanitization_level='basic', max_length=None):
        \"\"\"Sanitise une chaîne de caractères\"\"\"
        if not isinstance(value, str):
            return str(value) if value is not None else ''
        
        # Limiter la longueur
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        # Nettoyer les caractères de contrôle
        value = self._remove_control_characters(value)
        
        # Détecter les patterns suspects
        if self._contains_suspicious_patterns(value):
            self.logger.warning(f"Suspicious pattern detected in input: {value[:50]}...")
            return ''  # Rejeter complètement l'entrée suspecte
        
        # Sanitisation selon le niveau
        if sanitization_level == 'basic':
            # Échapper tout le HTML
            value = html.escape(value)
        elif sanitization_level == 'text':
            # Permettre quelques tags de formatage
            value = bleach.clean(value, 
                               tags=self.ALLOWED_TAGS['text'],
                               attributes=self.ALLOWED_ATTRIBUTES,
                               strip=True)
        elif sanitization_level == 'rich':
            # Permettre plus de tags HTML
            value = bleach.clean(value,
                               tags=self.ALLOWED_TAGS['rich'],
                               attributes=self.ALLOWED_ATTRIBUTES,
                               strip=True)
        
        # Normaliser les espaces
        value = re.sub(r'\s+', ' ', value).strip()
        
        return value
    
    def sanitize_dict(self, data, schema=None):
        \"\"\"Sanitise un dictionnaire de données\"\"\"
        if not isinstance(data, dict):
            return {}
        
        sanitized = {}
        
        for key, value in data.items():
            # Sanitiser la clé
            clean_key = self.sanitize_string(key, 'basic', 100)
            
            if not clean_key:
                continue
            
            # Appliquer le schéma si fourni
            if schema and clean_key in schema:
                field_config = schema[clean_key]
                sanitized_value = self._sanitize_by_schema(value, field_config)
            else:
                # Sanitisation par défaut
                if isinstance(value, str):
                    sanitized_value = self.sanitize_string(value, 'basic', 1000)
                elif isinstance(value, (int, float)):
                    sanitized_value = value
                elif isinstance(value, bool):
                    sanitized_value = value
                elif isinstance(value, list):
                    sanitized_value = [self.sanitize_string(str(item), 'basic', 500) 
                                     for item in value[:10]]  # Limiter à 10 éléments
                elif isinstance(value, dict):
                    sanitized_value = self.sanitize_dict(value)
                else:
                    sanitized_value = self.sanitize_string(str(value), 'basic', 500)
            
            sanitized[clean_key] = sanitized_value
        
        return sanitized
    
    def validate_pattern(self, value, pattern_name):
        \"\"\"Valide une valeur contre un pattern défini\"\"\"
        if pattern_name not in self.PATTERNS:
            return False
        
        pattern = self.PATTERNS[pattern_name]
        return bool(re.match(pattern, str(value)))
    
    def _sanitize_by_schema(self, value, field_config):
        \"\"\"Sanitise selon un schéma de champ\"\"\"
        field_type = field_config.get('type', 'string')
        max_length = field_config.get('max_length')
        pattern = field_config.get('pattern')
        sanitization_level = field_config.get('sanitization', 'basic')
        
        if field_type == 'string':
            sanitized = self.sanitize_string(value, sanitization_level, max_length)
            
            # Valider le pattern si fourni
            if pattern and not re.match(pattern, sanitized):
                return ''
            
            return sanitized
        
        elif field_type == 'integer':
            try:
                return int(float(str(value)))
            except (ValueError, TypeError):
                return 0
        
        elif field_type == 'float':
            try:
                return float(str(value))
            except (ValueError, TypeError):
                return 0.0
        
        elif field_type == 'boolean':
            return bool(value)
        
        elif field_type == 'email':
            sanitized = self.sanitize_string(value, 'basic', 120)
            if self.validate_pattern(sanitized, 'email'):
                return sanitized.lower()
            return ''
        
        return self.sanitize_string(str(value), 'basic', max_length or 500)
    
    def _remove_control_characters(self, value):
        \"\"\"Supprime les caractères de contrôle\"\"\"
        # Garder seulement les caractères imprimables et les espaces/tabs/newlines
        return ''.join(char for char in value 
                      if ord(char) >= 32 or char in '\t\n\r')
    
    def _contains_suspicious_patterns(self, value):
        \"\"\"Vérifie si la valeur contient des patterns suspects\"\"\"
        value_lower = value.lower()
        
        # Vérifier les mots interdits
        for word in self.FORBIDDEN_WORDS:
            if word in value_lower:
                return True
        
        # Vérifier les patterns suspects
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        return False

class ContentSecurityPolicy:
    \"\"\"Gestionnaire de Content Security Policy\"\"\"
    
    DEFAULT_POLICY = {
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
    
    @classmethod
    def generate_header(cls, custom_policy=None):
        \"\"\"Génère l'en-tête CSP\"\"\"
        policy = cls.DEFAULT_POLICY.copy()
        
        if custom_policy:
            policy.update(custom_policy)
        
        policy_parts = []
        for directive, sources in policy.items():
            sources_str = ' '.join(sources)
            policy_parts.append(f"{directive} {sources_str}")
        
        return '; '.join(policy_parts)

class SecurityHeaders:
    \"\"\"Gestionnaire des en-têtes de sécurité\"\"\"
    
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
    }
    
    @classmethod
    def apply_headers(cls, response):
        \"\"\"Applique les en-têtes de sécurité à une réponse\"\"\"
        for header, value in cls.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Ajouter CSP
        response.headers['Content-Security-Policy'] = ContentSecurityPolicy.generate_header()
        
        return response

# Décorateurs de sanitization
def sanitize_json_input(schema=None):
    \"\"\"Décorateur pour sanitiser les entrées JSON\"\"\"
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                sanitizer = InputSanitizer()
                
                try:
                    raw_data = request.get_json()
                    sanitized_data = sanitizer.sanitize_dict(raw_data, schema)
                    
                    # Remplacer les données de la requête
                    request._cached_json = sanitized_data
                    
                except Exception as e:
                    logging.error(f"JSON sanitization error: {e}")
                    return jsonify({'error': 'Invalid input data'}), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def sanitize_form_input(schema=None):
    \"\"\"Décorateur pour sanitiser les entrées de formulaire\"\"\"
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.form:
                sanitizer = InputSanitizer()
                
                sanitized_form = {}
                for key, value in request.form.items():
                    if schema and key in schema:
                        sanitized_form[key] = sanitizer._sanitize_by_schema(value, schema[key])
                    else:
                        sanitized_form[key] = sanitizer.sanitize_string(value, 'basic', 1000)
                
                # Remplacer les données du formulaire
                request.form = sanitized_form
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def apply_security_headers(f):
    \"\"\"Décorateur pour appliquer les en-têtes de sécurité\"\"\"
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Si c'est une réponse Flask, appliquer les en-têtes
        if hasattr(response, 'headers'):
            response = SecurityHeaders.apply_headers(response)
        
        return response
    
    return decorated_function

# Schémas de validation pour les différents endpoints
VALIDATION_SCHEMAS = {
    'user_registration': {
        'username': {
            'type': 'string',
            'max_length': 80,
            'pattern': r'^[a-zA-Z0-9_-]{3,80}$',
            'sanitization': 'basic'
        },
        'email': {
            'type': 'email',
            'max_length': 120
        },
        'password': {
            'type': 'string',
            'max_length': 128,
            'sanitization': 'basic'
        },
        'bunker_id': {
            'type': 'string',
            'pattern': r'^bunker-[0-9]{2}$',
            'sanitization': 'basic'
        },
        'room_preference': {
            'type': 'string',
            'max_length': 100,
            'sanitization': 'basic'
        },
        'emergency_contact': {
            'type': 'string',
            'max_length': 200,
            'sanitization': 'basic'
        },
        'medical_conditions': {
            'type': 'string',
            'max_length': 1000,
            'sanitization': 'text'
        }
    },
    
    'environmental_data': {
        'temperature': {'type': 'float'},
        'humidity': {'type': 'float'},
        'air_quality': {'type': 'float'},
        'oxygen_level': {'type': 'float'},
        'co2_level': {'type': 'float'},
        'radiation_level': {'type': 'float'},
        'atmospheric_pressure': {'type': 'float'},
        'bunker_id': {
            'type': 'string',
            'pattern': r'^bunker-[0-9]{2}$'
        },
        'sensor_location': {
            'type': 'string',
            'max_length': 100,
            'sanitization': 'basic'
        },
        'sensor_id': {
            'type': 'string',
            'max_length': 50,
            'pattern': r'^[a-zA-Z0-9_-]{1,50}$'
        }
    },
    
    'quiz_answer': {
        'question_id': {'type': 'integer'},
        'answer': {
            'type': 'string',
            'max_length': 500,
            'sanitization': 'basic'
        }
    },
    
    'alert_creation': {
        'alert_type': {
            'type': 'string',
            'max_length': 50,
            'sanitization': 'basic'
        },
        'severity': {
            'type': 'string',
            'pattern': r'^(low|medium|high|critical|emergency)$'
        },
        'title': {
            'type': 'string',
            'max_length': 200,
            'sanitization': 'basic'
        },
        'message': {
            'type': 'string',
            'max_length': 2000,
            'sanitization': 'text'
        },
        'bunker_id': {
            'type': 'string',
            'pattern': r'^bunker-[0-9]{2}$'
        },
        'sensor_location': {
            'type': 'string',
            'max_length': 100,
            'sanitization': 'basic'
        }
    }
}
"""
    
    return sanitization_code

def create_advanced_security_middleware():
    """Crée le middleware de sécurité avancé"""
    
    middleware_code = """from flask import request, jsonify, session, g
from functools import wraps
import time
import hashlib
import hmac
import secrets
import ipaddress
from datetime import datetime, timedelta
import logging

class SecurityMiddleware:
    \"\"\"Middleware de sécurité avancé\"\"\"
    
    def __init__(self, app=None):
        self.app = app
        self.blocked_ips = set()
        self.rate_limits = {}
        self.suspicious_activities = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        \"\"\"Initialise le middleware avec l'application Flask\"\"\"
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown)
    
    def before_request(self):
        \"\"\"Traitement avant chaque requête\"\"\"
        # Obtenir l'IP du client
        client_ip = self._get_client_ip()
        g.client_ip = client_ip
        
        # Vérifier si l'IP est bloquée
        if self._is_ip_blocked(client_ip):
            return jsonify({'error': 'Access denied'}), 403
        
        # Vérifier les limites de taux
        if self._check_rate_limit(client_ip):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # Vérifier l'intégrité de la requête
        if not self._verify_request_integrity():
            return jsonify({'error': 'Request integrity check failed'}), 400
        
        # Détecter les activités suspectes
        self._detect_suspicious_activity(client_ip)
        
        # Enregistrer la requête pour audit
        self._log_request()
    
    def after_request(self, response):
        \"\"\"Traitement après chaque requête\"\"\"
        # Appliquer les en-têtes de sécurité
        response = self._apply_security_headers(response)
        
        # Enregistrer la réponse pour audit
        self._log_response(response)
        
        return response
    
    def teardown(self, exception):
        \"\"\"Nettoyage après la requête\"\"\"
        if exception:
            logging.error(f"Request exception: {exception}")
    
    def _get_client_ip(self):
        \"\"\"Obtient l'IP réelle du client\"\"\"
        # Vérifier les en-têtes de proxy
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr
    
    def _is_ip_blocked(self, ip):
        \"\"\"Vérifie si une IP est bloquée\"\"\"
        return ip in self.blocked_ips
    
    def _check_rate_limit(self, ip):
        \"\"\"Vérifie les limites de taux\"\"\"
        now = time.time()
        window = 60  # 1 minute
        limit = 100  # 100 requêtes par minute
        
        if ip not in self.rate_limits:
            self.rate_limits[ip] = []
        
        # Nettoyer les anciennes requêtes
        self.rate_limits[ip] = [
            req_time for req_time in self.rate_limits[ip]
            if now - req_time < window
        ]
        
        # Vérifier la limite
        if len(self.rate_limits[ip]) >= limit:
            self._add_suspicious_activity(ip, 'rate_limit_exceeded')
            return True
        
        # Enregistrer cette requête
        self.rate_limits[ip].append(now)
        return False
    
    def _verify_request_integrity(self):
        \"\"\"Vérifie l'intégrité de la requête\"\"\"
        # Vérifier la taille de la requête
        content_length = request.content_length
        if content_length and content_length > 10 * 1024 * 1024:  # 10MB max
            return False
        
        # Vérifier les en-têtes suspects
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent or len(user_agent) > 500:
            return False
        
        # Vérifier les caractères suspects dans l'URL
        if self._contains_suspicious_chars(request.url):
            return False
        
        return True
    
    def _contains_suspicious_chars(self, text):
        \"\"\"Vérifie la présence de caractères suspects\"\"\"
        suspicious_patterns = [
            r'<script', r'javascript:', r'vbscript:', r'onload=',
            r'onerror=', r'onclick=', r'eval\(', r'expression\(',
            r'union\s+select', r'drop\s+table', r'insert\s+into'
        ]
        
        text_lower = text.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _detect_suspicious_activity(self, ip):
        \"\"\"Détecte les activités suspectes\"\"\"
        now = time.time()
        
        # Vérifier les patterns d'attaque
        if self._is_attack_pattern():
            self._add_suspicious_activity(ip, 'attack_pattern')
        
        # Vérifier les requêtes anormales
        if self._is_abnormal_request():
            self._add_suspicious_activity(ip, 'abnormal_request')
        
        # Vérifier si l'IP a trop d'activités suspectes
        if ip in self.suspicious_activities:
            activities = self.suspicious_activities[ip]
            recent_activities = [
                activity for activity in activities
                if now - activity['timestamp'] < 3600  # 1 heure
            ]
            
            if len(recent_activities) > 10:
                self._block_ip(ip, 'too_many_suspicious_activities')
    
    def _is_attack_pattern(self):
        \"\"\"Détecte les patterns d'attaque\"\"\"
        # Vérifier les tentatives d'injection SQL
        query_string = request.query_string.decode('utf-8', errors='ignore')
        if self._contains_suspicious_chars(query_string):
            return True
        
        # Vérifier les tentatives XSS
        if request.is_json:
            try:
                data = request.get_json()
                if data and self._contains_xss_payload(str(data)):
                    return True
            except:
                pass
        
        return False
    
    def _contains_xss_payload(self, text):
        \"\"\"Vérifie la présence de payload XSS\"\"\"
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'expression\s*\(',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>'
        ]
        
        text_lower = text.lower()
        for pattern in xss_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _is_abnormal_request(self):
        \"\"\"Détecte les requêtes anormales\"\"\"
        # Vérifier les en-têtes manquants ou suspects
        if not request.headers.get('Accept'):
            return True
        
        # Vérifier les méthodes HTTP suspectes
        if request.method in ['TRACE', 'CONNECT']:
            return True
        
        # Vérifier les chemins suspects
        path = request.path.lower()
        suspicious_paths = [
            '/admin', '/wp-admin', '/phpmyadmin', '/.env',
            '/config', '/backup', '/test', '/debug'
        ]
        
        for suspicious_path in suspicious_paths:
            if suspicious_path in path:
                return True
        
        return False
    
    def _add_suspicious_activity(self, ip, activity_type):
        \"\"\"Ajoute une activité suspecte\"\"\"
        if ip not in self.suspicious_activities:
            self.suspicious_activities[ip] = []
        
        self.suspicious_activities[ip].append({
            'type': activity_type,
            'timestamp': time.time(),
            'url': request.url,
            'user_agent': request.headers.get('User-Agent', ''),
            'method': request.method
        })
        
        logging.warning(f"Suspicious activity detected from {ip}: {activity_type}")
    
    def _block_ip(self, ip, reason):
        \"\"\"Bloque une IP\"\"\"
        self.blocked_ips.add(ip)
        logging.critical(f"IP {ip} blocked: {reason}")
        
        # En production, ajouter à un système de blocage persistant
        # comme iptables ou un WAF
    
    def _apply_security_headers(self, response):
        \"\"\"Applique les en-têtes de sécurité\"\"\"
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'Content-Security-Policy': self._generate_csp(),
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    def _generate_csp(self):
        \"\"\"Génère la Content Security Policy\"\"\"
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "img-src 'self' data: https:",
            "font-src 'self' https://fonts.gstatic.com",
            "connect-src 'self'",
            "media-src 'self'",
            "object-src 'none'",
            "child-src 'none'",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "base-uri 'self'"
        ]
        
        return '; '.join(csp_directives)
    
    def _log_request(self):
        \"\"\"Enregistre la requête pour audit\"\"\"
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'ip': g.client_ip,
            'method': request.method,
            'url': request.url,
            'user_agent': request.headers.get('User-Agent', ''),
            'referer': request.headers.get('Referer', ''),
            'content_length': request.content_length,
            'user_id': session.get('user_id')
        }
        
        # En production, envoyer à un système de logging centralisé
        logging.info(f"Request: {log_data}")
    
    def _log_response(self, response):
        \"\"\"Enregistre la réponse pour audit\"\"\"
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'ip': g.client_ip,
            'status_code': response.status_code,
            'content_length': response.content_length,
            'user_id': session.get('user_id')
        }
        
        # En production, envoyer à un système de logging centralisé
        logging.info(f"Response: {log_data}")

class ThreatDetection:
    \"\"\"Système de détection de menaces\"\"\"
    
    def __init__(self):
        self.threat_patterns = self._load_threat_patterns()
        self.ml_model = None  # Placeholder pour un modèle ML
    
    def _load_threat_patterns(self):
        \"\"\"Charge les patterns de menaces\"\"\"
        return {
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
    
    def analyze_request(self, request_data):
        \"\"\"Analyse une requête pour détecter des menaces\"\"\"
        threats_detected = []
        
        # Analyser l'URL
        url_threats = self._analyze_text(request_data.get('url', ''))
        if url_threats:
            threats_detected.extend(url_threats)
        
        # Analyser les paramètres
        params = request_data.get('params', {})
        for key, value in params.items():
            param_threats = self._analyze_text(f"{key}={value}")
            if param_threats:
                threats_detected.extend(param_threats)
        
        # Analyser le body
        body = request_data.get('body', '')
        if body:
            body_threats = self._analyze_text(body)
            if body_threats:
                threats_detected.extend(body_threats)
        
        # Analyser les en-têtes
        headers = request_data.get('headers', {})
        for key, value in headers.items():
            header_threats = self._analyze_text(f"{key}: {value}")
            if header_threats:
                threats_detected.extend(header_threats)
        
        return threats_detected
    
    def _analyze_text(self, text):
        \"\"\"Analyse un texte pour détecter des patterns de menaces\"\"\"
        threats = []
        text_lower = text.lower()
        
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    threats.append({
                        'type': threat_type,
                        'pattern': pattern,
                        'confidence': 0.8,  # Placeholder pour un score ML
                        'location': 'text'
                    })
        
        return threats
    
    def calculate_risk_score(self, threats):
        \"\"\"Calcule un score de risque basé sur les menaces détectées\"\"\"
        if not threats:
            return 0
        
        risk_weights = {
            'sql_injection': 0.9,
            'xss': 0.8,
            'command_injection': 0.95,
            'path_traversal': 0.7
        }
        
        total_risk = 0
        for threat in threats:
            threat_type = threat['type']
            confidence = threat['confidence']
            weight = risk_weights.get(threat_type, 0.5)
            
            total_risk += weight * confidence
        
        return min(total_risk, 1.0)  # Normaliser entre 0 et 1

# Décorateur pour la détection de menaces
def threat_detection(f):
    \"\"\"Décorateur pour la détection de menaces\"\"\"
    @wraps(f)
    def decorated_function(*args, **kwargs):
        detector = ThreatDetection()
        
        # Préparer les données de la requête
        request_data = {
            'url': request.url,
            'params': dict(request.args),
            'body': request.get_data(as_text=True),
            'headers': dict(request.headers)
        }
        
        # Analyser les menaces
        threats = detector.analyze_request(request_data)
        
        if threats:
            risk_score = detector.calculate_risk_score(threats)
            
            # Bloquer les requêtes à haut risque
            if risk_score > 0.7:
                logging.critical(f"High-risk request blocked: {threats}")
                return jsonify({'error': 'Request blocked by security system'}), 403
            
            # Logger les menaces de risque moyen
            elif risk_score > 0.4:
                logging.warning(f"Medium-risk request detected: {threats}")
        
        return f(*args, **kwargs)
    
    return decorated_function
"""
    
    return middleware_code

def create_encryption_utilities():
    """Crée les utilitaires de chiffrement"""
    
    encryption_code = """import os
import base64
import hashlib
import hmac
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import json

class EncryptionManager:
    \"\"\"Gestionnaire de chiffrement pour les données sensibles\"\"\"
    
    def __init__(self, master_key=None):
        self.master_key = master_key or os.environ.get('MASTER_KEY')
        if not self.master_key:
            raise ValueError("Master key is required for encryption")
        
        self.fernet = self._create_fernet_key()
    
    def _create_fernet_key(self):
        \"\"\"Crée une clé Fernet à partir de la clé maître\"\"\"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'bunker_salt_2025',  # En production, utiliser un salt aléatoire
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    def encrypt_string(self, plaintext):
        \"\"\"Chiffre une chaîne de caractères\"\"\"
        if not plaintext:
            return None
        
        encrypted = self.fernet.encrypt(plaintext.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt_string(self, ciphertext):
        \"\"\"Déchiffre une chaîne de caractères\"\"\"
        if not ciphertext:
            return None
        
        try:
            encrypted_data = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
            decrypted = self.fernet.decrypt(encrypted_data)
            return decrypted.decode('utf-8')
        except Exception:
            return None
    
    def encrypt_dict(self, data):
        \"\"\"Chiffre un dictionnaire\"\"\"
        if not data:
            return None
        
        json_data = json.dumps(data, sort_keys=True)
        return self.encrypt_string(json_data)
    
    def decrypt_dict(self, ciphertext):
        \"\"\"Déchiffre un dictionnaire\"\"\"
        if not ciphertext:
            return None
        
        json_data = self.decrypt_string(ciphertext)
        if json_data:
            try:
                return json.loads(json_data)
            except json.JSONDecodeError:
                return None
        return None
    
    def hash_password(self, password, salt=None):
        \"\"\"Hash un mot de passe avec salt\"\"\"
        if salt is None:
            salt = secrets.token_bytes(32)
        
        pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                     password.encode('utf-8'), 
                                     salt, 
                                     100000)
        
        return {
            'hash': base64.b64encode(pwdhash).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8')
        }
    
    def verify_password(self, password, stored_hash, stored_salt):
        \"\"\"Vérifie un mot de passe\"\"\"
        salt = base64.b64decode(stored_salt.encode('utf-8'))
        pwdhash = hashlib.pbkdf2_hmac('sha256',
                                     password.encode('utf-8'),
                                     salt,
                                     100000)
        
        stored_hash_bytes = base64.b64decode(stored_hash.encode('utf-8'))
        return hmac.compare_digest(pwdhash, stored_hash_bytes)
    
    def generate_secure_token(self, length=32):
        \"\"\"Génère un token sécurisé\"\"\"
        return secrets.token_urlsafe(length)
    
    def create_hmac_signature(self, data, secret=None):
        \"\"\"Crée une signature HMAC\"\"\"
        if secret is None:
            secret = self.master_key
        
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        
        signature = hmac.new(
            secret.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_hmac_signature(self, data, signature, secret=None):
        \"\"\"Vérifie une signature HMAC\"\"\"
        expected_signature = self.create_hmac_signature(data, secret)
        return hmac.compare_digest(signature, expected_signature)

class SecureStorage:
    \"\"\"Stockage sécurisé pour les données sensibles\"\"\"
    
    def __init__(self, encryption_manager):
        self.encryption = encryption_manager
        self.storage = {}  # En production, utiliser Redis ou une base sécurisée
    
    def store_sensitive_data(self, key, data, ttl=3600):
        \"\"\"Stocke des données sensibles chiffrées\"\"\"
        encrypted_data = self.encryption.encrypt_dict(data)
        
        self.storage[key] = {
            'data': encrypted_data,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
    
    def retrieve_sensitive_data(self, key):
        \"\"\"Récupère des données sensibles\"\"\"
        if key not in self.storage:
            return None
        
        stored_item = self.storage[key]
        
        # Vérifier l'expiration
        if time.time() > stored_item['expires_at']:
            del self.storage[key]
            return None
        
        return self.encryption.decrypt_dict(stored_item['data'])
    
    def delete_sensitive_data(self, key):
        \"\"\"Supprime des données sensibles\"\"\"
        if key in self.storage:
            del self.storage[key]
    
    def cleanup_expired_data(self):
        \"\"\"Nettoie les données expirées\"\"\"
        now = time.time()
        expired_keys = [
            key for key, item in self.storage.items()
            if now > item['expires_at']
        ]
        
        for key in expired_keys:
            del self.storage[key]
        
        return len(expired_keys)

class DataMasking:
    \"\"\"Utilitaires de masquage de données\"\"\"
    
    @staticmethod
    def mask_email(email):
        \"\"\"Masque une adresse email\"\"\"
        if not email or '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone):
        \"\"\"Masque un numéro de téléphone\"\"\"
        if not phone:
            return phone
        
        # Garder seulement les chiffres
        digits = ''.join(filter(str.isdigit, phone))
        
        if len(digits) < 4:
            return '*' * len(digits)
        
        return digits[:2] + '*' * (len(digits) - 4) + digits[-2:]
    
    @staticmethod
    def mask_credit_card(card_number):
        \"\"\"Masque un numéro de carte de crédit\"\"\"
        if not card_number:
            return card_number
        
        digits = ''.join(filter(str.isdigit, card_number))
        
        if len(digits) < 8:
            return '*' * len(digits)
        
        return '*' * (len(digits) - 4) + digits[-4:]
    
    @staticmethod
    def mask_sensitive_dict(data, sensitive_fields=None):
        \"\"\"Masque les champs sensibles d'un dictionnaire\"\"\"
        if sensitive_fields is None:
            sensitive_fields = [
                'password', 'token', 'secret', 'key', 'credit_card',
                'ssn', 'social_security', 'passport', 'license'
            ]
        
        masked_data = data.copy()
        
        for key, value in masked_data.items():
            key_lower = key.lower()
            
            if any(field in key_lower for field in sensitive_fields):
                if isinstance(value, str):
                    if 'email' in key_lower:
                        masked_data[key] = DataMasking.mask_email(value)
                    elif 'phone' in key_lower:
                        masked_data[key] = DataMasking.mask_phone(value)
                    elif 'card' in key_lower:
                        masked_data[key] = DataMasking.mask_credit_card(value)
                    else:
                        masked_data[key] = '*' * min(len(value), 8)
                else:
                    masked_data[key] = '[MASKED]'
        
        return masked_data

# Décorateur pour le chiffrement automatique
def encrypt_response_data(fields_to_encrypt=None):
    \"\"\"Décorateur pour chiffrer automatiquement les données de réponse\"\"\"
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            
            if isinstance(response, dict) and fields_to_encrypt:
                encryption_manager = EncryptionManager()
                
                for field in fields_to_encrypt:
                    if field in response:
                        response[field] = encryption_manager.encrypt_string(
                            str(response[field])
                        )
            
            return response
        
        return decorated_function
    return decorator
"""
    
    return encryption_code

def main():
    """Fonction principale pour créer le système de sécurisation avancé"""
    project_path = "/home/ubuntu/lataupe-bunker-tech"
    
    print("🔒 Création du système de sécurisation et sanitization avancé...")
    print("=" * 70)
    
    # Créer le dossier security
    security_dir = os.path.join(project_path, 'src', 'security')
    os.makedirs(security_dir, exist_ok=True)
    
    # Créer les fichiers de sécurité
    sanitization_file = os.path.join(security_dir, 'sanitization.py')
    with open(sanitization_file, 'w') as f:
        f.write(create_input_sanitization_system())
    
    middleware_file = os.path.join(security_dir, 'middleware.py')
    with open(middleware_file, 'w') as f:
        f.write(create_advanced_security_middleware())
    
    encryption_file = os.path.join(security_dir, 'encryption.py')
    with open(encryption_file, 'w') as f:
        f.write(create_encryption_utilities())
    
    # Créer le fichier __init__.py
    init_file = os.path.join(security_dir, '__init__.py')
    with open(init_file, 'w') as f:
        f.write('# Security package for lataupe-bunker-tech\n')
    
    print("\\n✅ Système de sécurisation avancé créé avec succès!")
    print("\\n📋 Fichiers créés:")
    print(f"   • Système de sanitization: {sanitization_file}")
    print(f"   • Middleware de sécurité: {middleware_file}")
    print(f"   • Utilitaires de chiffrement: {encryption_file}")
    
    print("\\n🛡️ Fonctionnalités de sécurité:")
    print("   • Sanitization avancée des entrées utilisateur")
    print("   • Détection de patterns d'attaque (SQL injection, XSS)")
    print("   • Middleware de sécurité avec rate limiting")
    print("   • Content Security Policy automatique")
    print("   • Chiffrement des données sensibles")
    print("   • Masquage des données pour les logs")
    print("   • Détection de menaces en temps réel")
    
    print("\\n🔍 Protections implémentées:")
    print("   • SQL Injection Prevention")
    print("   • Cross-Site Scripting (XSS) Protection")
    print("   • Command Injection Detection")
    print("   • Path Traversal Prevention")
    print("   • Rate Limiting et IP Blocking")
    print("   • Request Integrity Verification")
    print("   • Suspicious Activity Detection")
    
    print("\\n⚠️  Configuration requise:")
    print("   • Variable MASTER_KEY pour le chiffrement")
    print("   • Configuration des schémas de validation")
    print("   • Intégration avec le middleware Flask")
    print("   • Tests de sécurité complets")
    
    return True

if __name__ == "__main__":
    main()

