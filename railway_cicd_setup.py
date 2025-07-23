#!/usr/bin/env python3
"""
Système complet de déploiement Railway et CI/CD pour lataupe-bunker-tech
Crée tous les fichiers nécessaires pour un déploiement automatisé sur Railway
"""

import os
import json
from pathlib import Path

def create_railway_config():
    """Crée la configuration Railway"""
    
    railway_files = {}
    
    # railway.json - Configuration principale
    railway_files['railway.json'] = """{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.railway"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  },
  "environments": {
    "production": {
      "variables": {
        "FLASK_ENV": "production",
        "PYTHONUNBUFFERED": "1",
        "PORT": "8080"
      }
    },
    "staging": {
      "variables": {
        "FLASK_ENV": "staging",
        "PYTHONUNBUFFERED": "1",
        "PORT": "8080"
      }
    }
  }
}"""
    
    # railway.toml - Configuration avancée
    railway_files['railway.toml'] = """[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile.railway"

[deploy]
numReplicas = 1
sleepApplication = false
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
healthcheckPath = "/health"
healthcheckTimeout = 300

[environments.production]
[environments.production.variables]
FLASK_ENV = "production"
PYTHONUNBUFFERED = "1"
PORT = "8080"

[environments.staging]
[environments.staging.variables]
FLASK_ENV = "staging"
PYTHONUNBUFFERED = "1"
PORT = "8080"
"""
    
    return railway_files

def create_railway_dockerfile():
    """Crée le Dockerfile optimisé pour Railway"""
    
    dockerfile_content = """# Dockerfile optimisé pour Railway
FROM python:3.11-slim-bullseye

# Métadonnées
LABEL maintainer="Lataupe Bunker Tech Team"
LABEL version="2.0.0"
LABEL description="Bunker Management System - Railway Deployment"

# Variables d'environnement Railway
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production
ENV PORT=8080
ENV DEBIAN_FRONTEND=noninteractive

# Créer un utilisateur non-root
RUN groupadd -r railway && useradd -r -g railway -d /app -s /sbin/nologin railway

# Installer les dépendances système
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    libffi-dev \\
    libssl-dev \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# Créer le répertoire de l'application
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements_railway.txt /app/
RUN pip install --no-cache-dir --upgrade pip \\
    && pip install --no-cache-dir -r requirements_railway.txt

# Copier le code de l'application
COPY --chown=railway:railway . /app/

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs /app/uploads /app/static/uploads \\
    && chown -R railway:railway /app \\
    && chmod -R 755 /app

# Script de démarrage Railway
COPY --chown=railway:railway start_railway.sh /app/
RUN chmod +x /app/start_railway.sh

# Passer à l'utilisateur non-root
USER railway

# Exposer le port Railway
EXPOSE 8080

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Commande de démarrage
CMD ["./start_railway.sh"]
"""
    
    return dockerfile_content

def create_railway_requirements():
    """Crée le fichier requirements optimisé pour Railway"""
    
    requirements_content = """# Requirements pour déploiement Railway
# Core Flask
Flask==2.3.3
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-Login==0.6.3
Flask-WTF==1.1.1
Flask-Mail==0.9.1
Flask-Caching==2.1.0
Flask-Limiter==3.5.0

# Base de données
psycopg2-binary==2.9.7
SQLAlchemy==2.0.21
alembic==1.12.0

# Cache et sessions
redis==5.0.0
Flask-Session==0.5.0

# Sécurité
cryptography==41.0.4
bcrypt==4.0.1
PyJWT==2.8.0
bleach==6.0.0
markupsafe==2.1.3

# Validation et formulaires
WTForms==3.0.1
email-validator==2.0.0
validators==0.22.0

# HTTP et API
requests==2.31.0
urllib3==2.0.4
gunicorn==21.2.0

# Monitoring et logging
prometheus-client==0.17.1
sentry-sdk[flask]==1.32.0

# Utilitaires
python-dotenv==1.0.0
click==8.1.7
itsdangerous==2.1.2
Jinja2==3.1.2
Werkzeug==2.3.7

# Date et temps
python-dateutil==2.8.2
pytz==2023.3

# JSON et sérialisation
marshmallow==3.20.1
marshmallow-sqlalchemy==0.29.0

# Images et médias
Pillow==10.0.0

# Développement et tests (optionnel en production)
pytest==7.4.2
pytest-flask==1.2.0
coverage==7.3.2
"""
    
    return requirements_content

