#!/bin/bash
# Script de déploiement Kubernetes

set -e

echo "☸️  Déploiement Kubernetes - Lataupe Bunker Tech"
echo "==============================================="

# Variables
NAMESPACE="lataupe-bunker"
ENVIRONMENT=${1:-production}

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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
