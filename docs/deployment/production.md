# Production Deployment Guide

Полное руководство по развертыванию RAG Chat Application в production-окружении.

## 📋 Предварительные требования

### Infrastructure Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk | 10 GB | 20+ GB SSD |
| Network | 100 Mbps | 1 Gbps |

### Software Stack

- **OS:** Ubuntu 22.04 LTS / Debian 12 / AWS Linux 2
- **Container Runtime:** Docker 24.0+ / Kubernetes 1.28+
- **Database:** PostgreSQL 15+ / ChromaDB 0.4+
- **Cache:** Redis 7.0+
- **Web Server:** Nginx 1.24+

---

## 🏗️ Deployment Options

### Option 1: Docker Compose (Small/Medium Scale)

### Option 2: Kubernetes (Large Scale)

### Option 3: Cloud Services (Managed)

---

## 🐳 Option 1: Docker Compose Deployment

### 1. Project Structure

```
production/
├── docker-compose.yml
├── nginx/
│   ├── nginx.conf
│   └── ssl/
│       ├── certificate.crt
│       └── private.key
├── backend/
│   ├── Dockerfile
│   └── .env.production
├── frontend/
│   ├── Dockerfile
│   └── .env.production
└── scripts/
    ├── backup.sh
    └── deploy.sh
```

### 2. Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: rag_chat
      POSTGRES_USER: rag_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - rag-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rag_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ChromaDB Vector Database
  chromadb:
    image: chromadb/chroma:0.4.22
    restart: always
    volumes:
      - chroma_data:/chroma/chroma
    networks:
      - rag-network
    environment:
      - CHROMA_SERVER_AUTHN_CREDENTIALS=${CHROMA_AUTH_TOKEN}
      - CHROMA_SERVER_AUTHN_PROVIDER=chromadb.auth.token_authn.TokenAuthenticationServerProvider

  # Redis Cache
  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - rag-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    environment:
      - DATABASE_URL=postgresql://rag_user:${POSTGRES_PASSWORD}@postgres:5432/rag_chat
      - REDIS_URL=redis://redis:6379
      - CHROMA_HOST=chromadb
      - CHROMA_AUTH_TOKEN=${CHROMA_AUTH_TOKEN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OLLAMA_BASE_URL=http://ollama:11434
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      postgres:
        condition: service_healthy
      chromadb:
        condition: service_started
      redis:
        condition: service_healthy
    networks:
      - rag-network
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  # Ollama for Local LLMs
  ollama:
    image: ollama/ollama:latest
    restart: always
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - rag-network
    deploy:
      resources:
        limits:
          memory: 8G
    command: ["ollama", "serve"]

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NEXT_PUBLIC_APP_URL=https://your-domain.com
    depends_on:
      - backend
    networks:
      - rag-network
    deploy:
      replicas: 2

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    networks:
      - rag-network

networks:
  rag-network:
    driver: bridge

volumes:
  postgres_data:
  chroma_data:
  redis_data:
  ollama_data:
```

### 3. Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 4. Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

### 5. Nginx Configuration

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Upstream definitions
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        # SSL certificates
        ssl_certificate /etc/nginx/ssl/certificate.crt;
        ssl_certificate_key /etc/nginx/ssl/private.key;

        # SSL settings
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Rate limiting
            limit_req zone=api burst=20 nodelay;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # API Documentation
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }

        location /redoc {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }

        # Static files caching
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
}
```

### 6. Environment Variables

```bash
# .env.production
# Database
POSTGRES_PASSWORD=your-secure-random-password-here
POSTGRES_DB=rag_chat
POSTGRES_USER=rag_user

# ChromaDB
CHROMA_AUTH_TOKEN=your-secret-auth-token
CHROMA_SERVER_AUTHN_CREDENTIALS=your-secret-auth-token

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
ENVIRONMENT=production

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Application
NEXT_PUBLIC_APP_URL=https://your-domain.com
NEXT_PUBLIC_API_URL=http://backend:8000
```

### 7. Deployment Script

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 Starting deployment..."

# Pull latest code
git pull origin main

# Build images
echo "🔨 Building Docker images..."
docker-compose build --no-cache

# Stop running containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Start new containers
echo "▶️  Starting containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Run database migrations
echo "📊 Running database migrations..."
docker-compose exec backend python -m alembic upgrade head

# Health check
echo "🏥 Performing health checks..."
docker-compose ps

echo "✅ Deployment complete!"
echo "📍 Frontend: https://your-domain.com"
echo "📍 API Docs: https://your-domain.com/docs"
```

---

## ☸️ Option 2: Kubernetes Deployment

### 1. Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: rag-chat
  labels:
    name: rag-chat
```

### 2. Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: rag-chat-secrets
  namespace: rag-chat
type: Opaque
stringData:
  postgres-password: "your-secure-password"
  secret-key: "your-super-secret-key"
  openai-api-key: "sk-your-api-key"
  chroma-auth-token: "your-auth-token"
```

### 3. ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: rag-chat-config
  namespace: rag-chat
data:
  ENVIRONMENT: "production"
  OLLAMA_BASE_URL: "http://ollama-service:11434"
```

### 4. PostgreSQL StatefulSet

```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: rag-chat
spec:
  serviceName: postgres
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
          value: rag_chat
        - name: POSTGRES_USER
          value: rag_user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rag-chat-secrets
              key: postgres-password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: rag-chat
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

### 5. Backend Deployment

```yaml
# k8s/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: rag-chat
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: postgresql://rag_user:$(POSTGRES_PASSWORD)@postgres-service:5432/rag_chat
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: rag-chat-secrets
              key: secret-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: rag-chat-secrets
              key: openai-api-key
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: rag-chat-config
              key: ENVIRONMENT
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: rag-chat
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 6. Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rag-chat-ingress
  namespace: rag-chat
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: rag-chat-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api/
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
```

---

## ☁️ Option 3: Cloud Deployment

### AWS Deployment

#### 1. ECS Fargate

```yaml
# ecs/task-definition.json
{
  "family": "rag-chat-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-accounts.dkr.ecr.region.amazonaws.com/rag-chat-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://..."
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:rag-chat/secret-key"
        }
      ]
    }
  ]
}
```

#### 2. RDS PostgreSQL

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier rag-chat-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15 \
  --master-username rag_user \
  --master-user-password your-password \
  --allocated-storage 20 \
  --storage-encrypted \
  --vpc-security-group-ids sg-xxxxxxxx \
  --db-subnet-group-name rag-chat-subnet-group
```

