#!/usr/bin/env python3
"""
Scripts d'automatisation pour le déploiement Railway
Facilite la configuration et le déploiement de lataupe-bunker-tech sur Railway
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def create_railway_cli_scripts():
    """Crée les scripts CLI pour Railway"""
    
    scripts = {}
    
    # Script de configuration Railway
    scripts['scripts/railway-setup.sh'] = """#!/bin/bash
# Script de configuration Railway pour lataupe-bunker-tech

set -e

# Couleurs pour les logs
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

echo "🚂 Configuration Railway pour Lataupe Bunker Tech"
echo "================================================="

# Vérifier si Railway CLI est installé
if ! command -v railway &> /dev/null; then
    log_error "Railway CLI n'est pas installé"
    log_info "Installation de Railway CLI..."
    
    # Installer Railway CLI
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install railway
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://railway.app/install.sh | sh
    else
        log_error "OS non supporté. Installez Railway CLI manuellement: https://docs.railway.app/develop/cli"
        exit 1
    fi
fi

# Vérifier l'authentification
log_step "Vérification de l'authentification Railway..."
if ! railway whoami &> /dev/null; then
    log_warn "Non authentifié sur Railway"
    log_info "Connexion à Railway..."
    railway login
fi

log_info "Utilisateur connecté: $(railway whoami)"

# Créer le projet Railway
log_step "Création du projet Railway..."
read -p "Nom du projet Railway (lataupe-bunker-tech): " PROJECT_NAME
PROJECT_NAME=${PROJECT_NAME:-lataupe-bunker-tech}

# Initialiser le projet
if railway status &> /dev/null; then
    log_warn "Projet Railway déjà initialisé"
else
    railway init --name "$PROJECT_NAME"
fi

# Configurer les variables d'environnement
log_step "Configuration des variables d'environnement..."

# Variables de base
railway variables set FLASK_ENV=production
railway variables set PYTHONUNBUFFERED=1
railway variables set PORT=8080

# Générer une clé secrète
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
railway variables set SECRET_KEY="$SECRET_KEY"

# Configurer la base de données PostgreSQL
log_step "Configuration de la base de données..."
railway add postgresql
log_info "Base de données PostgreSQL ajoutée"

# Configurer Redis (optionnel)
read -p "Ajouter Redis pour le cache? (y/N): " ADD_REDIS
if [[ $ADD_REDIS =~ ^[Yy]$ ]]; then
    railway add redis
    log_info "Redis ajouté pour le cache"
fi

# Configurer les domaines
log_step "Configuration des domaines..."
railway domain

# Afficher les informations du projet
log_step "Informations du projet:"
railway status
railway variables

log_info "✅ Configuration Railway terminée!"
log_info "🚀 Déployez avec: railway up"
"""
    
    # Script de déploiement
    scripts['scripts/railway-deploy.sh'] = """#!/bin/bash
# Script de déploiement Railway pour lataupe-bunker-tech

set -e

# Couleurs
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
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

echo "🚀 Déploiement Railway - Lataupe Bunker Tech"
echo "============================================="

# Vérifier les prérequis
if ! command -v railway &> /dev/null; then
    log_error "Railway CLI non installé. Exécutez ./scripts/railway-setup.sh"
    exit 1
fi

if ! railway status &> /dev/null; then
    log_error "Projet Railway non initialisé. Exécutez ./scripts/railway-setup.sh"
    exit 1
fi

# Vérifier les fichiers nécessaires
REQUIRED_FILES=(
    "Dockerfile.railway"
    "requirements_railway.txt"
    "main_railway.py"
    "start_railway.sh"
    "railway.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        log_error "Fichier manquant: $file"
        exit 1
    fi
done

log_info "✅ Tous les fichiers requis sont présents"

# Sélectionner l'environnement
echo "Environnements disponibles:"
echo "1) production"
echo "2) staging"
read -p "Sélectionnez l'environnement (1-2): " ENV_CHOICE

case $ENV_CHOICE in
    1)
        ENVIRONMENT="production"
        ;;
    2)
        ENVIRONMENT="staging"
        ;;
    *)
        log_error "Choix invalide"
        exit 1
        ;;
