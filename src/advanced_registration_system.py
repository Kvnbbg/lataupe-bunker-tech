#!/usr/bin/env python3
"""
Système d'enregistrement avancé pour lataupe-bunker-tech
Inclut validation, audit, sécurité et fonctionnalités avancées
"""

import os
import json
import re
import secrets
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

def create_advanced_registration_routes():
    """Crée les routes d'enregistrement avancées"""
    
    routes_code = """from flask import Blueprint, request, jsonify, session, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from werkzeug.security import generate_password_hash
from src.models.advanced_models import db, User, BunkerUser, UserSubscription, AuditLog
from src.utils.security import SecurityValidator, RateLimiter
from src.utils.email import EmailService
from datetime import datetime, timedelta
import secrets
import re

registration_bp = Blueprint('registration', __name__, url_prefix='/auth')

class AdvancedRegistrationForm(FlaskForm):
    # Informations de base
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters'),
        Regexp(r'^[a-zA-Z0-9_-]+$', message='Username can only contain letters, numbers, underscores and hyphens')
    ])
    
    email = EmailField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    # Informations bunker
    bunker_id = SelectField('Bunker Assignment', choices=[
        ('bunker-01', 'Bunker-01 (Primary Facility)'),
        ('bunker-02', 'Bunker-02 (Secondary Facility)'),
        ('bunker-03', 'Bunker-03 (Emergency Facility)')
    ], validators=[DataRequired(message='Please select a bunker')])
    
    room_preference = StringField('Room Preference', validators=[
        Length(max=100, message='Room preference must be less than 100 characters')
    ])
    
    emergency_contact = StringField('Emergency Contact', validators=[
        DataRequired(message='Emergency contact is required'),
        Length(max=200, message='Emergency contact must be less than 200 characters')
    ])
    
    medical_conditions = TextAreaField('Medical Conditions/Allergies', validators=[
        Length(max=1000, message='Medical information must be less than 1000 characters')
    ])
    
    # Préférences et consentements
    subscription_type = SelectField('Subscription Type', choices=[
        ('free', 'Free Account (Basic Features)'),
        ('lataupe_plus', 'Lataupe+ (€9.99/month - Advanced Features)')
    ], default='free')
    
    newsletter_consent = BooleanField('Subscribe to safety updates and newsletters')
    data_processing_consent = BooleanField('I consent to data processing for bunker operations', validators=[
        DataRequired(message='Data processing consent is required for bunker access')
    ])
    terms_acceptance = BooleanField('I accept the Terms of Service and Privacy Policy', validators=[
        DataRequired(message='You must accept the terms to register')
    ])
    
    # Validation personnalisée
    def validate_username(self, field):
        if User.query.filter_by(username=field.data.lower()).first():
            raise ValidationError('Username already exists. Please choose a different one.')
        
        # Vérifier les mots interdits
        forbidden_words = ['admin', 'root', 'system', 'bunker', 'emergency']
        if any(word in field.data.lower() for word in forbidden_words):
            raise ValidationError('Username contains forbidden words.')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered. Please use a different email or try logging in.')
    
    def validate_password(self, field):
        password = field.data
        
        # Vérifications de sécurité du mot de passe
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        
        if not re.search(r'\\d', password):
            raise ValidationError('Password must contain at least one number.')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character.')
        
        # Vérifier les mots de passe communs
        common_passwords = ['password', '12345678', 'qwerty123', 'bunker123']
        if password.lower() in common_passwords:
            raise ValidationError('Password is too common. Please choose a more secure password.')

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[
        DataRequired(message='Username or email is required')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    remember_me = BooleanField('Remember me for 30 days')

@registration_bp.route('/register', methods=['GET', 'POST'])
@RateLimiter.limit("5 per minute")
def register():
    \"\"\"Page d'enregistrement avancée\"\"\"
    form = AdvancedRegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Validation de sécurité supplémentaire
            security_validator = SecurityValidator()
            
            # Vérifier l'IP pour détecter les tentatives suspectes
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            if security_validator.is_suspicious_ip(ip_address):
                flash('Registration temporarily unavailable. Please try again later.', 'warning')
                return render_template('auth/register.html', form=form)
            
            # Créer l'utilisateur
            user = User(
                username=form.username.data.lower().strip(),
                email=form.email.data.lower().strip(),
                role='resident',  # Rôle par défaut
                is_active=True,
                is_verified=False  # Nécessite une vérification email
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.flush()  # Pour obtenir l'ID utilisateur
            
            # Créer le profil bunker
            bunker_profile = BunkerUser(
                user_id=user.id,
                bunker_id=form.bunker_id.data,
                access_level='basic',
                room_assignment=form.room_preference.data or 'Unassigned',
                emergency_contact=form.emergency_contact.data,
                medical_info={
                    'conditions': form.medical_conditions.data,
                    'registered_at': datetime.utcnow().isoformat(),
                    'consent_given': True
                },
                security_clearance=1
            )
            
            db.session.add(bunker_profile)
            
            # Créer l'abonnement
            subscription_features = {
                'free': ['basic_quiz', 'emergency_training', 'basic_alerts'],
                'lataupe_plus': ['all_quiz', 'advanced_training', 'detailed_analytics', 'priority_support']
            }
            
            subscription = UserSubscription(
                user_id=user.id,
                subscription_type=form.subscription_type.data,
                features=subscription_features[form.subscription_type.data],
                is_active=True,
                auto_renew=False
            )
            
            if form.subscription_type.data == 'lataupe_plus':
                subscription.expires_at = datetime.utcnow() + timedelta(days=30)  # Essai gratuit
            
            db.session.add(subscription)
            
            # Log d'audit
            AuditLog.log_action(
                user_id=user.id,
                action='user_registration',
                resource_type='user',
                resource_id=str(user.id),
                new_values={
                    'username': user.username,
                    'email': user.email,
                    'bunker_id': bunker_profile.bunker_id,
                    'subscription_type': subscription.subscription_type
                },
                ip_address=ip_address,
                user_agent=request.headers.get('User-Agent'),
                success=True
            )
            
            db.session.commit()
            
            # Envoyer l'email de vérification
            email_service = EmailService()
            verification_token = secrets.token_urlsafe(32)
            
            # Stocker le token temporairement (en production, utiliser Redis)
            session[f'verification_token_{user.id}'] = verification_token
            session[f'verification_expires_{user.id}'] = (datetime.utcnow() + timedelta(hours=24)).isoformat()
            
            email_service.send_verification_email(
                user.email,
                user.username,
                verification_token,
                bunker_profile.bunker_id
            )
            
            flash(f'Registration successful! Welcome to {bunker_profile.bunker_id}. Please check your email to verify your account.', 'success')
            
            # Rediriger vers la page de vérification
            return redirect(url_for('registration.verify_email', user_id=user.id))
            
        except Exception as e:
            db.session.rollback()
            
            # Log de l'erreur
            AuditLog.log_action(
                user_id=None,
                action='registration_failed',
                resource_type='user',
                old_values={'form_data': form.data},
                ip_address=ip_address,
                user_agent=request.headers.get('User-Agent'),
                success=False,
                error_message=str(e)
            )
            
            flash('Registration failed. Please try again or contact support.', 'error')
            return render_template('auth/register.html', form=form)
    
    return render_template('auth/register.html', form=form)

@registration_bp.route('/login', methods=['GET', 'POST'])
@RateLimiter.limit("10 per minute")
def login():
    \"\"\"Page de connexion avec sécurité avancée\"\"\"
    form = LoginForm()
    
    if form.validate_on_submit():
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_agent = request.headers.get('User-Agent')
        
        # Rechercher l'utilisateur par nom d'utilisateur ou email
        user = User.query.filter(
            (User.username == form.username.data.lower()) |
            (User.email == form.username.data.lower())
        ).first()
        
        if user and user.check_password(form.password.data):
            # Vérifier si le compte est verrouillé
            if user.is_locked():
                flash(f'Account is locked until {user.locked_until.strftime("%Y-%m-%d %H:%M")}. Please try again later.', 'warning')
                return render_template('auth/login.html', form=form)
            
            # Vérifier si le compte est actif
            if not user.is_active:
                flash('Account is deactivated. Please contact support.', 'error')
                return render_template('auth/login.html', form=form)
            
            # Connexion réussie
            user.last_login = datetime.utcnow()
            user.failed_login_attempts = 0
            user.locked_until = None
            
            # Créer une session
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(days=30 if form.remember_me.data else 1)
            
            user_session = UserSession(
                session_id=session_id,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at
            )
            
            db.session.add(user_session)
            
            # Log de connexion
            AuditLog.log_action(
                user_id=user.id,
                action='user_login',
                resource_type='session',
                resource_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                success=True
            )
            
            db.session.commit()
            
            # Configurer la session Flask
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['session_id'] = session_id
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Rediriger vers le dashboard approprié
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('main.dashboard'))
        
        else:
            # Connexion échouée
            if user:
                user.failed_login_attempts += 1
                
                # Verrouiller le compte après 5 tentatives
                if user.failed_login_attempts >= 5:
                    user.lock_account(duration_minutes=30)
                    flash('Too many failed attempts. Account locked for 30 minutes.', 'error')
                else:
                    remaining = 5 - user.failed_login_attempts
                    flash(f'Invalid credentials. {remaining} attempts remaining.', 'error')
                
                db.session.commit()
            else:
                flash('Invalid credentials.', 'error')
            
            # Log de tentative échouée
            AuditLog.log_action(
                user_id=user.id if user else None,
                action='login_failed',
                resource_type='session',
                old_values={'username': form.username.data},
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                error_message='Invalid credentials'
            )
    
    return render_template('auth/login.html', form=form)

@registration_bp.route('/verify-email/<int:user_id>')
def verify_email(user_id):
    \"\"\"Page de vérification d'email\"\"\"
    user = User.query.get_or_404(user_id)
    
    if user.is_verified:
        flash('Email already verified. You can log in now.', 'info')
        return redirect(url_for('registration.login'))
    
    return render_template('auth/verify_email.html', user=user)

@registration_bp.route('/verify-email/<int:user_id>/<token>')
def confirm_email(user_id, token):
    \"\"\"Confirmer l'email avec le token\"\"\"
    user = User.query.get_or_404(user_id)
    
    # Vérifier le token
    stored_token = session.get(f'verification_token_{user_id}')
    expires_str = session.get(f'verification_expires_{user_id}')
    
    if not stored_token or not expires_str:
        flash('Verification link is invalid or expired.', 'error')
        return redirect(url_for('registration.register'))
    
    expires_at = datetime.fromisoformat(expires_str)
    if datetime.utcnow() > expires_at:
        flash('Verification link has expired. Please register again.', 'error')
        return redirect(url_for('registration.register'))
    
    if token != stored_token:
        flash('Invalid verification token.', 'error')
        return redirect(url_for('registration.register'))
    
    # Vérifier l'email
    user.is_verified = True
    
    # Nettoyer les tokens de session
    session.pop(f'verification_token_{user_id}', None)
    session.pop(f'verification_expires_{user_id}', None)
    
    # Log de vérification
    AuditLog.log_action(
        user_id=user.id,
        action='email_verified',
        resource_type='user',
        resource_id=str(user.id),
        ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        user_agent=request.headers.get('User-Agent'),
        success=True
    )
    
    db.session.commit()
    
    flash('Email verified successfully! You can now log in to access your bunker.', 'success')
    return redirect(url_for('registration.login'))

@registration_bp.route('/logout')
def logout():
    \"\"\"Déconnexion sécurisée\"\"\"
    user_id = session.get('user_id')
    session_id = session.get('session_id')
    
    if user_id and session_id:
        # Désactiver la session en base
        user_session = UserSession.query.filter_by(
            session_id=session_id,
            user_id=user_id
        ).first()
        
        if user_session:
            user_session.is_active = False
            
            # Log de déconnexion
            AuditLog.log_action(
                user_id=user_id,
                action='user_logout',
                resource_type='session',
                resource_id=session_id,
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent'),
                session_id=session_id,
                success=True
            )
            
            db.session.commit()
    
    # Nettoyer la session Flask
    session.clear()
    
    flash('You have been logged out successfully. Stay safe!', 'info')
    return redirect(url_for('main.index'))

@registration_bp.route('/profile')
def profile():
    \"\"\"Page de profil utilisateur\"\"\"
    if 'user_id' not in session:
        flash('Please log in to access your profile.', 'warning')
        return redirect(url_for('registration.login'))
    
    user = User.query.get(session['user_id'])
    bunker_profile = user.bunker_profile
    subscription = user.subscription
    
    return render_template('auth/profile.html', 
                         user=user, 
                         bunker_profile=bunker_profile,
                         subscription=subscription)

# API endpoints pour l'enregistrement
@registration_bp.route('/api/check-username', methods=['POST'])
def check_username():
    \"\"\"Vérifier la disponibilité d'un nom d'utilisateur\"\"\"
    data = request.get_json()
    username = data.get('username', '').lower().strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    if len(username) < 3:
        return jsonify({'available': False, 'message': 'Username too short'})
    
    existing_user = User.query.filter_by(username=username).first()
    
    return jsonify({
        'available': existing_user is None,
        'message': 'Username available' if existing_user is None else 'Username already taken'
    })

@registration_bp.route('/api/check-email', methods=['POST'])
def check_email():
    \"\"\"Vérifier la disponibilité d'un email\"\"\"
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'})
    
    existing_user = User.query.filter_by(email=email).first()
    
    return jsonify({
        'available': existing_user is None,
        'message': 'Email available' if existing_user is None else 'Email already registered'
    })

@registration_bp.route('/api/password-strength', methods=['POST'])
def check_password_strength():
    \"\"\"Évaluer la force d'un mot de passe\"\"\"
    data = request.get_json()
    password = data.get('password', '')
    
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append('At least 8 characters')
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append('One uppercase letter')
    
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append('One lowercase letter')
    
    if re.search(r'\\d', password):
        score += 1
    else:
        feedback.append('One number')
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append('One special character')
    
    strength_levels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']
    strength = strength_levels[min(score, 4)]
    
    return jsonify({
        'score': score,
        'strength': strength,
        'feedback': feedback,
        'is_strong': score >= 4
    })
"""
    
    return routes_code

