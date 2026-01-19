# Production Deployment Guide

This guide provides instructions for deploying LegalOS to production using Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Domain name configured with DNS
- SSL certificates (Let's Encrypt recommended)
- Minimum 4GB RAM, 8GB recommended
- 20GB disk space

## Environment Variables

Create a `.env` file in the project root:

```bash
# Security
SECRET_KEY=your-random-secret-key-at-least-32-characters-long
POSTGRES_PASSWORD=your-strong-postgres-password
REDIS_PASSWORD=your-strong-redis-password

# External Services
ZHIPU_API_KEY=your-zhipu-api-key

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your-grafana-password
```

**Security Notes:**
- Use strong, random passwords (minimum 32 characters)
- Rotate secrets regularly
- Never commit `.env` file to version control
- Use environment-specific secrets management in production

## SSL Certificates

### Option 1: Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d api.legalos.com -d www.legalos.com

# Copy certificates
sudo cp /etc/letsencrypt/live/legalos.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/legalos.com/privkey.pem nginx/ssl/key.pem
```

### Option 2: Self-Signed (Development Only)

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/CN=legalos.com"
```

## Deployment Steps

### 1. Prepare Server

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create project directory
mkdir -p /opt/legalos
cd /opt/legalos

# Clone repository
git clone <repository-url> .
```

### 2. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit with production values
nano .env
```

### 3. Build and Deploy

```bash
# Pull latest code
git pull origin main

# Build production images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Verify Deployment

```bash
# Health check
curl https://api.legalos.com/health

# API documentation
open https://api.legalos.com/docs

# Grafana dashboard
open https://monitoring.legalos.com
```

## Service Management

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f postgres
```

### Restart Services

```bash
# Restart all
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
```

### Update Services

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Clean up old images
docker image prune -f
```

### Backup and Restore

#### Database Backup

```bash
# Backup PostgreSQL
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U legal_user legal_os > backup_$(date +%Y%m%d).sql

# Backup Qdrant
docker cp legalos_qdrant_1:/qdrant/storage ./qdrant_backup_$(date +%Y%m%d)
```

#### Database Restore

```bash
# Restore PostgreSQL
cat backup_20240119.sql | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U legal_user legal_os

# Restore Qdrant
docker cp ./qdrant_backup_20240119 legalos_qdrant_1:/qdrant/storage
```

## Monitoring

### Access Monitoring Tools

- **Grafana**: https://monitoring.legalos.com
  - Default credentials: admin / <GRAFANA_ADMIN_PASSWORD>
- **Prometheus**: http://<server-ip>:9090
- **Logs**: Available in Grafana (Loki integration)

### Key Metrics to Monitor

1. **API Performance**
   - Request rate (requests/second)
   - Response times (p50, p95, p99)
   - Error rate (5xx responses)

2. **Resource Usage**
   - CPU utilization
   - Memory usage
   - Disk I/O

3. **Application Metrics**
   - LLM request rate
   - Vector search latency
   - Cache hit rate
   - Agent execution times

4. **Database Health**
   - Connection pool usage
   - Query performance
   - Storage growth

### Setting Up Alerts

Edit `monitoring/alerts.yml` to configure alerts:

```yaml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
```

## Security Hardening

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### Resource Limits

Edit `docker-compose.prod.yml` to add resource limits:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
      reservations:
        cpus: '1.0'
        memory: 2G
```

### Rate Limiting

Rate limiting is configured in `backend/app/core/security.py`:

```python
# Default: 100 requests per minute
# Adjust in docker-compose.prod.yml:
- RATE_LIMIT_PER_MINUTE=100
```

## Performance Tuning

### Database Optimization

```sql
-- Connect to PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres psql -U legal_user legal_os

-- Analyze tables
ANALYZE;

-- Create indexes (if not exists)
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_tasks_status ON tasks(status);
```

### Redis Configuration

Edit `docker-compose.prod.yml` Redis command:

```yaml
redis:
  command: >
    redis-server
    --appendonly yes
    --requirepass ${REDIS_PASSWORD}
    --maxmemory 1gb
    --maxmemory-policy allkeys-lru
```

### Scaling

#### Horizontal Scaling (Multiple Backend Instances)

```yaml
backend:
  deploy:
    replicas: 3
```

#### Vertical Scaling (More Resources)

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '4.0'
        memory: 8G
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs <service>

# Check port conflicts
sudo netstat -tulpn | grep LISTEN

# Verify disk space
df -h
```

### High Memory Usage

```bash
# Check memory usage
docker stats

# Restart bloated service
docker-compose -f docker-compose.prod.yml restart <service>
```

### Database Connection Issues

```bash
# Check PostgreSQL health
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U legal_user

# Check connection limit
docker-compose -f docker-compose.prod.yml exec postgres psql -U legal_user -d legal_os -c "SHOW max_connections;"
```

## Rollback Procedure

If a deployment causes issues:

```bash
# 1. Stop services
docker-compose -f docker-compose.prod.yml down

# 2. Rollback to previous version
git checkout <previous-commit-hash>

# 3. Restart with previous version
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify health
curl https://api.legalos.com/health
```

## Maintenance Schedule

### Daily
- Check Grafana dashboards
- Review error logs
- Monitor disk usage

### Weekly
- Review performance metrics
- Check SSL certificate expiration
- Review security alerts

### Monthly
- Update dependencies
- Run database maintenance
- Test backup/restore procedures
- Review and rotate secrets

## Support

For production issues:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Review Grafana dashboards
3. Check this troubleshooting guide
4. Create issue in repository

## Additional Resources

- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
