#!/usr/bin/env python3
"""
Scripts d'automatisation pour le déploiement Docker/Kubernetes
Crée tous les scripts nécessaires pour automatiser le déploiement
"""

import os
from pathlib import Path

def create_docker_scripts():
    """Crée les scripts Docker"""
    
    scripts = {}
    
    # Script de build Docker
    scripts['build-docker.sh'] = """#!/bin/bash
# Script de build Docker pour lataupe-bunker-tech

set -e

echo "🐳 Build Docker Images pour Lataupe Bunker Tech"
echo "================================================"

# Variables
PROJECT_NAME="lataupe-bunker-tech"
VERSION=${1:-latest}
REGISTRY=${DOCKER_REGISTRY:-""}

# Couleurs pour les logs
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

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
"""
    
    # Script de déploiement Docker Compose
    scripts['deploy-docker.sh'] = """#!/bin/bash
# Script de déploiement Docker Compose

set -e

echo "🚀 Déploiement Docker Compose - Lataupe Bunker Tech"
echo "==================================================="

# Variables
ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.yml"

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

# Vérifier les prérequis
if ! command -v docker-compose &> /dev/null; then
    log_error "docker-compose n'est pas installé"
    exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "Fichier $COMPOSE_FILE non trouvé"
    exit 1
fi

# Vérifier les variables d'environnement
if [ -z "$SECRET_KEY" ]; then
    log_warn "SECRET_KEY non définie, génération automatique..."
    export SECRET_KEY=$(openssl rand -hex 32)
fi

if [ -z "$MASTER_KEY" ]; then
    log_warn "MASTER_KEY non définie, génération automatique..."
    export MASTER_KEY=$(openssl rand -hex 32)
fi

# Créer les répertoires nécessaires
log_info "Création des répertoires..."
mkdir -p logs uploads static/uploads monitoring/prometheus monitoring/grafana

# Arrêter les services existants
log_info "Arrêt des services existants..."
docker-compose down --remove-orphans

# Nettoyer les volumes orphelins si demandé
if [ "$2" = "--clean" ]; then
    log_warn "Nettoyage des volumes..."
    docker-compose down -v
    docker system prune -f
fi

# Build des images si nécessaire
if [ "$2" = "--build" ] || [ "$3" = "--build" ]; then
    log_info "Build des images..."
    docker-compose build --no-cache
fi

# Démarrer les services
log_info "Démarrage des services..."
docker-compose up -d

# Attendre que les services soient prêts
log_info "Attente du démarrage des services..."
sleep 30

# Vérifier la santé des services
log_info "Vérification de la santé des services..."

services=("bunker-app" "bunker-postgres" "bunker-redis" "bunker-nginx")
for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up.*healthy"; then
        log_info "✅ $service est en bonne santé"
    else
        log_error "❌ $service n'est pas en bonne santé"
        docker-compose logs "$service" | tail -20
    fi
done

# Afficher les informations de déploiement
log_info "📊 Informations de déploiement:"
echo ""
echo "Services déployés:"
docker-compose ps

echo ""
echo "URLs d'accès:"
echo "  - Application: http://localhost"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000"

echo ""
echo "Commandes utiles:"
echo "  - Voir les logs: docker-compose logs -f [service]"
echo "  - Redémarrer: docker-compose restart [service]"
echo "  - Arrêter: docker-compose down"
echo "  - Mise à jour: ./deploy-docker.sh --build"

log_info "✅ Déploiement terminé avec succès!"
"""
    
    # Script de monitoring Docker
    scripts['monitor-docker.sh'] = """#!/bin/bash
# Script de monitoring Docker

echo "📊 Monitoring Docker - Lataupe Bunker Tech"
echo "=========================================="

# Fonction pour afficher les statistiques
show_stats() {
    echo ""
    echo "=== État des conteneurs ==="
    docker-compose ps
    
    echo ""
    echo "=== Utilisation des ressources ==="
    docker stats --no-stream --format "table {{.Container}}\\t{{.CPUPerc}}\\t{{.MemUsage}}\\t{{.NetIO}}\\t{{.BlockIO}}"
    
    echo ""
    echo "=== Santé des services ==="
    for container in $(docker-compose ps -q); do
        name=$(docker inspect --format='{{.Name}}' $container | sed 's/^\\///')
        health=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "no-healthcheck")
        echo "$name: $health"
    done
    
    echo ""
    echo "=== Utilisation des volumes ==="
    docker system df
}

# Fonction pour afficher les logs
show_logs() {
    echo ""
    echo "=== Logs récents ==="
    docker-compose logs --tail=50 --timestamps
}

# Fonction pour tester la connectivité
test_connectivity() {
    echo ""
    echo "=== Tests de connectivité ==="
    
    # Test de l'application
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/health | grep -q "200"; then
        echo "✅ Application: OK"
    else
        echo "❌ Application: ERREUR"
    fi
    
    # Test de Prometheus
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:9090/-/healthy | grep -q "200"; then
        echo "✅ Prometheus: OK"
    else
        echo "❌ Prometheus: ERREUR"
    fi
    
    # Test de Grafana
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health | grep -q "200"; then
        echo "✅ Grafana: OK"
    else
        echo "❌ Grafana: ERREUR"
    fi
}

# Menu interactif
while true; do
    echo ""
    echo "Choisissez une option:"
    echo "1) Afficher les statistiques"
    echo "2) Afficher les logs"
    echo "3) Tester la connectivité"
    echo "4) Monitoring en temps réel"
    echo "5) Quitter"
    
    read -p "Votre choix [1-5]: " choice
    
    case $choice in
        1)
            show_stats
            ;;
        2)
            show_logs
            ;;
        3)
            test_connectivity
            ;;
        4)
            echo "Monitoring en temps réel (Ctrl+C pour arrêter)..."
            watch -n 5 'docker stats --no-stream'
            ;;
        5)
            echo "Au revoir!"
            exit 0
            ;;
        *)
            echo "Option invalide"
            ;;
    esac
done
"""
    
    return scripts

