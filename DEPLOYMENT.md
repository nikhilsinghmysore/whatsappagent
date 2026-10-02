# Deployment Guide

## Local Development Setup

### Prerequisites

- Docker & Docker Compose installed
- Python 3.12+ (for local testing)
- ngrok (for local testing with Meta)

### Step 1: Clone & Setup

```bash
git clone <repo> && cd whatsapp-booking-agent
cp .env.example .env
```

### Step 2: Generate Secrets

```bash
# Generate Fernet key for encryption
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate JWT secret
openssl rand -hex 32

# Add to .env
FERNET_KEY=<generated-fernet-key>
ADMIN_JWT_SECRET=<generated-jwt-secret>
```

### Step 3: Get WhatsApp Credentials

1. Go to [Meta Developers](https://developers.facebook.com/)
2. Create a Business app
3. Add WhatsApp product
4. Get credentials from **Configuration**:
   - `WHATSAPP_PHONE_NUMBER_ID`
   - `WHATSAPP_BUSINESS_ACCOUNT_ID`
   - `WHATSAPP_API_TOKEN` (from **System User** → **Access Tokens**)
   - `WHATSAPP_APP_SECRET` (from **Settings** → **Basic**)
5. Generate `WHATSAPP_VERIFY_TOKEN` (random string): `openssl rand -hex 16`

### Step 4: Get Anthropic API Key

Visit [console.anthropic.com](https://console.anthropic.com) and create an API key.

### Step 5: Start Docker

```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI app (port 8000)
- ARQ worker

### Step 6: Initialize Database

```bash
docker-compose exec app alembic upgrade head
docker-compose exec app python scripts/seed_providers.py
```

### Step 7: Test Locally

```bash
# Health check
curl http://localhost:8000/health

# Simulate webhooks
docker-compose exec app python scripts/simulate_webhooks.py

# Run tests
docker-compose exec app pytest tests/
```

---

## Local Testing with Meta Webhooks

### Using ngrok

```bash
ngrok http 8000
# Copy ngrok URL (e.g., https://abc123.ngrok.io)
```

### Configure Meta Webhook

1. Go to Meta Developers → Your App → WhatsApp → Configuration
2. Set **Callback URL**: `https://<your-ngrok-url>/webhook`
3. Set **Verify Token**: The value you set in `.env`
4. Subscribe to: `messages`, `message_status`, `message_template_status_update`

### Test with WhatsApp Test Number

1. In WhatsApp Getting Started, scan the QR code
2. Send a test message
3. Check `docker-compose logs -f app` for logs

---

## Production Deployment

### Prerequisites

- Kubernetes cluster or Docker-based hosting (e.g., AWS ECS, Railway, Fly.io)
- PostgreSQL managed service (AWS RDS, Heroku Postgres, etc.)
- Redis managed service (AWS ElastiCache, Upstash, etc.)
- Meta system user token (never expires)

### Environment Setup

Create `.env.production`:

```bash
DEBUG=false
ENVIRONMENT=production

# Database (use managed service)
DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/homeclinic
DATABASE_ECHO=false

# Redis (use managed service)
REDIS_URL=redis://user:pass@prod-redis.example.com:6379

# WhatsApp (from Meta, tested on production account)
WHATSAPP_API_TOKEN=<permanent-system-user-token>
WHATSAPP_PHONE_NUMBER_ID=<prod-phone-id>
WHATSAPP_APP_SECRET=<prod-app-secret>

# Anthropic
ANTHROPIC_API_KEY=<api-key>

# Encryption
FERNET_KEY=<strong-key>

# Admin
ADMIN_JWT_SECRET=<strong-secret>

# Alerts
EMERGENCY_ESCALATION_EMAIL=oncall@homeclinic.com
```

### Database Migrations

```bash
# Run migrations before deploying
python -m alembic upgrade head
```

### Docker Image

```bash
docker build -t homeclinic-agent:latest .
docker push <registry>/homeclinic-agent:latest
```

### Deployment to Kubernetes

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: homeclinic-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: homeclinic-agent
  template:
    metadata:
      labels:
        app: homeclinic-agent
    spec:
      containers:
      - name: app
        image: homeclinic-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: homeclinic-secrets
              key: database-url
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: homeclinic-secrets
              key: anthropic-key
        # ... other env vars
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      - name: worker
        image: homeclinic-agent:latest
        command: ["python", "-m", "src.workers.run_worker"]
        env:
        # Same env vars as app
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: homeclinic-agent-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: homeclinic-agent
```

Deploy:

```bash
kubectl apply -f k8s/
```

### Environment Variables for Production

Set these securely in your hosting platform:

```
DEBUG=false
DATABASE_URL=<prod-db>
REDIS_URL=<prod-redis>
WHATSAPP_API_TOKEN=<system-user-token>
ANTHROPIC_API_KEY=<api-key>
FERNET_KEY=<encryption-key>
ADMIN_JWT_SECRET=<jwt-secret>
LOG_LEVEL=info
```

---

## Monitoring & Logging

### Application Logs

```bash
# View app logs
docker-compose logs -f app

# View worker logs
docker-compose logs -f worker
```

### Health Checks

```bash
curl https://your-domain/health
```

### Database Backups

For PostgreSQL:

```bash
# Local backup
pg_dump -h localhost -U homeclinic homeclinic > backup.sql

# Restore
psql -h localhost -U homeclinic homeclinic < backup.sql
```

### ARQ Worker Monitoring

Monitor via Redis:

```bash
redis-cli
> KEYS arq:*
> GET arq:job:<job-id>
```

---

## Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Use managed PostgreSQL with backups enabled
- [ ] Use managed Redis with persistence
- [ ] Set up SSL/TLS certificates
- [ ] Configure DNS for webhook domain
- [ ] Set permanent WhatsApp system user token
- [ ] Create message templates in Meta (booking_confirmation, etc.)
- [ ] Set up email alerts for emergency escalations
- [ ] Enable database query logging (slow queries)
- [ ] Set up APM (Application Performance Monitoring)
- [ ] Configure rate limiting (1 message per 6 seconds per user)
- [ ] Add CORS headers for webhook domain only
- [ ] Test emergency flow (call 108 escalation)
- [ ] Test data deletion (DPDP Act)
- [ ] Set up provider verification workflow
- [ ] Configure admin access control
- [ ] Test backup & restore process
- [ ] Load test with 1000+ concurrent users
- [ ] Plan for graceful shutdown (ongoing requests handled)

---

## Troubleshooting

### Database Connection Failed

```bash
# Check PostgreSQL is running
docker-compose logs db

# Check connection string
echo $DATABASE_URL
```

### Webhook Signature Verification Failed

```
❌ Invalid signature received
```

- Verify `WHATSAPP_APP_SECRET` matches Meta dashboard
- Check raw request body is used for verification (not parsed JSON)

### Claude API Errors

```
Error: Anthropic API key invalid
```

- Verify `ANTHROPIC_API_KEY` is set correctly
- Check API key is not revoked in console.anthropic.com
- Verify network access to api.anthropic.com

### WhatsApp Message Sending Failed

```
429 Too Many Requests
```

- Rate limiting: Back off and retry with exponential backoff
- Verify `WHATSAPP_API_TOKEN` has right permissions

### Worker Not Processing Tasks

```bash
# Check Redis connection
redis-cli ping

# Check worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker
```

---

## Scaling Considerations

1. **Database**: Use read replicas for analytics
2. **Redis**: Use Redis Cluster for high throughput
3. **Workers**: Scale horizontally (multiple ARQ workers)
4. **API**: Use load balancer (Nginx, HAProxy)
5. **Message Queue**: Add retry logic & dead-letter queue

---

## Security Best Practices

1. **Secrets**: Never commit .env; use secret managers
2. **HTTPS**: Always use HTTPS for webhooks
3. **Encryption**: Encrypt sensitive fields at rest & in transit
4. **Rate Limiting**: Implement per-user rate limits
5. **Logging**: Don't log message bodies in production
6. **CORS**: Restrict to known domains only
7. **JWT**: Rotate secrets regularly
8. **DB**: Use parameterized queries (SQLAlchemy ORM does this)

---

## Support

For issues or questions, check:
- Application logs: `docker-compose logs`
- Database logs: `docker-compose logs db`
- Worker logs: `docker-compose logs worker`
- Meta webhook status: Meta Developers → Webhooks