esac

log_info "Déploiement vers l'environnement: $ENVIRONMENT"

# Basculer vers l'environnement
if [[ "$ENVIRONMENT" != "production" ]]; then
    railway environment $ENVIRONMENT
fi

# Vérifier les variables d'environnement
log_info "Vérification des variables d'environnement..."
railway variables

# Confirmer le déploiement
read -p "Confirmer le déploiement vers $ENVIRONMENT? (y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    log_warn "Déploiement annulé"
    exit 0
fi

# Déployer
log_info "🚀 Déploiement en cours..."
railway up --detach

# Attendre le déploiement
log_info "⏳ Attente du déploiement..."
sleep 30

# Vérifier le déploiement
log_info "🔍 Vérification du déploiement..."
DOMAIN=$(railway domain | grep -o 'https://[^[:space:]]*' | head -1)

if [[ -n "$DOMAIN" ]]; then
    log_info "🌍 Application déployée: $DOMAIN"
    
    # Test de santé
    log_info "🏥 Test de santé..."
    if curl -f "$DOMAIN/health" > /dev/null 2>&1; then
        log_info "✅ Application en bonne santé!"
        log_info "🎉 Déploiement réussi!"
        
        # Afficher les logs récents
        log_info "📋 Logs récents:"
        railway logs --tail 20
    else
        log_error "❌ Test de santé échoué"
        log_error "📋 Logs d'erreur:"
        railway logs --tail 50
        exit 1
    fi
else
    log_error "❌ Impossible de récupérer le domaine"
    exit 1
fi

log_info "✅ Déploiement terminé avec succès!"
"""
    
    # Script de monitoring
    scripts['scripts/railway-monitor.sh'] = """#!/bin/bash
# Script de monitoring Railway pour lataupe-bunker-tech

set -e

GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
BLUE='\\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

echo "📊 Monitoring Railway - Lataupe Bunker Tech"
echo "==========================================="

# Vérifier Railway CLI
if ! command -v railway &> /dev/null; then
    log_error "Railway CLI non installé"
    exit 1
fi

# Menu de monitoring
while true; do
    echo ""
    echo "Options de monitoring:"
    echo "1) Status du service"
    echo "2) Logs en temps réel"
    echo "3) Métriques de performance"
    echo "4) Variables d'environnement"
    echo "5) Test de santé"
    echo "6) Redémarrer le service"
    echo "7) Quitter"
    
    read -p "Sélectionnez une option (1-7): " CHOICE
    
    case $CHOICE in
        1)
            log_step "Status du service..."
            railway status
            ;;
        2)
            log_step "Logs en temps réel (Ctrl+C pour arrêter)..."
            railway logs
            ;;
        3)
            log_step "Métriques de performance..."
            railway metrics
            ;;
        4)
            log_step "Variables d'environnement..."
            railway variables
            ;;
        5)
            log_step "Test de santé..."
            DOMAIN=$(railway domain | grep -o 'https://[^[:space:]]*' | head -1)
            if [[ -n "$DOMAIN" ]]; then
                if curl -f "$DOMAIN/health" > /dev/null 2>&1; then
                    log_info "✅ Application en bonne santé!"
                    curl -s "$DOMAIN/health" | python3 -m json.tool
                else
                    log_error "❌ Test de santé échoué"
                fi
            else
                log_error "❌ Impossible de récupérer le domaine"
            fi
            ;;
        6)
            log_step "Redémarrage du service..."
            read -p "Confirmer le redémarrage? (y/N): " CONFIRM
            if [[ $CONFIRM =~ ^[Yy]$ ]]; then
                railway restart
                log_info "✅ Service redémarré"
            fi
            ;;
        7)
            log_info "Au revoir!"
            exit 0
            ;;
        *)
            log_error "Option invalide"
            ;;
    esac