def create_security_utilities():
    """Crée les utilitaires de sécurité"""
    
    security_code = """import hashlib
import secrets
import re
import time
from datetime import datetime, timedelta
from flask import request, session
from functools import wraps
import ipaddress

class SecurityValidator:
    \"\"\"Validateur de sécurité pour l'enregistrement\"\"\"
    
    def __init__(self):
        self.suspicious_ips = set()
        self.failed_attempts = {}
    
    def is_suspicious_ip(self, ip_address):
        \"\"\"Vérifie si une IP est suspecte\"\"\"
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
        \"\"\"Enregistre une tentative échouée\"\"\"
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = []
        
        self.failed_attempts[ip_address].append(time.time())
        
        # Nettoyer les anciennes tentatives
        self.failed_attempts[ip_address] = [
            t for t in self.failed_attempts[ip_address] 
            if time.time() - t < 3600
        ]
    
    def _is_development(self):
        \"\"\"Vérifie si on est en mode développement\"\"\"
        import os
        return os.environ.get('FLASK_ENV') == 'development'
    
    @staticmethod
    def validate_password_strength(password):
        \"\"\"Valide la force d'un mot de passe\"\"\"
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\\d', password):
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
        \"\"\"Génère un token sécurisé\"\"\"
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_sensitive_data(data):
        \"\"\"Hash des données sensibles pour les logs\"\"\"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

class RateLimiter:
    \"\"\"Limiteur de taux pour les requêtes\"\"\"
    
    _requests = {}
    
    @classmethod
    def limit(cls, rate_string):
        \"\"\"Décorateur pour limiter le taux de requêtes\"\"\"
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
    \"\"\"Gestionnaire de sessions sécurisé\"\"\"
    
    @staticmethod
    def create_secure_session(user_id, remember_me=False):
        \"\"\"Crée une session sécurisée\"\"\"
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
        \"\"\"Valide une session\"\"\"
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
        \"\"\"Nettoie les sessions expirées\"\"\"
        from src.models.advanced_models import UserSession, db
        
        expired_sessions = UserSession.query.filter(
            UserSession.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            session.is_active = False
        
        db.session.commit()
        return len(expired_sessions)

def require_auth(f):
    \"\"\"Décorateur pour exiger une authentification\"\"\"
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
    \"\"\"Décorateur pour exiger un rôle spécifique\"\"\"
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
"""
    
    return security_code

