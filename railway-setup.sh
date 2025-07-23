#!/bin/bash
# Script de configuration Railway pour lataupe-bunker-tech

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