def create_kubernetes_scripts():
    """Crée les scripts Kubernetes"""
    
    scripts = {}
    
    # Script de déploiement Kubernetes
    scripts['deploy-k8s.sh'] = """#!/bin/bash
# Script de déploiement Kubernetes

set -e

echo "☸️  Déploiement Kubernetes - Lataupe Bunker Tech"
echo "==============================================="

# Variables
NAMESPACE="lataupe-bunker"
ENVIRONMENT=${1:-production}

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

# Vérifier kubectl
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl n'est pas installé"
    exit 1
fi

# Vérifier la connexion au cluster
if ! kubectl cluster-info &> /dev/null; then
    log_error "Impossible de se connecter au cluster Kubernetes"
    exit 1
fi

log_info "Cluster Kubernetes connecté: $(kubectl config current-context)"

# Créer le namespace
log_info "Création du namespace $NAMESPACE..."
kubectl apply -f k8s/namespace.yaml

# Appliquer les secrets (après avoir vérifié qu'ils sont configurés)
log_info "Application des secrets..."
if [ -z "$SECRET_KEY" ] || [ -z "$MASTER_KEY" ]; then
    log_warn "Variables de secrets non définies, utilisation des valeurs par défaut"
    log_warn "ATTENTION: Changez les secrets en production!"
fi

kubectl apply -f k8s/secrets.yaml

# Appliquer les ConfigMaps
log_info "Application des ConfigMaps..."
kubectl apply -f k8s/configmap.yaml

# Déployer PostgreSQL
log_info "Déploiement de PostgreSQL..."
kubectl apply -f k8s/postgres-deployment.yaml

# Attendre que PostgreSQL soit prêt
log_info "Attente du démarrage de PostgreSQL..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s

# Déployer Redis
log_info "Déploiement de Redis..."
kubectl apply -f k8s/redis-deployment.yaml

# Attendre que Redis soit prêt
log_info "Attente du démarrage de Redis..."
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s

# Déployer l'application
log_info "Déploiement de l'application..."
kubectl apply -f k8s/app-deployment.yaml

# Attendre que l'application soit prête
log_info "Attente du démarrage de l'application..."
kubectl wait --for=condition=ready pod -l app=bunker-app -n $NAMESPACE --timeout=300s

# Déployer Nginx
log_info "Déploiement de Nginx..."
kubectl apply -f k8s/nginx-deployment.yaml

# Déployer l'Ingress
log_info "Déploiement de l'Ingress..."
kubectl apply -f k8s/ingress.yaml

# Déployer l'HPA
log_info "Déploiement de l'HPA..."
kubectl apply -f k8s/hpa.yaml

# Déployer les Network Policies
log_info "Déploiement des Network Policies..."
kubectl apply -f k8s/network-policy.yaml

# Vérifier le déploiement
log_info "Vérification du déploiement..."
echo ""
echo "=== Pods ==="
kubectl get pods -n $NAMESPACE

echo ""
echo "=== Services ==="
kubectl get services -n $NAMESPACE

echo ""
echo "=== Ingress ==="
kubectl get ingress -n $NAMESPACE

echo ""
echo "=== HPA ==="
kubectl get hpa -n $NAMESPACE

# Obtenir l'URL d'accès
INGRESS_IP=$(kubectl get ingress bunker-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")

echo ""
log_info "📊 Informations de déploiement:"
echo "  - Namespace: $NAMESPACE"
echo "  - Environnement: $ENVIRONMENT"
echo "  - Ingress IP: $INGRESS_IP"

if [ "$INGRESS_IP" != "pending" ] && [ ! -z "$INGRESS_IP" ]; then
    echo "  - URL d'accès: http://$INGRESS_IP"
else
    echo "  - URL d'accès: En attente de l'attribution de l'IP"
fi

echo ""
echo "Commandes utiles:"
echo "  - Voir les pods: kubectl get pods -n $NAMESPACE"
echo "  - Voir les logs: kubectl logs -f deployment/bunker-app-deployment -n $NAMESPACE"
echo "  - Redémarrer: kubectl rollout restart deployment/bunker-app-deployment -n $NAMESPACE"
echo "  - Supprimer: kubectl delete namespace $NAMESPACE"

log_info "✅ Déploiement Kubernetes terminé avec succès!"
"""
    
    # Script de monitoring Kubernetes
    scripts['monitor-k8s.sh'] = """#!/bin/bash
# Script de monitoring Kubernetes

NAMESPACE="lataupe-bunker"

echo "📊 Monitoring Kubernetes - Lataupe Bunker Tech"
echo "=============================================="

# Fonction pour afficher l'état général
show_overview() {
    echo ""
    echo "=== Vue d'ensemble ==="
    echo "Namespace: $NAMESPACE"
    echo "Cluster: $(kubectl config current-context)"
    
    echo ""
    echo "=== Pods ==="
    kubectl get pods -n $NAMESPACE -o wide
    
    echo ""
    echo "=== Services ==="
    kubectl get services -n $NAMESPACE
    
    echo ""
    echo "=== Deployments ==="
    kubectl get deployments -n $NAMESPACE
    
    echo ""
    echo "=== HPA ==="
    kubectl get hpa -n $NAMESPACE
}

# Fonction pour afficher les métriques de ressources
show_resources() {
    echo ""
    echo "=== Utilisation des ressources ==="
    kubectl top pods -n $NAMESPACE --sort-by=cpu
    
    echo ""
    echo "=== Utilisation des nœuds ==="
    kubectl top nodes
}

# Fonction pour afficher les logs
show_logs() {
    echo ""
    echo "=== Logs de l'application ==="
    kubectl logs -l app=bunker-app -n $NAMESPACE --tail=50 --timestamps
}

# Fonction pour afficher les événements
show_events() {
    echo ""
    echo "=== Événements récents ==="
    kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -20
}

# Fonction pour tester la santé
test_health() {
    echo ""
    echo "=== Tests de santé ==="
    
    # Vérifier les pods
    echo "Pods en cours d'exécution:"
    kubectl get pods -n $NAMESPACE --field-selector=status.phase=Running --no-headers | wc -l
    
    echo "Pods en erreur:"
    kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running --no-headers | wc -l
    
    # Vérifier les services
    echo ""
    echo "Services disponibles:"
    kubectl get services -n $NAMESPACE --no-headers | wc -l
    
    # Test de connectivité interne
    echo ""
    echo "Test de connectivité interne..."
    POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=bunker-app -o jsonpath='{.items[0].metadata.name}')
    if [ ! -z "$POD_NAME" ]; then
        kubectl exec -n $NAMESPACE $POD_NAME -- curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/health | grep -q "200" && echo "✅ Application: OK" || echo "❌ Application: ERREUR"
    fi
}

# Fonction pour afficher les détails d'un pod
show_pod_details() {
    echo ""
    read -p "Nom du pod à analyser: " pod_name
    
    if [ ! -z "$pod_name" ]; then
        echo ""
        echo "=== Détails du pod $pod_name ==="
        kubectl describe pod $pod_name -n $NAMESPACE
        
        echo ""
        echo "=== Logs du pod $pod_name ==="
        kubectl logs $pod_name -n $NAMESPACE --tail=100
    fi
}

# Menu interactif
while true; do
    echo ""
    echo "Choisissez une option:"
    echo "1) Vue d'ensemble"
    echo "2) Utilisation des ressources"
    echo "3) Logs de l'application"
    echo "4) Événements récents"
    echo "5) Tests de santé"
    echo "6) Détails d'un pod"
    echo "7) Monitoring en temps réel"
    echo "8) Quitter"
    
    read -p "Votre choix [1-8]: " choice
    
    case $choice in
        1)
            show_overview
            ;;
        2)
            show_resources
            ;;
        3)
            show_logs
            ;;
        4)
            show_events
            ;;
        5)
            test_health
            ;;
        6)
            show_pod_details
            ;;
        7)
            echo "Monitoring en temps réel (Ctrl+C pour arrêter)..."
            watch -n 5 "kubectl get pods -n $NAMESPACE && echo '' && kubectl top pods -n $NAMESPACE"
            ;;
        8)
            echo "Au revoir!"
            exit 0
            ;;
        *)
            echo "Option invalide"
            ;;
    esac
done
"""
    
    # Script Helm
    scripts['deploy-helm.sh'] = """#!/bin/bash
# Script de déploiement Helm

set -e

echo "⎈ Déploiement Helm - Lataupe Bunker Tech"
echo "========================================"

# Variables
RELEASE_NAME="bunker-app"
NAMESPACE="lataupe-bunker"
CHART_PATH="./helm/lataupe-bunker-tech"
VALUES_FILE="values.yaml"

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

# Vérifier Helm
if ! command -v helm &> /dev/null; then
    log_error "Helm n'est pas installé"
    exit 1
fi

# Vérifier le chart
if [ ! -d "$CHART_PATH" ]; then
    log_error "Chart Helm non trouvé: $CHART_PATH"
    exit 1
fi

# Créer le namespace
log_info "Création du namespace $NAMESPACE..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Ajouter les repositories Helm nécessaires
log_info "Ajout des repositories Helm..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Valider le chart
log_info "Validation du chart..."
helm lint $CHART_PATH

# Déployer ou mettre à jour
if helm list -n $NAMESPACE | grep -q $RELEASE_NAME; then
    log_info "Mise à jour de la release existante..."
    helm upgrade $RELEASE_NAME $CHART_PATH \\
        --namespace $NAMESPACE \\
        --values $CHART_PATH/$VALUES_FILE \\
        --wait \\
        --timeout 10m
else
    log_info "Installation de la nouvelle release..."
    helm install $RELEASE_NAME $CHART_PATH \\
        --namespace $NAMESPACE \\
        --values $CHART_PATH/$VALUES_FILE \\
        --wait \\
        --timeout 10m
fi

# Vérifier le déploiement
log_info "Vérification du déploiement..."
helm status $RELEASE_NAME -n $NAMESPACE

echo ""
log_info "📊 Informations de déploiement:"
echo "  - Release: $RELEASE_NAME"
echo "  - Namespace: $NAMESPACE"
echo "  - Chart: $CHART_PATH"

echo ""
echo "Commandes utiles:"
echo "  - Status: helm status $RELEASE_NAME -n $NAMESPACE"
echo "  - Logs: kubectl logs -f deployment/bunker-app -n $NAMESPACE"
echo "  - Rollback: helm rollback $RELEASE_NAME -n $NAMESPACE"
echo "  - Désinstaller: helm uninstall $RELEASE_NAME -n $NAMESPACE"

log_info "✅ Déploiement Helm terminé avec succès!"
"""
    
    return scripts

