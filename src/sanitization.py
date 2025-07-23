import re
import html
import bleach
import urllib.parse
from markupsafe import Markup, escape
from flask import request, jsonify
from functools import wraps
import logging

class InputSanitizer:
    """Système de sanitization des entrées utilisateur"""
    
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
        r'\x[0-9a-fA-F]{2}',  # Hex encoding
        r'%[0-9a-fA-F]{2}',  # URL encoding
        r'&#x?[0-9a-fA-F]+;',  # HTML entities
        r'(union|select|insert|update|delete|drop|create|alter)\s+',  # SQL
        r'(eval|exec|system|shell_exec|passthru)\s*\(',  # Code execution
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def sanitize_string(self, value, sanitization_level='basic', max_length=None):
        """Sanitise une chaîne de caractères"""
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
        """Sanitise un dictionnaire de données"""
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
        """Valide une valeur contre un pattern défini"""
        if pattern_name not in self.PATTERNS:
            return False
        
        pattern = self.PATTERNS[pattern_name]
        return bool(re.match(pattern, str(value)))
    
    def _sanitize_by_schema(self, value, field_config):
        """Sanitise selon un schéma de champ"""
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
        """Supprime les caractères de contrôle"""
        # Garder seulement les caractères imprimables et les espaces/tabs/newlines
        return ''.join(char for char in value 
                      if ord(char) >= 32 or char in '	
')
    
    def _contains_suspicious_patterns(self, value):
        """Vérifie si la valeur contient des patterns suspects"""
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
    """Gestionnaire de Content Security Policy"""
    
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
        """Génère l'en-tête CSP"""
        policy = cls.DEFAULT_POLICY.copy()
        
        if custom_policy:
            policy.update(custom_policy)
        
        policy_parts = []
        for directive, sources in policy.items():
            sources_str = ' '.join(sources)
            policy_parts.append(f"{directive} {sources_str}")
        
        return '; '.join(policy_parts)

class SecurityHeaders:
    """Gestionnaire des en-têtes de sécurité"""
    
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
        """Applique les en-têtes de sécurité à une réponse"""
        for header, value in cls.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Ajouter CSP
        response.headers['Content-Security-Policy'] = ContentSecurityPolicy.generate_header()
        
        return response

# Décorateurs de sanitization
def sanitize_json_input(schema=None):
    """Décorateur pour sanitiser les entrées JSON"""
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
    """Décorateur pour sanitiser les entrées de formulaire"""
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
    """Décorateur pour appliquer les en-têtes de sécurité"""
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