def create_railway_startup_script():
    """Crée le script de démarrage Railway"""
    
    startup_script = """#!/bin/bash
# Script de démarrage pour Railway

set -e

echo "🚀 Démarrage Lataupe Bunker Tech sur Railway"
echo "============================================="

# Variables d'environnement
export FLASK_APP=main_railway.py
export FLASK_ENV=${FLASK_ENV:-production}
export PORT=${PORT:-8080}

# Couleurs pour les logs
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier les variables d'environnement critiques
if [ -z "$DATABASE_URL" ]; then
    log_warn "DATABASE_URL non définie, utilisation de SQLite par défaut"
    export DATABASE_URL="sqlite:///bunker.db"
fi

if [ -z "$SECRET_KEY" ]; then
    log_warn "SECRET_KEY non définie, génération automatique"
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi

# Créer les répertoires nécessaires
log_info "Création des répertoires..."
mkdir -p logs uploads static/uploads

# Initialiser la base de données
log_info "Initialisation de la base de données..."
if [ "$FLASK_ENV" = "production" ]; then
    python3 -c "
from main_railway import app, db
with app.app_context():
    db.create_all()
    print('Base de données initialisée')
"
fi

# Vérifier la santé de l'application
log_info "Vérification de l'application..."
python3 -c "
import sys
try:
    from main_railway import app
    print('Application chargée avec succès')
except Exception as e:
    print(f'Erreur lors du chargement: {e}')
    sys.exit(1)
"

# Démarrer l'application avec Gunicorn
log_info "Démarrage de l'application sur le port $PORT..."

if [ "$FLASK_ENV" = "development" ]; then
    # Mode développement avec Flask dev server
    python3 main_railway.py
else
    # Mode production avec Gunicorn
    exec gunicorn \\
        --bind 0.0.0.0:$PORT \\
        --workers 2 \\
        --threads 4 \\
        --worker-class gthread \\
        --worker-connections 1000 \\
        --max-requests 1000 \\
        --max-requests-jitter 100 \\
        --timeout 30 \\
        --keep-alive 2 \\
        --log-level info \\
        --access-logfile - \\
        --error-logfile - \\
        --capture-output \\
        --enable-stdio-inheritance \\
        main_railway:app
fi
"""
    
    return startup_script

def create_railway_main_app():
    """Crée l'application principale pour Railway"""
    
    main_app_content = """#!/usr/bin/env python3
\"\"\"
Application principale pour déploiement Railway
Version optimisée pour la production sur Railway
\"\"\"

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
    \"\"\"Factory pour créer l'application Flask\"\"\"
    
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
        \"\"\"Page d'accueil\"\"\"
        return render_template('dashboard_mobile.html')
    
    @app.route('/health')
    def health():
        \"\"\"Endpoint de santé pour Railway\"\"\"
        try:
            # Vérifier la base de données
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        # Vérifier le cache
        try:
            cache.set('health_check', 'ok', timeout=10)
            cache_status = 'healthy' if cache.get('health_check') == 'ok' else 'unhealthy'
        except Exception as e:
            cache_status = f'unhealthy: {str(e)}'
        
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
        \"\"\"Dashboard principal\"\"\"
        return render_template('dashboard_mobile.html')
    
    @app.route('/quiz')
    def quiz():
        \"\"\"Page quiz\"\"\"
        return render_template('quiz_dashboard.html')
    
    @app.route('/api/metrics')
    @limiter.limit("30 per minute")
    def api_metrics():
        \"\"\"API pour les métriques du bunker\"\"\"
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
        \"\"\"API pour les alertes\"\"\"
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
                'message': 'Niveau d\\'eau à 75%',
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
"""
    
    return main_app_content

