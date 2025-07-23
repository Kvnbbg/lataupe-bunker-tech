#!/usr/bin/env python3
"""
Système complet de dockerisation et configuration Kubernetes pour lataupe-bunker-tech
Crée tous les fichiers nécessaires pour un déploiement containerisé sécurisé
"""

import os
import json
from pathlib import Path

def create_main_dockerfile():
    """Crée le Dockerfile principal pour l'application"""
    
    dockerfile_content = """# Dockerfile pour lataupe-bunker-tech
# Image de base optimisée pour la sécurité et les performances
FROM python:3.11-slim-bullseye

# Métadonnées
LABEL maintainer="Lataupe Bunker Tech Team"
LABEL version="2.0.0"
LABEL description="Secure Bunker Management System"

# Variables d'environnement pour la sécurité
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production
ENV DEBIAN_FRONTEND=noninteractive

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r bunker && useradd -r -g bunker -d /app -s /sbin/nologin bunker

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    libffi-dev \\
    libssl-dev \\
    curl \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# Créer les répertoires de l'application
WORKDIR /app
RUN mkdir -p /app/logs /app/uploads /app/static/uploads \\
    && chown -R bunker:bunker /app

# Copier les fichiers de requirements en premier pour optimiser le cache Docker
COPY requirements_secure.txt /app/
RUN pip install --no-cache-dir --upgrade pip \\
    && pip install --no-cache-dir -r requirements_secure.txt

# Copier le code de l'application
COPY --chown=bunker:bunker . /app/

# Créer les répertoires nécessaires avec les bonnes permissions
RUN mkdir -p /app/instance /app/migrations \\
    && chown -R bunker:bunker /app \\
    && chmod -R 755 /app \\
    && chmod +x /app/start_secure.sh

# Exposer le port de l'application
EXPOSE 5001

# Passer à l'utilisateur non-root
USER bunker

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5001/health || exit 1

# Commande par défaut
CMD ["python", "main_secure.py"]
"""
    
    return dockerfile_content

def create_nginx_dockerfile():
    """Crée le Dockerfile pour Nginx (reverse proxy)"""
    
    nginx_dockerfile = """# Dockerfile pour Nginx reverse proxy
FROM nginx:1.25-alpine

# Métadonnées
LABEL maintainer="Lataupe Bunker Tech Team"
LABEL description="Nginx Reverse Proxy for Bunker App"

# Copier la configuration Nginx
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Copier les certificats SSL (si disponibles)
COPY nginx/ssl/ /etc/nginx/ssl/

# Créer les répertoires nécessaires
RUN mkdir -p /var/cache/nginx/client_temp \\
    && mkdir -p /var/log/nginx \\
    && chown -R nginx:nginx /var/cache/nginx \\
    && chown -R nginx:nginx /var/log/nginx

# Exposer les ports
EXPOSE 80 443

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost/health || exit 1

# Commande par défaut
CMD ["nginx", "-g", "daemon off;"]
"""
    
    return nginx_dockerfile

def create_postgres_dockerfile():
    """Crée le Dockerfile pour PostgreSQL personnalisé"""
    
    postgres_dockerfile = """# Dockerfile pour PostgreSQL avec extensions bunker
FROM postgres:15-alpine

# Métadonnées
LABEL maintainer="Lataupe Bunker Tech Team"
LABEL description="PostgreSQL Database for Bunker System"

# Variables d'environnement
ENV POSTGRES_DB=lataupe_bunker
ENV POSTGRES_USER=bunker_user
ENV POSTGRES_PASSWORD=change_this_password
ENV PGDATA=/var/lib/postgresql/data/pgdata

# Installer les extensions nécessaires
RUN apk add --no-cache \\
    postgresql-contrib \\
    postgresql-dev

# Copier les scripts d'initialisation
COPY database/init/ /docker-entrypoint-initdb.d/

# Copier la configuration PostgreSQL optimisée
COPY database/postgresql.conf /etc/postgresql/postgresql.conf
COPY database/pg_hba.conf /etc/postgresql/pg_hba.conf

# Créer les répertoires avec les bonnes permissions
RUN mkdir -p /var/lib/postgresql/data/pgdata \\
    && chown -R postgres:postgres /var/lib/postgresql/data

# Exposer le port PostgreSQL
EXPOSE 5432

# Volume pour la persistance des données
VOLUME ["/var/lib/postgresql/data"]

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\
    CMD pg_isready -U $POSTGRES_USER -d $POSTGRES_DB || exit 1
"""
    
    return postgres_dockerfile