done
"""
    
    # Script de rollback
    scripts['scripts/railway-rollback.sh'] = """#!/bin/bash
# Script de rollback Railway pour lataupe-bunker-tech

set -e

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

echo "🔄 Rollback Railway - Lataupe Bunker Tech"
echo "========================================="

# Vérifier Railway CLI
if ! command -v railway &> /dev/null; then
    log_error "Railway CLI non installé"
    exit 1
fi

# Lister les déploiements récents
log_info "Déploiements récents:"
railway deployments

# Demander le déploiement cible
read -p "ID du déploiement pour rollback: " DEPLOYMENT_ID

if [[ -z "$DEPLOYMENT_ID" ]]; then
    log_error "ID de déploiement requis"
    exit 1
fi

# Confirmer le rollback
log_warn "⚠️  ATTENTION: Cette action va restaurer l'application à un état précédent"
read -p "Confirmer le rollback vers $DEPLOYMENT_ID? (y/N): " CONFIRM

if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    log_info "Rollback annulé"
    exit 0
fi

# Effectuer le rollback
log_info "🔄 Rollback en cours..."
railway rollback $DEPLOYMENT_ID

# Vérifier le rollback
log_info "⏳ Vérification du rollback..."
sleep 30

DOMAIN=$(railway domain | grep -o 'https://[^[:space:]]*' | head -1)
if [[ -n "$DOMAIN" ]]; then
    if curl -f "$DOMAIN/health" > /dev/null 2>&1; then
        log_info "✅ Rollback réussi!"
        log_info "🌍 Application: $DOMAIN"
    else
        log_error "❌ Rollback échoué - Test de santé KO"
        railway logs --tail 20
    fi
else
    log_error "❌ Impossible de vérifier le rollback"
fi
"""
    
    return scripts

def create_railway_documentation():
    """Crée la documentation Railway"""
    
    docs = {}
    
    # Guide de déploiement Railway
    docs['docs/RAILWAY_DEPLOYMENT.md'] = """# Guide de Déploiement Railway - Lataupe Bunker Tech

## Vue d'ensemble

Ce guide détaille le processus de déploiement de l'application Lataupe Bunker Tech sur Railway, une plateforme cloud moderne pour le déploiement d'applications.

## Prérequis

### 1. Compte Railway
- Créer un compte sur [railway.app](https://railway.app)
- Installer Railway CLI: `curl -fsSL https://railway.app/install.sh | sh`
- Se connecter: `railway login`

### 2. Repository GitHub
- Code source sur GitHub
- Accès en écriture au repository
- Secrets configurés pour CI/CD

### 3. Dépendances locales
- Python 3.11+
- Docker (optionnel)
- Git

## Configuration Initiale

### 1. Initialisation du Projet

```bash
# Cloner le repository
git clone https://github.com/kvnbbg/lataupe-bunker-tech.git
cd lataupe-bunker-tech

# Exécuter le script de configuration
chmod +x scripts/railway-setup.sh
./scripts/railway-setup.sh
```

### 2. Variables d'Environnement

Les variables suivantes sont configurées automatiquement:

```bash
# Variables de base
FLASK_ENV=production
PYTHONUNBUFFERED=1
PORT=8080
SECRET_KEY=<généré automatiquement>

# Base de données (ajoutée automatiquement)
DATABASE_URL=<PostgreSQL URL>

# Cache (optionnel)
REDIS_URL=<Redis URL>
```

### 3. Services Additionnels

#### PostgreSQL (Requis)
```bash
railway add postgresql
```

#### Redis (Optionnel)
```bash
railway add redis
```

## Déploiement

### 1. Déploiement Manuel

```bash
# Déploiement simple
railway up

# Déploiement avec script automatisé
chmod +x scripts/railway-deploy.sh
./scripts/railway-deploy.sh
```

### 2. Déploiement Automatique (CI/CD)

Le déploiement automatique est configuré via GitHub Actions:

- **Push sur `develop`** → Déploiement staging
- **Push sur `main`** → Déploiement production

#### Configuration des Secrets GitHub

```bash
# Secrets requis dans GitHub
RAILWAY_TOKEN_STAGING=<token pour staging>
RAILWAY_TOKEN_PRODUCTION=<token pour production>
STAGING_URL=<URL staging>
PRODUCTION_URL=<URL production>
SLACK_WEBHOOK_URL=<webhook pour notifications>
```

### 3. Environnements

#### Staging
- Branch: `develop`
- URL: `https://lataupe-bunker-staging.railway.app`
- Base de données: PostgreSQL staging
- Monitoring: Basique

#### Production
- Branch: `main`
- URL: `https://lataupe-bunker.railway.app`
- Base de données: PostgreSQL production
- Monitoring: Complet avec alertes

## Monitoring et Maintenance

### 1. Health Checks

L'application expose un endpoint de santé:

```bash
curl https://your-app.railway.app/health
```

Réponse attendue:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "2.0.0",
  "environment": "production",
  "database": "healthy",
  "cache": "healthy",
  "port": 8080
}
```

### 2. Logs

```bash
# Logs en temps réel
railway logs

