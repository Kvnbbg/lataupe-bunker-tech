from flask import request, jsonify, session, g
from functools import wraps
import time
import hashlib
import hmac
import secrets
import ipaddress
from datetime import datetime, timedelta
import logging

class SecurityMiddleware:
    """Middleware de sécurité avancé"""
    
    def __init__(self, app=None):
        self.app = app
        self.blocked_ips = set()
        self.rate_limits = {}
        self.suspicious_activities = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialise le middleware avec l'application Flask"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown)
    
    def before_request(self):
        """Traitement avant chaque requête"""
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
        """Traitement après chaque requête"""
        # Appliquer les en-têtes de sécurité
        response = self._apply_security_headers(response)
        
        # Enregistrer la réponse pour audit
        self._log_response(response)
        
        return response
    
    def teardown(self, exception):
        """Nettoyage après la requête"""
        if exception:
            logging.error(f"Request exception: {exception}")
    
    def _get_client_ip(self):
        """Obtient l'IP réelle du client"""
        # Vérifier les en-têtes de proxy
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr
    
    def _is_ip_blocked(self, ip):
        """Vérifie si une IP est bloquée"""
        return ip in self.blocked_ips
    
    def _check_rate_limit(self, ip):
        """Vérifie les limites de taux"""
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
        """Vérifie l'intégrité de la requête"""
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
        """Vérifie la présence de caractères suspects"""
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
        """Détecte les activités suspectes"""
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
        """Détecte les patterns d'attaque"""
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
        """Vérifie la présence de payload XSS"""
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
        """Détecte les requêtes anormales"""
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
        """Ajoute une activité suspecte"""
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
        """Bloque une IP"""
        self.blocked_ips.add(ip)
        logging.critical(f"IP {ip} blocked: {reason}")
        
        # En production, ajouter à un système de blocage persistant
        # comme iptables ou un WAF
    
    def _apply_security_headers(self, response):
        """Applique les en-têtes de sécurité"""
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
        """Génère la Content Security Policy"""
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
        """Enregistre la requête pour audit"""
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
        """Enregistre la réponse pour audit"""
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
    """Système de détection de menaces"""
    
    def __init__(self):
        self.threat_patterns = self._load_threat_patterns()
        self.ml_model = None  # Placeholder pour un modèle ML
    
    def _load_threat_patterns(self):
        """Charge les patterns de menaces"""
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
                r"\.\.\\",
                r"%2e%2e%2f",
                r"%2e%2e%5c",
                r"..%2f",
                r"..%5c"
            ]
        }
    
    def analyze_request(self, request_data):
        """Analyse une requête pour détecter des menaces"""
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
        """Analyse un texte pour détecter des patterns de menaces"""
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
        """Calcule un score de risque basé sur les menaces détectées"""
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
    """Décorateur pour la détection de menaces"""
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