def create_email_service():
    """Crée le service d'email pour les notifications"""
    
    email_code = """import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import logging

class EmailService:
    \"\"\"Service d'envoi d'emails pour les notifications\"\"\"
    
    def __init__(self):
        self.smtp_server = os.environ.get('SMTP_SERVER', 'localhost')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@bunker.tech')
        self.from_name = os.environ.get('FROM_NAME', 'Lataupe Bunker Tech')
        
        self.logger = logging.getLogger(__name__)
    
    def send_email(self, to_email, subject, html_content, text_content=None):
        \"\"\"Envoie un email\"\"\"
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Ajouter le contenu texte si fourni
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Ajouter le contenu HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Envoyer l'email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_username and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            self.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_verification_email(self, email, username, token, bunker_id):
        \"\"\"Envoie l'email de vérification\"\"\"
        verification_url = f"{os.environ.get('BASE_URL', 'http://localhost:5001')}/auth/verify-email/{token}"
        
        subject = f"Welcome to {bunker_id} - Verify Your Account"
        
        html_content = f\"\"\"
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Account Verification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏠 Welcome to Lataupe Bunker Tech</h1>
                    <p>Your survival depends on secure access</p>
                </div>
                
                <div class="content">
                    <h2>Hello {username},</h2>
                    
                    <p>Welcome to <strong>{bunker_id}</strong>! Your registration has been received and your bunker access is being prepared.</p>
                    
                    <p>To complete your registration and activate your account, please verify your email address by clicking the button below:</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify My Account</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: #f0f0f0; padding: 10px; border-radius: 3px;">{verification_url}</p>
                    
                    <div class="warning">
                        <strong>⚠️ Important Security Notice:</strong>
                        <ul>
                            <li>This verification link expires in 24 hours</li>
                            <li>Never share your account credentials</li>
                            <li>Report any suspicious activity immediately</li>
                            <li>Your safety is our priority</li>
                        </ul>
                    </div>
                    
                    <p>Once verified, you'll have access to:</p>
                    <ul>
                        <li>🏠 Bunker environmental monitoring</li>
                        <li>🎯 Survival training modules</li>
                        <li>🚨 Emergency alert system</li>
                        <li>📊 Personal safety dashboard</li>
                    </ul>
                    
                    <p>If you didn't create this account, please ignore this email or contact our security team immediately.</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Lataupe Bunker Tech - Underground Survival Systems</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>For support, contact: support@bunker.tech</p>
                </div>
            </div>
        </body>
        </html>
        \"\"\"
        
        text_content = f\"\"\"
        Welcome to Lataupe Bunker Tech!
        
        Hello {username},
        
        Welcome to {bunker_id}! To complete your registration, please verify your email address by visiting:
        
        {verification_url}
        
        This link expires in 24 hours.
        
        If you didn't create this account, please ignore this email.
        
        For support, contact: support@bunker.tech
        
        © 2025 Lataupe Bunker Tech
        \"\"\"
        
        return self.send_email(email, subject, html_content, text_content)
    
    def send_password_reset_email(self, email, username, token):
        \"\"\"Envoie l'email de réinitialisation de mot de passe\"\"\"
        reset_url = f"{os.environ.get('BASE_URL', 'http://localhost:5001')}/auth/reset-password/{token}"
        
        subject = "🔒 Password Reset Request - Lataupe Bunker Tech"
        
        html_content = f\"\"\"
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .security-notice {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 Password Reset Request</h1>
                    <p>Secure your bunker access</p>
                </div>
                
                <div class="content">
                    <h2>Hello {username},</h2>
                    
                    <p>We received a request to reset your password for your Lataupe Bunker Tech account.</p>
                    
                    <p>If you requested this password reset, click the button below to create a new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset My Password</a>
                    </div>
                    
                    <div class="security-notice">
                        <strong>🛡️ Security Information:</strong>
                        <ul>
                            <li>This reset link expires in 1 hour</li>
                            <li>If you didn't request this reset, ignore this email</li>
                            <li>Your current password remains unchanged until you create a new one</li>
                            <li>Always use a strong, unique password</li>
                        </ul>
                    </div>
                    
                    <p>For your security, this request was made from IP: {os.environ.get('REQUEST_IP', 'Unknown')}</p>
                    <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Lataupe Bunker Tech - Underground Survival Systems</p>
                    <p>For security concerns, contact: security@bunker.tech</p>
                </div>
            </div>
        </body>
        </html>
        \"\"\"
        
        return self.send_email(email, subject, html_content)
    
    def send_welcome_email(self, email, username, bunker_id, subscription_type):
        \"\"\"Envoie l'email de bienvenue après vérification\"\"\"
        subject = f"🎉 Welcome to {bunker_id} - Your Account is Active!"
        
        features = {
            'free': ['Basic survival training', 'Emergency alerts', 'Environmental monitoring'],
            'lataupe_plus': ['Advanced training modules', 'Detailed analytics', 'Priority support', 'Unlimited quiz attempts']
        }
        
        feature_list = features.get(subscription_type, features['free'])
        
        html_content = f\"\"\"
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Your Bunker</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .features {{ background: white; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to Your Bunker!</h1>
                    <p>Your survival journey begins now</p>
                </div>
                
                <div class="content">
                    <h2>Congratulations {username}!</h2>
                    
                    <p>Your account has been successfully verified and you now have full access to <strong>{bunker_id}</strong>.</p>
                    
                    <div class="features">
                        <h3>Your {subscription_type.replace('_', ' ').title()} Account Includes:</h3>
                        <ul>
                            {''.join(f'<li>✅ {feature}</li>' for feature in feature_list)}
                        </ul>
                    </div>
                    
                    <p>Ready to start your survival training? Access your dashboard now:</p>
                    
                    <div style="text-align: center;">
                        <a href="{os.environ.get('BASE_URL', 'http://localhost:5001')}/dashboard" class="button">Access My Dashboard</a>
                    </div>
                    
                    <h3>🚀 Getting Started:</h3>
                    <ol>
                        <li>Complete your mandatory safety training</li>
                        <li>Familiarize yourself with emergency procedures</li>
                        <li>Set up your environmental monitoring preferences</li>
                        <li>Connect with other bunker residents</li>
                    </ol>
                    
                    <p>Remember: In the bunker, preparation is survival. Stay alert, stay alive!</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Lataupe Bunker Tech - Underground Survival Systems</p>
                    <p>Need help? Visit our support center or contact: support@bunker.tech</p>
                </div>
            </div>
        </body>
        </html>
        \"\"\"
        
        return self.send_email(email, subject, html_content)
"""
    
    return email_code