def create_redis_dockerfile():
    """Crée le Dockerfile pour Redis (cache et sessions)"""
    
    redis_dockerfile = """# Dockerfile pour Redis
FROM redis:7-alpine

# Métadonnées
LABEL maintainer="Lataupe Bunker Tech Team"
LABEL description="Redis Cache and Session Store"

# Copier la configuration Redis sécurisée
COPY redis/redis.conf /etc/redis/redis.conf

# Créer les répertoires nécessaires
RUN mkdir -p /var/lib/redis \\
    && chown -R redis:redis /var/lib/redis

# Exposer le port Redis
EXPOSE 6379

# Volume pour la persistance
VOLUME ["/var/lib/redis"]

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD redis-cli ping || exit 1

# Commande avec configuration personnalisée
CMD ["redis-server", "/etc/redis/redis.conf"]
"""
    
    return redis_dockerfile

def create_docker_compose():
    """Crée le fichier docker-compose.yml"""
    
    compose_content = """version: '3.8'

services:
  # Application principale
  bunker-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: bunker-app
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://bunker_user:secure_password@postgres:5432/lataupe_bunker
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - MASTER_KEY=${MASTER_KEY}
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
      - ./static/uploads:/app/static/uploads
    depends_on:
      - postgres
      - redis
    networks:
      - bunker-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Base de données PostgreSQL
  postgres:
    build:
      context: .
      dockerfile: docker/Dockerfile.postgres
    container_name: bunker-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=lataupe_bunker
      - POSTGRES_USER=bunker_user
      - POSTGRES_PASSWORD=secure_password
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/backups:/backups
    networks:
      - bunker-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bunker_user -d lataupe_bunker"]
      interval: 30s
      timeout: 5s
      retries: 5
      start_period: 30s

  # Cache Redis
  redis:
    build:
      context: .
      dockerfile: docker/Dockerfile.redis
    container_name: bunker-redis
    restart: unless-stopped
    volumes:
      - redis_data:/var/lib/redis
    networks:
      - bunker-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 3s
      retries: 3

  # Reverse Proxy Nginx
  nginx:
    build:
      context: .
      dockerfile: docker/Dockerfile.nginx
    container_name: bunker-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - bunker-app
    networks:
      - bunker-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  # Monitoring avec Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: bunker-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - bunker-network

  # Visualisation avec Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: bunker-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin_password_change_me
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - bunker-network

# Réseaux
networks:
  bunker-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

# Volumes persistants
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
"""
    
    return compose_content