def create_configuration_files():
    """Crée les fichiers de configuration"""
    
    configs = {}
    
    # Configuration Nginx
    configs['nginx/nginx.conf'] = """user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # Performance settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 16M;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Upstream pour l'application
    upstream bunker_app {
        least_conn;
        server bunker-app:5001 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    server {
        listen 80;
        server_name _;

        # Security
        server_tokens off;

        # Health check
        location /nginx-health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }

        # Rate limiting pour les API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://bunker_app;
            include /etc/nginx/proxy_params;
        }

        # Rate limiting pour le login
        location /auth/login {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://bunker_app;
            include /etc/nginx/proxy_params;
        }

        # Application principale
        location / {
            proxy_pass http://bunker_app;
            include /etc/nginx/proxy_params;
        }

        # Fichiers statiques
        location /static/ {
            proxy_pass http://bunker_app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Uploads
        location /uploads/ {
            proxy_pass http://bunker_app/uploads/;
            expires 1d;
            add_header Cache-Control "public";
        }
    }
}
"""
    
    # Paramètres proxy Nginx
    configs['nginx/proxy_params'] = """proxy_set_header Host $http_host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;

proxy_connect_timeout 30s;
proxy_send_timeout 30s;
proxy_read_timeout 30s;

proxy_buffering on;
proxy_buffer_size 4k;
proxy_buffers 8 4k;
proxy_busy_buffers_size 8k;

proxy_redirect off;
"""
    
    # Configuration Redis
    configs['redis/redis.conf'] = """# Configuration Redis pour lataupe-bunker-tech

# Réseau
bind 0.0.0.0
port 6379
protected-mode yes

# Sécurité
requirepass change_this_redis_password

# Persistance
save 900 1
save 300 10
save 60 10000

appendonly yes
appendfsync everysec

# Mémoire
maxmemory 256mb
maxmemory-policy allkeys-lru

# Logs
loglevel notice
logfile /var/log/redis/redis-server.log

# Performance
tcp-keepalive 300
timeout 0

# Clients
maxclients 10000

# Slow log
slowlog-log-slower-than 10000
slowlog-max-len 128
"""
    
    # Configuration Prometheus
    configs['monitoring/prometheus.yml'] = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'bunker-app'
    static_configs:
      - targets: ['bunker-app:5001']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    scrape_interval: 30s