# Logs récents
railway logs --tail 100

# Logs avec filtre
railway logs --filter "ERROR"
```

### 3. Métriques

```bash
# Métriques Railway
railway metrics

# Status du service
railway status
```

### 4. Monitoring Automatisé

Script de monitoring continu:

```bash
chmod +x scripts/railway-monitor.sh
./scripts/railway-monitor.sh
```

## Gestion des Incidents

### 1. Rollback

En cas de problème après déploiement:

```bash
# Rollback automatisé
chmod +x scripts/railway-rollback.sh
./scripts/railway-rollback.sh

# Rollback manuel
railway deployments  # Lister les déploiements
railway rollback <deployment-id>
```

### 2. Redémarrage

```bash
# Redémarrage du service
railway restart

# Redémarrage avec logs
railway restart && railway logs
```

### 3. Debug

```bash
# Connexion au container
railway shell

# Variables d'environnement
railway variables

# Status détaillé
railway status --json
```

## Optimisations Performance

### 1. Configuration Gunicorn

Le fichier `start_railway.sh` configure Gunicorn pour la production:

```bash
gunicorn \\
  --bind 0.0.0.0:$PORT \\
  --workers 2 \\
  --threads 4 \\
  --worker-class gthread \\
  --timeout 30 \\
  --keep-alive 2 \\
  main_railway:app
```

### 2. Mise en Cache

- Redis pour le cache applicatif
- Cache HTTP avec headers appropriés
- Cache statique avec CDN

### 3. Base de Données

- Connection pooling configuré
- Index optimisés
- Requêtes optimisées

## Sécurité

### 1. Variables Sensibles

Toutes les variables sensibles sont stockées dans Railway:

```bash
# Ajouter une variable sensible
railway variables set API_KEY=<valeur>

# Lister les variables (valeurs masquées)
railway variables
```

### 2. HTTPS

- HTTPS automatique avec certificats Let's Encrypt
- Redirection HTTP → HTTPS
- Headers de sécurité configurés

### 3. Authentification

- Tokens Railway sécurisés
- Accès basé sur les rôles
- Audit logs disponibles

## Troubleshooting

### Problèmes Courants

#### 1. Échec de Déploiement

```bash
# Vérifier les logs de build
railway logs --deployment <deployment-id>

# Vérifier la configuration
railway status
```

#### 2. Application Inaccessible

```bash
# Vérifier le health check
curl https://your-app.railway.app/health

# Vérifier les logs
railway logs --tail 50
```

#### 3. Base de Données Inaccessible

```bash
# Vérifier la connexion DB
railway variables | grep DATABASE_URL