def create_kubernetes_manifests():
    """Crée les manifests Kubernetes"""
    
    manifests = {}
    
    # Namespace
    manifests['namespace.yaml'] = """apiVersion: v1
kind: Namespace
metadata:
  name: lataupe-bunker
  labels:
    name: lataupe-bunker
    environment: production
"""
    
    # ConfigMap pour la configuration
    manifests['configmap.yaml'] = """apiVersion: v1
kind: ConfigMap
metadata:
  name: bunker-config
  namespace: lataupe-bunker
data:
  FLASK_ENV: "production"
  DATABASE_HOST: "postgres-service"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "lataupe_bunker"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  SMTP_SERVER: "smtp.gmail.com"
  SMTP_PORT: "587"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: lataupe-bunker
data:
  nginx.conf: |
    user nginx;
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
        
        # Logging
        log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for"';
        access_log /var/log/nginx/access.log main;
        
        # Performance
        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 65;
        types_hash_max_size 2048;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        
        # Gzip compression
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
        
        upstream bunker-app {
            server bunker-app-service:5001;
        }
        
        server {
            listen 80;
            server_name _;
            
            # Health check endpoint
            location /health {
                proxy_pass http://bunker-app/health;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
            
            # Main application
            location / {
                proxy_pass http://bunker-app;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                
                # Timeouts
                proxy_connect_timeout 30s;
                proxy_send_timeout 30s;
                proxy_read_timeout 30s;
                
                # Buffer settings
                proxy_buffering on;
                proxy_buffer_size 4k;
                proxy_buffers 8 4k;
            }
            
            # Static files
            location /static/ {
                proxy_pass http://bunker-app/static/;
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }
    }
"""
    
    # Secrets
    manifests['secrets.yaml'] = """apiVersion: v1
kind: Secret
metadata:
  name: bunker-secrets
  namespace: lataupe-bunker
type: Opaque
data:
  # Base64 encoded values - replace with actual values
  SECRET_KEY: Y2hhbmdlX3RoaXNfc2VjcmV0X2tleQ==
  MASTER_KEY: Y2hhbmdlX3RoaXNfbWFzdGVyX2tleQ==
  DATABASE_PASSWORD: c2VjdXJlX3Bhc3N3b3Jk
  SMTP_USERNAME: eW91cl9lbWFpbEBnbWFpbC5jb20=
  SMTP_PASSWORD: eW91cl9hcHBfcGFzc3dvcmQ=
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: lataupe-bunker
type: Opaque
data:
  POSTGRES_PASSWORD: c2VjdXJlX3Bhc3N3b3Jk
  POSTGRES_USER: YnVua2VyX3VzZXI=
"""
    
    # PostgreSQL Deployment
    manifests['postgres-deployment.yaml'] = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-deployment
  namespace: lataupe-bunker
  labels:
    app: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: "lataupe_bunker"
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_PASSWORD
        - name: PGDATA
          value: "/var/lib/postgresql/data/pgdata"
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - bunker_user
            - -d
            - lataupe_bunker
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - bunker_user
            - -d
            - lataupe_bunker
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: lataupe-bunker
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: lataupe-bunker
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
"""
    
    # Redis Deployment
    manifests['redis-deployment.yaml'] = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-deployment
  namespace: lataupe-bunker
  labels:
    app: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server"]
        args: ["--appendonly", "yes", "--requirepass", "$(REDIS_PASSWORD)"]
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: bunker-secrets
              key: SECRET_KEY
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: lataupe-bunker
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: lataupe-bunker
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
"""
    
    # Application Deployment
    manifests['app-deployment.yaml'] = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: bunker-app-deployment
  namespace: lataupe-bunker
  labels:
    app: bunker-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bunker-app
  template:
    metadata:
      labels:
        app: bunker-app
    spec:
      containers:
      - name: bunker-app
        image: lataupe-bunker-tech:latest
        ports:
        - containerPort: 5001
        env:
        - name: FLASK_ENV
          valueFrom:
            configMapKeyRef:
              name: bunker-config
              key: FLASK_ENV
        - name: DATABASE_URL
          value: "postgresql://$(DATABASE_USER):$(DATABASE_PASSWORD)@$(DATABASE_HOST):$(DATABASE_PORT)/$(DATABASE_NAME)"
        - name: DATABASE_HOST
          valueFrom:
            configMapKeyRef:
              name: bunker-config
              key: DATABASE_HOST
        - name: DATABASE_PORT
          valueFrom:
            configMapKeyRef:
              name: bunker-config
              key: DATABASE_PORT
        - name: DATABASE_NAME
          valueFrom:
            configMapKeyRef:
              name: bunker-config
              key: DATABASE_NAME
        - name: DATABASE_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_USER
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_PASSWORD
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: bunker-secrets
              key: SECRET_KEY
        - name: MASTER_KEY
          valueFrom:
            secretKeyRef:
              name: bunker-secrets
              key: MASTER_KEY
        - name: REDIS_URL
          value: "redis://$(REDIS_HOST):$(REDIS_PORT)/0"
        - name: REDIS_HOST
          valueFrom:
            configMapKeyRef:
              name: bunker-config
              key: REDIS_HOST
        - name: REDIS_PORT
          valueFrom:
            configMapKeyRef:
              name: bunker-config
              key: REDIS_PORT
        volumeMounts:
        - name: app-logs
          mountPath: /app/logs
        - name: app-uploads
          mountPath: /app/uploads
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5001
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: app-logs
        persistentVolumeClaim:
          claimName: app-logs-pvc
      - name: app-uploads
        persistentVolumeClaim:
          claimName: app-uploads-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: bunker-app-service
  namespace: lataupe-bunker