#### 3. ElastiCache Redis

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id rag-chat-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

---

## 🔐 Security Best Practices

### 1. SSL/TLS Certificates

```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 2. Database Security

```sql
-- PostgreSQL security
CREATE ROLE rag_app WITH LOGIN PASSWORD 'secure-password';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO rag_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO rag_app;

-- Restrict network access
ALTER SYSTEM SET listen_addresses = 'localhost';
```

### 3. Network Security

```yaml
# Kubernetes NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: rag-chat
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: rag-chat
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

---

## 📊 Monitoring & Logging

### 1. Prometheus & Grafana

```yaml
# monitoring/prometheus.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: rag-chat
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    
    scrape_configs:
      - job_name: 'backend'
        static_configs:
          - targets: ['backend-service:8000']
```

### 2. Application Logging

```python
# backend/logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_production_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(jsonjsonlogger.JsonFormatter())
    logger.addHandler(handler)
    
    return logger
```

---

## 🔄 Backup & Disaster Recovery

### 1. Database Backup

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

# Create backup
pg_dump -h postgres-host -U rag_user rag_chat > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Delete old backups (keep 7 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup created: $BACKUP_FILE.gz"
```

### 2. Restore Procedure

```bash
#!/bin/bash
# scripts/restore.sh

BACKUP_FILE=$1
RESTORE_DATE=$(date +%Y%m%d_%H%M%S)

# Decompress
gunzip $BACKUP_FILE

# Restore
psql -h postgres-host -U rag_user -d rag_chat < ${BACKUP_FILE%.gz}

echo "Database restored from: $BACKUP_FILE"
```

---

## ✅ Deployment Checklist

### Pre-Deployment

- [ ] All environment variables configured
- [ ] SSL certificates obtained
- [ ] Database migrations tested
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Monitoring configured
- [ ] Backup strategy defined
- [ ] Rollback plan documented

### Deployment

- [ ] Pull latest code
- [ ] Build Docker images
- [ ] Deploy database changes
- [ ] Deploy backend services
- [ ] Deploy frontend services
- [ ] Configure load balancer
- [ ] Verify health checks
- [ ] Test critical workflows

### Post-Deployment

- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Verify all endpoints
- [ ] Test user flows
- [ ] Confirm monitoring alerts
- [ ] Document any issues
- [ ] Schedule follow-up review

---

## 📞 Support & Maintenance

### Regular Tasks

- **Daily:** Check error logs, monitor performance
- **Weekly:** Review security patches, backup verification
- **Monthly:** Performance optimization, capacity planning
- **Quarterly:** Security audit, disaster recovery test

### Contact Information

- **Operations Team:** ops@example.com
- **On-Call:** +1-555-ONCALL
- **Incident Response:** incidents@example.com