"""
    
    # Fichier d'environnement
    configs['.env.example'] = """# Configuration d'environnement pour lataupe-bunker-tech

# Application
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-in-production
MASTER_KEY=your-master-key-here-change-in-production

# Base de données
DATABASE_URL=postgresql://bunker_user:secure_password@postgres:5432/lataupe_bunker
DB_HOST=postgres
DB_PORT=5432
DB_NAME=lataupe_bunker
DB_USER=bunker_user
DB_PASSWORD=secure_password

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@bunker.tech
FROM_NAME=Lataupe Bunker Tech

# URLs
BASE_URL=https://bunker.tech

# Docker Registry (optionnel)
DOCKER_REGISTRY=your-registry.com/bunker

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
"""
    
    return configs

def main():
    """Fonction principale pour créer les scripts d'automatisation"""
    project_path = "/home/ubuntu/lataupe-bunker-tech"
    
    print("🤖 Création des scripts d'automatisation...")
    print("=" * 50)
    
    # Créer les scripts Docker
    docker_scripts = create_docker_scripts()
    for filename, content in docker_scripts.items():
        filepath = os.path.join(project_path, 'scripts', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        os.chmod(filepath, 0o755)  # Rendre exécutable
    
    # Créer les scripts Kubernetes
    k8s_scripts = create_kubernetes_scripts()
    for filename, content in k8s_scripts.items():
        filepath = os.path.join(project_path, 'scripts', filename)
        with open(filepath, 'w') as f:
            f.write(content)
        os.chmod(filepath, 0o755)  # Rendre exécutable
    
    # Créer les fichiers de configuration
    configs = create_configuration_files()
    for filename, content in configs.items():
        filepath = os.path.join(project_path, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
    
    print("\\n✅ Scripts d'automatisation créés avec succès!")
    print("\\n📋 Scripts créés:")
    print(f"   • Scripts Docker: {len(docker_scripts)} fichiers")
    print(f"   • Scripts Kubernetes: {len(k8s_scripts)} fichiers")
    print(f"   • Fichiers de configuration: {len(configs)} fichiers")
    
    print("\\n🐳 Scripts Docker:")
    print("   • build-docker.sh - Build des images Docker")
    print("   • deploy-docker.sh - Déploiement Docker Compose")
    print("   • monitor-docker.sh - Monitoring Docker")
    
    print("\\n☸️  Scripts Kubernetes:")
    print("   • deploy-k8s.sh - Déploiement Kubernetes")
    print("   • monitor-k8s.sh - Monitoring Kubernetes")
    print("   • deploy-helm.sh - Déploiement Helm")
    
    print("\\n⚙️  Configurations:")
    print("   • nginx/nginx.conf - Configuration Nginx optimisée")
    print("   • redis/redis.conf - Configuration Redis sécurisée")
    print("   • monitoring/prometheus.yml - Configuration Prometheus")
    print("   • .env.example - Variables d'environnement")
    
    print("\\n🚀 Utilisation:")
    print("   # Docker")
    print("   ./scripts/build-docker.sh")
    print("   ./scripts/deploy-docker.sh")
    print("   ")
    print("   # Kubernetes")
    print("   ./scripts/deploy-k8s.sh")
    print("   ./scripts/monitor-k8s.sh")
    print("   ")
    print("   # Helm")
    print("   ./scripts/deploy-helm.sh")
    
    return True

if __name__ == "__main__":
    main()