def create_github_actions():
    """Crée les workflows GitHub Actions pour CI/CD"""
    
    workflows = {}
    
    # Workflow principal CI/CD
    workflows['.github/workflows/railway-deploy.yml'] = """name: Deploy to Railway

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_bunker
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Cache Python dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements_railway.txt
        pip install pytest pytest-flask pytest-cov flake8 black isort
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Format check with black
      run: black --check .
    
    - name: Import sort check with isort
      run: isort --check-only .
    
    - name: Test with pytest
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_bunker
        REDIS_URL: redis://localhost:6379/0
        SECRET_KEY: test-secret-key
        FLASK_ENV: testing
      run: |
        pytest --cov=. --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
    
    - name: Security scan with bandit
      run: |
        pip install bandit
        bandit -r . -x tests/
    
    - name: Dependency check
      run: |
        pip install safety
        safety check

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Build Docker image
      run: |
        docker build -f Dockerfile.railway -t lataupe-bunker-tech:latest .
    
    - name: Test Docker image
      run: |
        docker run --rm -d --name test-app -p 8080:8080 -e SECRET_KEY=test lataupe-bunker-tech:latest
        sleep 30
        curl -f http://localhost:8080/health || exit 1
        docker stop test-app

  deploy-staging:
    needs: [test, build]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Deploy to Railway (Staging)
      uses: railwayapp/railway-deploy@v1
      with:
        railway-token: ${{ secrets.RAILWAY_TOKEN_STAGING }}
        service: lataupe-bunker-staging
        environment: staging
    
    - name: Health check staging
      run: |
        sleep 60
        curl -f ${{ secrets.STAGING_URL }}/health || exit 1

  deploy-production:
    needs: [test, build]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Deploy to Railway (Production)
      uses: railwayapp/railway-deploy@v1
      with:
        railway-token: ${{ secrets.RAILWAY_TOKEN_PRODUCTION }}
        service: lataupe-bunker-production
        environment: production
    
    - name: Health check production
      run: |
        sleep 60
        curl -f ${{ secrets.PRODUCTION_URL }}/health || exit 1
    
    - name: Notify deployment success
      uses: 8398a7/action-slack@v3
      with:
        status: success
        channel: '#deployments'
        text: '🚀 Lataupe Bunker Tech deployed to production successfully!'
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      if: success()
    
    - name: Notify deployment failure
      uses: 8398a7/action-slack@v3
      with:
        status: failure
        channel: '#deployments'
        text: '❌ Lataupe Bunker Tech deployment to production failed!'
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      if: failure()

  lighthouse:
    needs: deploy-production
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Run Lighthouse CI
      uses: treosh/lighthouse-ci-action@v10
      with:
        urls: |
          ${{ secrets.PRODUCTION_URL }}
          ${{ secrets.PRODUCTION_URL }}/dashboard
          ${{ secrets.PRODUCTION_URL }}/quiz
        configPath: './lighthouserc.json'
        uploadArtifacts: true
        temporaryPublicStorage: true
"""
    
    # Workflow de tests de performance
    workflows['.github/workflows/performance-tests.yml'] = """name: Performance Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Tous les jours à 2h du matin
  workflow_dispatch:

jobs:
  performance-test:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
    
    - name: Install k6
      run: |
        sudo gpg -k
        sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6
    
    - name: Run load tests
      run: |
        k6 run tests/performance/load-test.js
    
    - name: Run stress tests
      run: |
        k6 run tests/performance/stress-test.js
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: performance-results
        path: results/
"""
    
    # Workflow de sécurité
    workflows['.github/workflows/security-scan.yml'] = """name: Security Scan

on:
  push:
    branches: [ main, develop ]
  schedule:
    - cron: '0 6 * * 1'  # Tous les lundis à 6h du matin

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
    
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/python@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high
    
    - name: OWASP ZAP Baseline Scan
      uses: zaproxy/action-baseline@v0.7.0
      with:
        target: ${{ secrets.PRODUCTION_URL }}
        rules_file_name: '.zap/rules.tsv'
        cmd_options: '-a'
"""
    
    return workflows

