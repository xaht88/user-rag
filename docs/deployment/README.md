# Deployment Guide

## Overview

This directory contains deployment documentation for the RAG Chat Application.

## Documents

| File | Description |
|------|-------------|
| [production.md](./production.md) | Complete production deployment guide |

## Deployment Options

### 1. Docker Compose (Small/Medium Scale)

Best for: Development, small teams, single-server deployments

**Components:**
- PostgreSQL (session storage)
- ChromaDB (vector database)
- Redis (caching)
- Backend (FastAPI)
- Frontend (Next.js)
- Ollama (local LLM)
- Nginx (reverse proxy)

### 2. Kubernetes (Large Scale)

Best for: Enterprise deployments, high availability, auto-scaling

**Components:**
- Helm charts for all services
- Ingress controller
- Horizontal Pod Autoscaler
- Persistent Volume Claims
- Network Policies

### 3. Cloud Services (Managed)

Best for: Teams wanting minimal DevOps overhead

**AWS Options:**
- ECS Fargate (containers)
- RDS PostgreSQL (database)
- ElastiCache Redis (caching)
- CloudFront (CDN)

---

## Quick Deployment (Docker Compose)

### Prerequisites

- Docker 24.0+
- Docker Compose 2.0+
- Git

### Steps

1. **Clone Repository**
```bash
git clone <repository-url>
cd otus_dz2
```

2. **Create Environment File**
```bash
cp .env.example .env.production
# Edit .env.production with your values
```

3. **Build and Start**
```bash
docker-compose up --build -d
```

4. **Verify Deployment**
```bash
docker-compose ps
docker-compose logs -f
```

Access:
- Frontend: http://localhost
- API Docs: http://localhost/docs

---

## Production Checklist

### Pre-Deployment

- [ ] All environment variables configured
- [ ] SSL certificates obtained
- [ ] Database migrations tested
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Monitoring configured
- [ ] Backup strategy defined
- [ ] Rollback plan documented

### Post-Deployment

- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Verify all endpoints
- [ ] Test user flows
- [ ] Confirm monitoring alerts

---

## Monitoring

### Health Checks

- **Backend:** `GET /health`
- **Frontend:** `GET /`
- **Database:** Connection pool status
- **Redis:** `PING` command

### Metrics to Track

1. **Performance**
   - API response times
   - Query latency
   - Embedding generation time
   - LLM response time

2. **Resource Usage**
   - CPU utilization
   - Memory consumption
   - Disk space
   - Network I/O

3. **Business Metrics**
   - Active sessions
   - Documents uploaded
   - Queries processed
   - User engagement

---

## Security

### Best Practices

1. **Authentication**
   - Implement JWT authentication
   - Use OAuth2 for third-party auth
   - Rotate API keys regularly

2. **Authorization**
   - Role-based access control (RBAC)
   - API rate limiting
   - Input validation

3. **Data Protection**
   - Encrypt data at rest
   - Use HTTPS everywhere
   - Secure database connections

4. **Infrastructure**
   - Network segmentation
   - Firewall rules
   - Regular security updates

---

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL
pg_dump -h hostname -U user dbname > backup.sql

# ChromaDB
cp -r chroma_db/ chroma_db_backup/
```

### Restore Procedure

```bash
# PostgreSQL
psql -h hostname -U user dbname < backup.sql

# ChromaDB
rm -rf chroma_db/
cp -r chroma_db_backup/ chroma_db/
```

---

## Scaling

### Vertical Scaling

- Increase CPU/RAM for existing instances
- Upgrade database instance type
- Add more storage

### Horizontal Scaling

- Add more backend instances behind load balancer
- Deploy multiple frontend replicas
- Use database read replicas
- Implement caching layer

---

## Troubleshooting

See [production.md](./production.md) for detailed troubleshooting guide.

---

**See also:**
- [Development Guide](../development/README.md)
- [API Documentation](../api/README.md)
- [Architecture](../architecture/README.md)