# Tester la connexion
railway shell
python3 -c "import psycopg2; print('DB OK')"
```

### Support

- Documentation Railway: [docs.railway.app](https://docs.railway.app)
- Support Railway: [help.railway.app](https://help.railway.app)
- Community Discord: [discord.gg/railway](https://discord.gg/railway)

## Commandes de Référence

```bash
# Configuration
railway login                    # Connexion
railway init                     # Initialiser projet
railway link                     # Lier projet existant

# Déploiement
railway up                       # Déployer
railway up --detach             # Déployer en arrière-plan

# Monitoring
railway status                   # Status du service
railway logs                     # Logs en temps réel
railway logs --tail 100         # Logs récents
railway metrics                  # Métriques

# Gestion
railway restart                  # Redémarrer
railway shell                    # Accès shell
railway variables                # Variables d'env

# Domaines
railway domain                   # Gérer domaines
railway domain add example.com  # Ajouter domaine custom

# Services
railway add postgresql           # Ajouter PostgreSQL
railway add redis               # Ajouter Redis
```

Ce guide couvre tous les aspects du déploiement Railway pour Lataupe Bunker Tech. Pour des questions spécifiques, consultez la documentation Railway ou contactez l'équipe de développement.
"""
    
    # Guide CI/CD
    docs['docs/CICD_GUIDE.md'] = """# Guide CI/CD - Lataupe Bunker Tech

## Vue d'ensemble

Ce guide détaille le pipeline CI/CD complet pour l'application Lataupe Bunker Tech, utilisant GitHub Actions pour l'intégration continue et Railway pour le déploiement continu.

## Architecture CI/CD

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Developer     │    │   GitHub Actions │    │    Railway      │
│                 │    │                  │    │                 │
│ git push        │───▶│ 1. Tests         │───▶│ 1. Staging      │
│ ├─ develop      │    │ 2. Security      │    │ 2. Production   │
│ └─ main         │    │ 3. Performance   │    │ 3. Monitoring   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Workflows GitHub Actions

### 1. Workflow Principal: `railway-deploy.yml`

Déclenché sur:
- Push sur `main` (production)
- Push sur `develop` (staging)
- Pull requests vers `main`

#### Étapes:

1. **Tests** (`test` job)
   - Tests unitaires avec pytest
   - Tests d'intégration
   - Couverture de code
   - Lint avec flake8, black, isort
   - Scan de sécurité avec bandit

2. **Build** (`build` job)
   - Construction de l'image Docker
   - Tests de l'image
   - Validation du health check

3. **Déploiement Staging** (`deploy-staging` job)
   - Déploiement automatique sur `develop`
   - Tests de santé post-déploiement
   - Validation des fonctionnalités

4. **Déploiement Production** (`deploy-production` job)
   - Déploiement automatique sur `main`
   - Tests de santé post-déploiement
   - Notifications Slack

5. **Tests Lighthouse** (`lighthouse` job)
   - Tests de performance
   - Audit d'accessibilité
   - Validation PWA

### 2. Workflow Performance: `performance-tests.yml`

Déclenché:
- Quotidiennement à 2h du matin
- Manuellement via workflow_dispatch

#### Tests inclus:
- Tests de charge avec K6
- Tests de stress
- Métriques de performance
- Rapports automatisés

### 3. Workflow Sécurité: `security-scan.yml`

Déclenché:
- Push sur branches principales
- Hebdomadairement le lundi

#### Scans inclus:
- Trivy (vulnérabilités containers)
- Snyk (dépendances)
- OWASP ZAP (sécurité web)
- Bandit (code Python)

## Configuration des Secrets

### Secrets GitHub Requis

```bash
# Railway
RAILWAY_TOKEN_STAGING=<token-staging>
RAILWAY_TOKEN_PRODUCTION=<token-production>