def create_railway_monitoring():
    """Crée les fichiers de monitoring pour Railway"""
    
    monitoring_files = {}
    
    # Configuration Lighthouse
    monitoring_files['lighthouserc.json'] = """{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "settings": {
        "chromeFlags": "--no-sandbox --disable-dev-shm-usage"
      }
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:accessibility": ["error", {"minScore": 0.9}],
        "categories:best-practices": ["error", {"minScore": 0.9}],
        "categories:seo": ["error", {"minScore": 0.9}],
        "categories:pwa": ["error", {"minScore": 0.9}]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}"""
    
    # Tests de charge K6
    monitoring_files['tests/performance/load-test.js'] = """import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Montée progressive
    { duration: '5m', target: 10 }, // Maintien
    { duration: '2m', target: 20 }, // Pic de charge
    { duration: '5m', target: 20 }, // Maintien du pic
    { duration: '2m', target: 0 },  // Descente
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% des requêtes < 500ms
    http_req_failed: ['rate<0.1'],    // Taux d'erreur < 10%
    errors: ['rate<0.1'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://your-app.railway.app';

export default function() {
  // Test de la page d'accueil
  let response = http.get(`${BASE_URL}/`);
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  }) || errorRate.add(1);

  sleep(1);

  // Test du dashboard
  response = http.get(`${BASE_URL}/dashboard`);
  check(response, {
    'dashboard status is 200': (r) => r.status === 200,
    'dashboard response time < 1000ms': (r) => r.timings.duration < 1000,
  }) || errorRate.add(1);

  sleep(1);

  // Test de l'API metrics
  response = http.get(`${BASE_URL}/api/metrics`);
  check(response, {
    'api status is 200': (r) => r.status === 200,
    'api response time < 200ms': (r) => r.timings.duration < 200,
    'api returns json': (r) => r.headers['Content-Type'].includes('application/json'),
  }) || errorRate.add(1);

  sleep(2);
}"""
    
    # Tests de stress K6
    monitoring_files['tests/performance/stress-test.js'] = """import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 50 },   // Montée rapide
    { duration: '3m', target: 100 },  // Stress test
    { duration: '1m', target: 200 },  // Pic de stress
    { duration: '2m', target: 0 },    // Récupération
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // Plus permissif en stress
    http_req_failed: ['rate<0.2'],     // 20% d'erreur acceptable
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://your-app.railway.app';

export default function() {
  let response = http.get(`${BASE_URL}/health`);
  check(response, {
    'health check status': (r) => r.status === 200,
  });

  sleep(0.5);
}"""
    
    # Configuration de monitoring
    monitoring_files['monitoring/railway-monitor.py'] = """#!/usr/bin/env python3
\"\"\"
Script de monitoring pour Railway
Vérifie la santé de l'application et envoie des alertes
\"\"\"

import requests
import time
import os
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class RailwayMonitor:
    def __init__(self):
        self.base_url = os.environ.get('RAILWAY_APP_URL', 'https://your-app.railway.app')
        self.alert_email = os.environ.get('ALERT_EMAIL')
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_username = os.environ.get('SMTP_USERNAME')
        self.smtp_password = os.environ.get('SMTP_PASSWORD')
        
        self.checks = [
            {'name': 'Health Check', 'url': '/health', 'timeout': 10},
            {'name': 'Dashboard', 'url': '/dashboard', 'timeout': 15},
            {'name': 'API Metrics', 'url': '/api/metrics', 'timeout': 5},
        ]
    
    def check_endpoint(self, check):
        \"\"\"Vérifier un endpoint spécifique\"\"\"
        try:
            url = f"{self.base_url}{check['url']}"
            response = requests.get(url, timeout=check['timeout'])
            
            return {
                'name': check['name'],
                'url': url,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'success': response.status_code == 200,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'name': check['name'],
                'url': f"{self.base_url}{check['url']}",
                'error': str(e),
                'success': False,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def run_checks(self):
        \"\"\"Exécuter tous les checks\"\"\"
        results = []
        for check in self.checks:
            result = self.check_endpoint(check)
            results.append(result)
            print(f"✅ {result['name']}: {'OK' if result['success'] else 'FAILED'}")
        
        return results
    
    def send_alert(self, failed_checks):
        \"\"\"Envoyer une alerte par email\"\"\"
        if not self.alert_email or not failed_checks:
            return
        
        subject = f"🚨 Railway App Alert - {len(failed_checks)} checks failed"
        
        body = f\"\"\"
        Railway Application Health Check Alert
        
        Time: {datetime.utcnow().isoformat()}
        Application: {self.base_url}
        
        Failed Checks:
        \"\"\"
        
        for check in failed_checks:
            body += f\"\"\"
        - {check['name']}: {check.get('error', f"Status {check.get('status_code', 'Unknown')}")}
          URL: {check['url']}
        \"\"\"
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.alert_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Alert sent to {self.alert_email}")
        except Exception as e:
            print(f"❌ Failed to send alert: {e}")
    
    def monitor(self, interval=300):
        \"\"\"Monitoring continu\"\"\"
        print(f"🔍 Starting Railway monitoring for {self.base_url}")
        print(f"⏰ Check interval: {interval} seconds")
        
        while True:
            try:
                results = self.run_checks()
                failed_checks = [r for r in results if not r['success']]
                
                if failed_checks:
                    print(f"❌ {len(failed_checks)} checks failed")
                    self.send_alert(failed_checks)
                else:
                    print("✅ All checks passed")
                
                # Sauvegarder les résultats
                with open('monitoring_results.json', 'w') as f:
                    json.dump({
                        'timestamp': datetime.utcnow().isoformat(),
                        'results': results
                    }, f, indent=2)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\\n🛑 Monitoring stopped")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(60)  # Attendre 1 minute avant de réessayer

if __name__ == '__main__':
    monitor = RailwayMonitor()
    monitor.monitor()
"""
    
    return monitoring_files