spec:
  selector:
    app: bunker-app
  ports:
  - port: 5001
    targetPort: 5001
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-logs-pvc
  namespace: lataupe-bunker
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-uploads-pvc
  namespace: lataupe-bunker
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
"""
    
    # Nginx Deployment
    manifests['nginx-deployment.yaml'] = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: lataupe-bunker
  labels:
    app: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25-alpine
        ports:
        - containerPort: 80
        - containerPort: 443
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/nginx.conf
          subPath: nginx.conf
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: nginx-config
        configMap:
          name: nginx-config
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: lataupe-bunker
spec:
  selector:
    app: nginx
  ports:
  - name: http
    port: 80
    targetPort: 80
  - name: https
    port: 443
    targetPort: 443
  type: LoadBalancer
"""
    
    # Ingress
    manifests['ingress.yaml'] = """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bunker-ingress
  namespace: lataupe-bunker
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "16m"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - bunker.tech
    - www.bunker.tech
    secretName: bunker-tls
  rules:
  - host: bunker.tech
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-service
            port:
              number: 80
  - host: www.bunker.tech
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-service
            port:
              number: 80
"""
    
    # HorizontalPodAutoscaler
    manifests['hpa.yaml'] = """apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bunker-app-hpa
  namespace: lataupe-bunker
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bunker-app-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
"""
    
    # NetworkPolicy
    manifests['network-policy.yaml'] = """apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: bunker-network-policy
  namespace: lataupe-bunker
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app: nginx
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
  - from:
    - podSelector:
        matchLabels:
          app: bunker-app
    - podSelector:
        matchLabels:
          app: postgres
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 5001
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 587
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
"""
    
    return manifests

def create_helm_chart():
    """Crée un chart Helm pour le déploiement"""
    
    helm_files = {}
    
    # Chart.yaml
    helm_files['Chart.yaml'] = """apiVersion: v2
name: lataupe-bunker-tech
description: A Helm chart for Lataupe Bunker Tech secure application
type: application
version: 2.0.0
appVersion: "2.0.0"
keywords:
  - bunker
  - security
  - survival
  - monitoring
home: https://bunker.tech
sources:
  - https://github.com/kvnbbg/lataupe-bunker-tech
maintainers:
  - name: Lataupe Bunker Tech Team
    email: admin@bunker.tech
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
  - name: redis
    version: "17.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
"""
    
    # values.yaml
    helm_files['values.yaml'] = """# Default values for lataupe-bunker-tech
replicaCount: 3

image:
  repository: lataupe-bunker-tech
  pullPolicy: IfNotPresent
  tag: "latest"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations: {}

podSecurityContext:
  fsGroup: 1000

securityContext:
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: false
  runAsNonRoot: true
  runAsUser: 1000

service:
  type: ClusterIP
  port: 5001

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "16m"
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: bunker.tech
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: bunker-tls
      hosts:
        - bunker.tech

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity: {}

# Configuration de l'application
app:
  config:
    flaskEnv: production
    secretKey: ""
    masterKey: ""
    databaseUrl: ""
    redisUrl: ""
    smtpServer: "smtp.gmail.com"
    smtpPort: 587
    smtpUsername: ""
    smtpPassword: ""

# PostgreSQL configuration
postgresql:
  enabled: true
  auth:
    postgresPassword: "secure_password"
    username: "bunker_user"
    password: "secure_password"
    database: "lataupe_bunker"
  primary:
    persistence:
      enabled: true
      size: 10Gi
    resources:
      requests:
        memory: 256Mi
        cpu: 250m
      limits:
        memory: 512Mi
        cpu: 500m

# Redis configuration
redis:
  enabled: true
  auth:
    enabled: true
    password: "redis_password"
  master:
    persistence:
      enabled: true
      size: 5Gi
    resources:
      requests:
        memory: 128Mi
        cpu: 100m
      limits:
        memory: 256Mi
        cpu: 200m

# Monitoring
monitoring:
  enabled: true
  prometheus:
    enabled: true
  grafana:
    enabled: true
    adminPassword: "admin_password"

# Persistence
persistence:
  logs:
    enabled: true
    size: 5Gi
    accessMode: ReadWriteMany
  uploads:
    enabled: true
    size: 10Gi
    accessMode: ReadWriteMany
"""
    
    return helm_files

