#!/bin/bash
# Script de build Docker pour lataupe-bunker-tech

set -e

echo "🐳 Build Docker Images pour Lataupe Bunker Tech"
echo "================================================"

# Variables
PROJECT_NAME="lataupe-bunker-tech"
VERSION=${1:-latest}
REGISTRY=${DOCKER_REGISTRY:-""}

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    log_error "Docker n'est pas installé"
    exit 1
fi

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "Dockerfile" ]; then
    log_error "Dockerfile non trouvé. Exécutez ce script depuis la racine du projet."
    exit 1
fi

log_info "Building main application image..."
docker build -t ${PROJECT_NAME}:${VERSION} .

log_info "Building Nginx image..."
docker build -f docker/Dockerfile.nginx -t ${PROJECT_NAME}-nginx:${VERSION} .

log_info "Building PostgreSQL image..."
docker build -f docker/Dockerfile.postgres -t ${PROJECT_NAME}-postgres:${VERSION} .

log_info "Building Redis image..."
docker build -f docker/Dockerfile.redis -t ${PROJECT_NAME}-redis:${VERSION} .

# Tag pour le registry si spécifié
if [ ! -z "$REGISTRY" ]; then
    log_info "Tagging images for registry: $REGISTRY"
    
    docker tag ${PROJECT_NAME}:${VERSION} ${REGISTRY}/${PROJECT_NAME}:${VERSION}
    docker tag ${PROJECT_NAME}-nginx:${VERSION} ${REGISTRY}/${PROJECT_NAME}-nginx:${VERSION}
    docker tag ${PROJECT_NAME}-postgres:${VERSION} ${REGISTRY}/${PROJECT_NAME}-postgres:${VERSION}
    docker tag ${PROJECT_NAME}-redis:${VERSION} ${REGISTRY}/${PROJECT_NAME}-redis:${VERSION}
    
    log_info "Pushing images to registry..."
    docker push ${REGISTRY}/${PROJECT_NAME}:${VERSION}
    docker push ${REGISTRY}/${PROJECT_NAME}-nginx:${VERSION}
    docker push ${REGISTRY}/${PROJECT_NAME}-postgres:${VERSION}
    docker push ${REGISTRY}/${PROJECT_NAME}-redis:${VERSION}
fi

log_info "✅ Build completed successfully!"
log_info "Images created:"
echo "  - ${PROJECT_NAME}:${VERSION}"
echo "  - ${PROJECT_NAME}-nginx:${VERSION}"
echo "  - ${PROJECT_NAME}-postgres:${VERSION}"
echo "  - ${PROJECT_NAME}-redis:${VERSION}"

if [ ! -z "$REGISTRY" ]; then
    echo ""
    log_info "Images pushed to registry: $REGISTRY"
fi