# URLs
STAGING_URL=https://lataupe-bunker-staging.railway.app
PRODUCTION_URL=https://lataupe-bunker.railway.app

# Notifications
SLACK_WEBHOOK_URL=<webhook-url>

# Sécurité
SNYK_TOKEN=<snyk-token>
CODECOV_TOKEN=<codecov-token>
```

### Configuration des Tokens Railway

1. **Obtenir les tokens:**
   ```bash
   railway login
   railway tokens create
   ```

2. **Configurer dans GitHub:**
   - Settings → Secrets and variables → Actions
   - Ajouter chaque secret individuellement

## Environnements

### Staging
- **Branch:** `develop`
- **URL:** https://lataupe-bunker-staging.railway.app
- **Base de données:** PostgreSQL staging
- **Déploiement:** Automatique sur push
- **Tests:** Complets mais non-bloquants

### Production
- **Branch:** `main`
- **URL:** https://lataupe-bunker.railway.app
- **Base de données:** PostgreSQL production
- **Déploiement:** Automatique après validation
- **Tests:** Complets et bloquants

## Tests Automatisés

### 1. Tests Unitaires

```python
# Exemple de test
def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
```

Configuration pytest:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=. --cov-report=xml --cov-report=html
```

### 2. Tests d'Intégration

```python
# Test avec base de données
def test_user_registration(client, db):
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword'
    }
    response = client.post('/register', json=data)
    assert response.status_code == 201
```

### 3. Tests de Performance

```javascript
// K6 load test
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 },
    { duration: '5m', target: 10 },
    { duration: '2m', target: 0 },
  ],
};

export default function() {
  let response = http.get('https://your-app.railway.app/');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
```

## Monitoring et Alertes

### 1. Health Checks

Endpoint automatiquement testé:
```bash
GET /health
```

Réponse attendue:
```json
{
  "status": "healthy",
  "database": "healthy",
  "cache": "healthy",
  "version": "2.0.0"
}
```

### 2. Métriques Lighthouse

Tests automatiques:
- Performance > 90
- Accessibility = 100
- Best Practices = 100
- SEO > 90
- PWA = 100

### 3. Notifications Slack

Messages automatiques:
- ✅ Déploiement réussi
- ❌ Déploiement échoué
- ⚠️ Tests de performance dégradés
- 🔒 Vulnérabilités détectées

## Gestion des Échecs

### 1. Échec de Tests

```yaml
# Workflow continue même si tests échouent (staging)
continue-on-error: true  # Staging seulement

# Workflow s'arrête si tests échouent (production)
continue-on-error: false  # Production
```

### 2. Échec de Déploiement

Actions automatiques:
1. Notification Slack immédiate
2. Logs détaillés dans GitHub Actions
3. Rollback automatique si configuré

### 3. Rollback Automatique

```bash
# En cas d'échec du health check
if ! curl -f $PRODUCTION_URL/health; then
  railway rollback $PREVIOUS_DEPLOYMENT
fi
```

## Optimisations CI/CD

### 1. Cache des Dépendances

```yaml
- name: Cache Python dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
```

### 2. Parallélisation

```yaml
strategy:
  matrix:
    python-version: [3.11]
    os: [ubuntu-latest]
  fail-fast: false
```

### 3. Conditions de Déploiement

```yaml
# Déployer seulement si tests passent
needs: [test, build]
if: github.ref == 'refs/heads/main'
```

## Métriques et KPIs

### 1. Métriques de Déploiement

- **Fréquence:** Plusieurs fois par jour
- **Lead Time:** < 10 minutes
- **MTTR:** < 30 minutes
- **Taux de réussite:** > 95%

### 2. Métriques de Qualité

- **Couverture de code:** > 80%
- **Tests passants:** 100%
- **Vulnérabilités:** 0 critiques
- **Performance:** Score Lighthouse > 90

### 3. Métriques Opérationnelles

