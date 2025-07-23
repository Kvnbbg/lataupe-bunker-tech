# Guide de Déploiement Railway - Lataupe Bunker Tech

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
gunicorn \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --threads 4 \
  --worker-class gthread \
  --timeout 30 \
  --keep-alive 2 \
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