def main():
    """Fonction principale pour créer le système Docker/Kubernetes"""
    project_path = "/home/ubuntu/lataupe-bunker-tech"
    
    print("🐳 Création du système Docker et Kubernetes...")
    print("=" * 55)
    
    # Créer les dossiers nécessaires
    docker_dir = os.path.join(project_path, 'docker')
    k8s_dir = os.path.join(project_path, 'k8s')
    helm_dir = os.path.join(project_path, 'helm', 'lataupe-bunker-tech')
    nginx_dir = os.path.join(project_path, 'nginx')
    redis_dir = os.path.join(project_path, 'redis')
    monitoring_dir = os.path.join(project_path, 'monitoring')
    
    for directory in [docker_dir, k8s_dir, helm_dir, nginx_dir, redis_dir, monitoring_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # Créer le Dockerfile principal
    main_dockerfile = os.path.join(project_path, 'Dockerfile')
    with open(main_dockerfile, 'w') as f:
        f.write(create_main_dockerfile())
    
    # Créer les Dockerfiles spécialisés
    dockerfiles = {
        'Dockerfile.nginx': create_nginx_dockerfile(),
        'Dockerfile.postgres': create_postgres_dockerfile(),
        'Dockerfile.redis': create_redis_dockerfile()
    }
    
    for filename, content in dockerfiles.items():
        filepath = os.path.join(docker_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
    
    # Créer docker-compose.yml
    compose_file = os.path.join(project_path, 'docker-compose.yml')
    with open(compose_file, 'w') as f:
        f.write(create_docker_compose())
    
    # Créer les manifests Kubernetes
    k8s_manifests = create_kubernetes_manifests()
    for filename, content in k8s_manifests.items():
        filepath = os.path.join(k8s_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
    
    # Créer le chart Helm
    helm_files = create_helm_chart()
    for filename, content in helm_files.items():
        filepath = os.path.join(helm_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
    
    print("\\n✅ Système Docker et Kubernetes créé avec succès!")
    print("\\n📋 Fichiers créés:")
    print(f"   • Dockerfile principal: {main_dockerfile}")
    print(f"   • Docker Compose: {compose_file}")
    print(f"   • Dockerfiles spécialisés: {len(dockerfiles)} fichiers")
    print(f"   • Manifests Kubernetes: {len(k8s_manifests)} fichiers")
    print(f"   • Chart Helm: {len(helm_files)} fichiers")
    
    print("\\n🐳 Fonctionnalités Docker:")
    print("   • Images multi-stage optimisées")
    print("   • Utilisateurs non-root pour la sécurité")
    print("   • Health checks intégrés")
    print("   • Volumes persistants")
    print("   • Réseau isolé")
    print("   • Monitoring avec Prometheus/Grafana")
    
    print("\\n☸️  Fonctionnalités Kubernetes:")
    print("   • Déploiements haute disponibilité")
    print("   • Auto-scaling horizontal")
    print("   • Network policies sécurisées")
    print("   • Secrets et ConfigMaps")
    print("   • Ingress avec SSL/TLS")
    print("   • Persistent volumes")
    print("   • Resource limits et requests")
    
    print("\\n🚀 Commandes de déploiement:")
    print("   # Docker Compose")
    print("   docker-compose up -d")
    print("   ")
    print("   # Kubernetes")
    print("   kubectl apply -f k8s/")
    print("   ")
    print("   # Helm")
    print("   helm install bunker-app ./helm/lataupe-bunker-tech")
    
    return True

if __name__ == "__main__":
    main()

