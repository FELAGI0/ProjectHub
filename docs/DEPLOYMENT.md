# Deployment Guide

This guide covers deploying ProjectHub to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Database Setup](#database-setup)
- [Security Checklist](#security-checklist)
- [Monitoring](#monitoring)
- [Backup and Recovery](#backup-and-recovery)

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- PostgreSQL 16+
- Domain name with SSL certificate
- Reverse proxy (nginx, Caddy, or Traefik)

## Environment Variables

Production `.env` configuration:

```bash
# Application
APP_NAME=ProjectHub
DEBUG=false                    # IMPORTANT: Disable debug in production
LOG_LEVEL=INFO                # INFO or WARNING for production
API_PORT=8000

# Database
POSTGRES_DB=projecthub
POSTGRES_USER=projecthub
POSTGRES_PASSWORD=<STRONG_PASSWORD_HERE>
POSTGRES_HOST=postgres         # or external host
POSTGRES_PORT=5432
POSTGRES_SSL=true             # Enable SSL for remote connections

# Security
JWT_SECRET_KEY=<GENERATE_SECURE_KEY>  # min 32 characters
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Generating Secure Secrets

```bash
# Generate JWT secret (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate PostgreSQL password
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

## Docker Deployment

### Production Docker Compose

Create `compose.prod.yaml`:

```yaml
services:
  api:
    image: ghcr.io/yourusername/projecthub:latest
    restart: unless-stopped
    env_file:
      - .env.production
    environment:
      POSTGRES_HOST: postgres
    ports:
      - "127.0.0.1:8000:8000"  # Only expose on localhost
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 10s
      timeout: 5s
      retries: 5
    # Don't expose PostgreSQL port to host in production

volumes:
  postgres_data:
    driver: local
```

### Deployment Steps

```bash
# 1. Pull latest image
docker compose -f compose.prod.yaml pull

# 2. Stop existing containers
docker compose -f compose.prod.yaml down

# 3. Run migrations
docker compose -f compose.prod.yaml run --rm api uv run alembic upgrade head

# 4. Start services
docker compose -f compose.prod.yaml up -d

# 5. Verify health
curl http://localhost:8000/api/v1/health
```

## Cloud Platforms

### AWS (ECS + RDS)

1. **Create RDS PostgreSQL instance**
2. **Push image to ECR**
3. **Create ECS task definition**
4. **Deploy to ECS service**
5. **Configure ALB with SSL**

### Google Cloud Run

```bash
# Build and deploy
gcloud run deploy projecthub \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars POSTGRES_HOST=<CLOUD_SQL_IP> \
  --add-cloudsql-instances <INSTANCE_CONNECTION_NAME>
```

### Heroku

```bash
# Create app
heroku create projecthub-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# Set environment variables
heroku config:set JWT_SECRET_KEY=<secret>
heroku config:set DEBUG=false

# Deploy
git push heroku main

# Run migrations
heroku run uv run alembic upgrade head
```

### DigitalOcean App Platform

1. Create app from GitHub repository
2. Add managed PostgreSQL database
3. Configure environment variables
4. Set build and run commands
5. Deploy

## Database Setup

### Managed PostgreSQL (Recommended)

Use managed database services:
- AWS RDS
- Google Cloud SQL
- Azure Database for PostgreSQL
- DigitalOcean Managed Databases
- Heroku PostgreSQL

### Self-Hosted PostgreSQL

```bash
# Install PostgreSQL 16
sudo apt update
sudo apt install postgresql-16

# Create database and user
sudo -u postgres psql
CREATE DATABASE projecthub;
CREATE USER projecthub WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE projecthub TO projecthub;

# Enable SSL (recommended)
# Edit postgresql.conf:
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
```

### Running Migrations

```bash
# In Docker
docker compose -f compose.prod.yaml exec api uv run alembic upgrade head

# Standalone
uv run alembic upgrade head

# Check current version
uv run alembic current
```

## Reverse Proxy Setup

### Nginx

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Caddy (Automatic HTTPS)

```caddyfile
api.yourdomain.com {
    reverse_proxy localhost:8000
    
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
        X-XSS-Protection "1; mode=block"
    }
}
```

## Security Checklist

### Before Deployment

- [ ] Set `DEBUG=false`
- [ ] Generate strong `JWT_SECRET_KEY` (32+ chars)
- [ ] Use strong database password
- [ ] Enable PostgreSQL SSL
- [ ] Configure CORS for your frontend domain
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure security headers
- [ ] Enable rate limiting
- [ ] Review and secure environment variables
- [ ] Restrict database access (firewall rules)
- [ ] Enable database backups
- [ ] Set up monitoring and alerts
- [ ] Configure log aggregation
- [ ] Review exposed ports

### CORS Configuration

Add to `app/factory.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Monitoring

### Health Checks

The API provides a health endpoint:

```bash
curl https://api.yourdomain.com/api/v1/health
```

### Logging

ProjectHub uses structured JSON logging. Configure log aggregation:

- **AWS**: CloudWatch Logs
- **GCP**: Cloud Logging
- **Self-hosted**: ELK Stack, Loki, or Graylog

### Metrics

Recommended tools:
- **Prometheus** + **Grafana** for metrics
- **Sentry** for error tracking
- **Uptime monitoring**: Pingdom, UptimeRobot

## Backup and Recovery

### Database Backups

```bash
# Manual backup
docker compose exec postgres pg_dump -U projecthub projecthub > backup.sql

# Automated daily backups (cron)
0 2 * * * docker compose exec postgres pg_dump -U projecthub projecthub | gzip > /backups/projecthub_$(date +\%Y\%m\%d).sql.gz
```

### Restore from Backup

```bash
# Stop API
docker compose stop api

# Restore database
docker compose exec -T postgres psql -U projecthub projecthub < backup.sql

# Start API
docker compose start api
```

### Disaster Recovery

1. Keep automated daily backups (retention: 30 days)
2. Test restore procedure monthly
3. Store backups in different location/region
4. Document recovery procedures
5. Maintain backup of environment variables

## Performance Optimization

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_tasks_project_status 
  ON tasks(project_id, status);

CREATE INDEX CONCURRENTLY idx_project_members_user 
  ON project_members(user_id);

-- Enable connection pooling in SQLAlchemy
# In app/db/session.py, configure pool_size and max_overflow
```

### Application Optimization

- Enable Uvicorn workers: `--workers 4`
- Use production ASGI server (Gunicorn + Uvicorn)
- Configure database connection pooling
- Add Redis for caching (optional)
- Enable HTTP caching headers

## Scaling

### Horizontal Scaling

- Deploy multiple API instances behind load balancer
- Use managed PostgreSQL with read replicas
- Add Redis for session storage and caching
- Use CDN for static assets

### Load Balancer

```nginx
upstream projecthub_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    location / {
        proxy_pass http://projecthub_backend;
    }
}
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs api

# Verify environment variables
docker compose config

# Test database connection
docker compose exec postgres psql -U projecthub -d projecthub
```

### High Memory Usage

- Reduce Uvicorn workers
- Configure database connection pool limits
- Check for memory leaks in application code

### Slow Queries

```sql
-- Enable query logging in PostgreSQL
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s
SELECT pg_reload_conf();

-- View slow queries
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

## Support

For deployment issues, check:
1. Application logs: `docker compose logs api`
2. Database logs: `docker compose logs postgres`
3. Health endpoint: `/api/v1/health`
4. Open GitHub issue for help

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Nginx Optimization](https://www.nginx.com/blog/tuning-nginx/)
- [12-Factor App Methodology](https://12factor.net/)
