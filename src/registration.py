from flask import Blueprint, request, jsonify, session, render_template, flash, redirect, url_for
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
        
        if not re.search(r'\d', password):
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
    """Page d'enregistrement avancée"""
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
    """Page de connexion avec sécurité avancée"""
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
    """Page de vérification d'email"""
    user = User.query.get_or_404(user_id)
    
    if user.is_verified:
        flash('Email already verified. You can log in now.', 'info')
        return redirect(url_for('registration.login'))
    
    return render_template('auth/verify_email.html', user=user)

@registration_bp.route('/verify-email/<int:user_id>/<token>')
def confirm_email(user_id, token):
    """Confirmer l'email avec le token"""
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
    """Déconnexion sécurisée"""
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
    """Page de profil utilisateur"""
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
    """Vérifier la disponibilité d'un nom d'utilisateur"""
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
    """Vérifier la disponibilité d'un email"""
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
    """Évaluer la force d'un mot de passe"""
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
    
    if re.search(r'\d', password):
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