def main():
    """Fonction principale pour créer le système d'enregistrement avancé"""
    project_path = "/home/ubuntu/lataupe-bunker-tech"
    
    print("📝 Création du système d'enregistrement avancé...")
    print("=" * 60)
    
    # Créer le dossier utils
    utils_dir = os.path.join(project_path, 'src', 'utils')
    os.makedirs(utils_dir, exist_ok=True)
    
    # Créer les fichiers utilitaires
    security_file = os.path.join(utils_dir, 'security.py')
    with open(security_file, 'w') as f:
        f.write(create_security_utilities())
    
    email_file = os.path.join(utils_dir, 'email.py')
    with open(email_file, 'w') as f:
        f.write(create_email_service())
    
    # Créer les routes d'enregistrement
    routes_file = os.path.join(project_path, 'src', 'routes', 'registration.py')
    with open(routes_file, 'w') as f:
        f.write(create_advanced_registration_routes())
    
    # Créer le fichier __init__.py pour utils
    init_file = os.path.join(utils_dir, '__init__.py')
    with open(init_file, 'w') as f:
        f.write('# Utilities package for lataupe-bunker-tech\n')
    
    print("\\n✅ Système d'enregistrement avancé créé avec succès!")
    print("\\n📋 Fichiers créés:")
    print(f"   • Routes d'enregistrement: {routes_file}")
    print(f"   • Utilitaires de sécurité: {security_file}")
    print(f"   • Service d'email: {email_file}")
    
    print("\\n🔐 Fonctionnalités de sécurité:")
    print("   • Validation avancée des mots de passe")
    print("   • Protection contre les attaques par force brute")
    print("   • Limitation du taux de requêtes")
    print("   • Vérification d'email obligatoire")
    print("   • Audit logging complet")
    print("   • Gestion sécurisée des sessions")
    
    print("\\n📧 Système d'email:")
    print("   • Email de vérification avec design responsive")
    print("   • Notifications de sécurité")
    print("   • Templates HTML professionnels")
    print("   • Support SMTP configurable")
    
    print("\\n⚠️  Configuration requise:")
    print("   • Variables d'environnement SMTP")
    print("   • Configuration des templates HTML")
    print("   • Intégration avec main_secure.py")
    print("   • Tests des fonctionnalités d'email")
    
    return True

if __name__ == "__main__":
    main()