def main():
    """Fonction principale pour créer le système Railway et CI/CD"""
    project_path = "/home/ubuntu/lataupe-bunker-tech"
    
    print("🚂 Création du système Railway et CI/CD...")
    print("=" * 50)
    
    # Créer les dossiers nécessaires
    github_dir = os.path.join(project_path, '.github', 'workflows')
    tests_dir = os.path.join(project_path, 'tests', 'performance')
    monitoring_dir = os.path.join(project_path, 'monitoring')
    
    for directory in [github_dir, tests_dir, monitoring_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # Créer la configuration Railway
    railway_config = create_railway_config()
    for filename, content in railway_config.items():
        filepath = os.path.join(project_path, filename)
        with open(filepath, 'w') as f:
            f.write(content)
    
    # Créer le Dockerfile Railway
    dockerfile_railway = os.path.join(project_path, 'Dockerfile.railway')
    with open(dockerfile_railway, 'w') as f:
        f.write(create_railway_dockerfile())
    
    # Créer les requirements Railway
    requirements_railway = os.path.join(project_path, 'requirements_railway.txt')
    with open(requirements_railway, 'w') as f:
        f.write(create_railway_requirements())
    
    # Créer le script de démarrage
    startup_script = os.path.join(project_path, 'start_railway.sh')
    with open(startup_script, 'w') as f:
        f.write(create_railway_startup_script())
    os.chmod(startup_script, 0o755)
    
    # Créer l'application principale Railway
    main_app = os.path.join(project_path, 'main_railway.py')
    with open(main_app, 'w') as f:
        f.write(create_railway_main_app())
    
    # Créer les workflows GitHub Actions
    workflows = create_github_actions()
    for filepath, content in workflows.items():
        full_path = os.path.join(project_path, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    # Créer les fichiers de monitoring
    monitoring_files = create_railway_monitoring()
    for filepath, content in monitoring_files.items():
        full_path = os.path.join(project_path, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    print("\\n✅ Système Railway et CI/CD créé avec succès!")
    print("\\n📋 Fichiers créés:")
    print(f"   • Configuration Railway: {len(railway_config)} fichiers")
    print(f"   • Dockerfile Railway: {dockerfile_railway}")
    print(f"   • Requirements Railway: {requirements_railway}")
    print(f"   • Script de démarrage: {startup_script}")
    print(f"   • Application principale: {main_app}")
    print(f"   • Workflows GitHub: {len(workflows)} fichiers")
    print(f"   • Fichiers de monitoring: {len(monitoring_files)} fichiers")
    
    print("\\n🚂 Fonctionnalités Railway:")
    print("   • Déploiement automatique depuis GitHub")
    print("   • Configuration multi-environnement (staging/prod)")
    print("   • Health checks intégrés")
    print("   • Scaling automatique")
    print("   • Monitoring et alertes")
    
    print("\\n🔄 Pipeline CI/CD:")
    print("   • Tests automatisés (pytest, flake8, black)")
    print("   • Scans de sécurité (Trivy, Snyk, OWASP ZAP)")
    print("   • Tests de performance (K6, Lighthouse)")
    print("   • Déploiement automatique staging/production")
    print("   • Notifications Slack")
    
    print("\\n📊 Monitoring:")
    print("   • Health checks automatiques")
    print("   • Tests de performance continus")
    print("   • Alertes par email")
    print("   • Métriques Lighthouse")
    print("   • Logs centralisés")
    
    print("\\n🚀 Déploiement Railway:")
    print("   1. Connecter le repository GitHub à Railway")
    print("   2. Configurer les variables d'environnement")
    print("   3. Déployer automatiquement sur push")
    print("   4. Surveiller avec les health checks")
    
    return True

if __name__ == "__main__":
    main()