- **Uptime:** > 99.9%
- **Response time:** < 200ms (p95)
- **Error rate:** < 0.1%
- **Throughput:** 1000+ req/min

## Bonnes Pratiques

### 1. Commits

```bash
# Format des commits
feat: add user authentication
fix: resolve database connection issue
docs: update deployment guide
test: add integration tests for API
```

### 2. Branches

```bash
# Stratégie de branches
main        # Production stable
develop     # Staging/développement
feature/*   # Nouvelles fonctionnalités
hotfix/*    # Corrections urgentes
```

### 3. Pull Requests

- Tests automatiques requis
- Review obligatoire
- Squash merge recommandé
- Description détaillée

### 4. Releases

```bash
# Tags sémantiques
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin v2.0.0
```

## Troubleshooting

### Problèmes Courants

#### 1. Tests Échouent

```bash
# Exécuter localement
pytest -v
flake8 .
black --check .
```

#### 2. Déploiement Échoué

```bash
# Vérifier les logs
railway logs --deployment <id>

# Vérifier la configuration
railway status
```

#### 3. Health Check KO

```bash
# Tester localement
curl http://localhost:8080/health

# Vérifier les dépendances
railway variables
```

## Commandes Utiles

```bash
# CI/CD local
act                              # Exécuter GitHub Actions localement
docker build -f Dockerfile.railway .  # Build local

# Tests
pytest --cov=.                   # Tests avec couverture
flake8 .                         # Lint
black .                          # Format
safety check                     # Sécurité dépendances

# Railway
railway logs                     # Logs déploiement
railway status                   # Status service
railway restart                  # Redémarrage
```

Ce guide couvre l'ensemble du pipeline CI/CD pour Lataupe Bunker Tech. Pour des questions spécifiques, consultez les logs GitHub Actions ou contactez l'équipe DevOps.
"""
    
    return docs

def main():
    """Fonction principale pour créer les scripts d'automatisation Railway"""
    project_path = "/home/ubuntu/lataupe-bunker-tech"
    
    print("🤖 Création des scripts d'automatisation Railway...")
    print("=" * 55)
    
    # Créer les dossiers nécessaires
    scripts_dir = os.path.join(project_path, 'scripts')
    docs_dir = os.path.join(project_path, 'docs')
    
    for directory in [scripts_dir, docs_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # Créer les scripts CLI
    cli_scripts = create_railway_cli_scripts()
    for filepath, content in cli_scripts.items():
        full_path = os.path.join(project_path, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        # Rendre les scripts exécutables
        if filepath.endswith('.sh'):
            os.chmod(full_path, 0o755)
    
    # Créer la documentation
    documentation = create_railway_documentation()
    for filepath, content in documentation.items():
        full_path = os.path.join(project_path, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    print("\\n✅ Scripts d'automatisation Railway créés avec succès!")
    print("\\n📋 Scripts CLI créés:")
    for script in cli_scripts.keys():
        print(f"   • {script}")
    
    print("\\n📚 Documentation créée:")
    for doc in documentation.keys():
        print(f"   • {doc}")
    
    print("\\n🚀 Utilisation des scripts:")
    print("   1. Configuration initiale: ./scripts/railway-setup.sh")
    print("   2. Déploiement: ./scripts/railway-deploy.sh")
    print("   3. Monitoring: ./scripts/railway-monitor.sh")
    print("   4. Rollback: ./scripts/railway-rollback.sh")
    
    print("\\n📖 Documentation disponible:")
    print("   • Guide de déploiement: docs/RAILWAY_DEPLOYMENT.md")
    print("   • Guide CI/CD: docs/CICD_GUIDE.md")
    
    print("\\n🔧 Prochaines étapes:")
    print("   1. Configurer les secrets GitHub")
    print("   2. Exécuter railway-setup.sh")
    print("   3. Tester le déploiement")
    print("   4. Configurer le monitoring")
    
    return True

if __name__ == "__main__":
    main()

