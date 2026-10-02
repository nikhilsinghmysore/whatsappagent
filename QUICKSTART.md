# Quick Start Guide

Get the Home Clinic WhatsApp Booking Agent running in 5 minutes.

## 1. Clone and Setup

```bash
git clone <repo> whatsapp-booking-agent
cd whatsapp-booking-agent
cp .env.example .env
```

## 2. Generate Secrets

```bash
# Encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# JWT secret
openssl rand -hex 32
```

Update `.env` with the generated values.

## 3. Configure WhatsApp

Go to [Meta Developers](https://developers.facebook.com/):

1. Create a **Business** app
2. Add **WhatsApp** product
3. Copy these to `.env`:
   - `WHATSAPP_PHONE_NUMBER_ID` (from Configuration)
   - `WHATSAPP_BUSINESS_ACCOUNT_ID` (from Configuration)
   - `WHATSAPP_API_TOKEN` (System User → Access Tokens)
   - `WHATSAPP_APP_SECRET` (Settings → Basic)
4. Create a `WHATSAPP_VERIFY_TOKEN`: `openssl rand -hex 16`

## 4. Get Anthropic API Key

Visit [console.anthropic.com](https://console.anthropic.com), create API key, add to `.env`.

## 5. Start Docker

```bash
docker-compose up -d
```

Wait 30 seconds for services to start.

## 6. Initialize Database

```bash
docker-compose exec app alembic upgrade head
docker-compose exec app python scripts/seed_providers.py
```

## 7. Test

```bash
# Health check
curl http://localhost:8000/health

# View logs
docker-compose logs -f app

# Simulate a message
docker-compose exec app python scripts/simulate_webhooks.py
```

## 8. Configure Webhook in Meta

1. Go to Meta Developers → Your App → WhatsApp → Configuration
2. **Callback URL**: For local testing, use ngrok:
   ```bash
   ngrok http 8000
   # Copy the forwarded URL, e.g., https://abc123.ngrok.io
   # Set webhook to: https://abc123.ngrok.io/webhook
   ```
3. **Verify Token**: The value from step 3
4. **Subscribe to**: `messages`, `message_status`

## 9. Test with WhatsApp

1. Go to Getting Started → Test
2. Scan QR code with WhatsApp
3. Send a test message
4. Check `docker-compose logs -f app` for response

## What's Included

✅ **Webhook Integration** — Receive & send WhatsApp messages  
✅ **Claude Agent** — AI booking assistant with tool use  
✅ **Database** — PostgreSQL with Alembic migrations  
✅ **Provider Management** — Register, approve, availability  
✅ **Booking State Machine** — Full lifecycle (requested → completed)  
✅ **Emergency Detection** — Auto-escalate on chest pain, breathing issues, etc.  
✅ **Admin API** — Manage bookings, providers, escalations  
✅ **Templates** — Confirmations, reminders, feedback requests  
✅ **DPDP Compliance** — Data deletion & export endpoints  
✅ **Background Tasks** — ARQ worker for reminders  
✅ **Tests** — Unit tests for tools, state machine, signatures  

## API Endpoints

### Webhook
- `GET /webhook` — Meta verification
- `POST /webhook` — Receive messages

### Health
- `GET /health` — App health

### Admin (pass `?token=<jwt>`)
- `POST /admin/providers/{id}/approve`
- `GET /admin/bookings`
- `GET /admin/conversations/{wa_id}`
- `POST /admin/conversations/{wa_id}/takeover`

### Privacy
- `POST /privacy/delete-patient-data` — Delete patient data (DPDP)
- `GET /privacy/data-export/{wa_id}` — Export patient data

## Generate Admin Token

```python
import jwt
from src.config import settings

token = jwt.encode(
    {"admin": True},
    settings.admin_jwt_secret,
    algorithm=settings.admin_jwt_algorithm,
)
print(token)
```

## Common Commands

```bash
# View logs
docker-compose logs -f app

# Run tests
docker-compose exec app pytest tests/

# Database shell
docker-compose exec db psql -U homeclinic -d homeclinic

# Worker logs
docker-compose logs -f worker

# Stop all services
docker-compose down

# Full reset (with data loss)
docker-compose down -v && docker-compose up -d
```

## Troubleshooting

**Webhook signature invalid?**
- Verify `WHATSAPP_APP_SECRET` matches Meta dashboard
- Check raw body is used for verification

**Claude API not responding?**
- Verify `ANTHROPIC_API_KEY` is set
- Check logs: `docker-compose logs app | grep Anthropic`

**Database connection failed?**
- Wait 30s for PostgreSQL to start
- Check: `docker-compose logs db`

**No response to messages?**
- Check WhatsApp webhook URL is accessible
- Verify verify token matches
- View logs: `docker-compose logs -f app`

## Next Steps

1. **Configure Message Templates** — Create in Meta for production
2. **Set Up Admin UI** — Build dashboard for provider management
3. **Add Rating System** — Collect feedback after bookings
4. **Set Availability** — Let providers set service hours
5. **Implement Payments** — Integrate payment gateway (optional)
6. **Go to Production** — Follow [DEPLOYMENT.md](DEPLOYMENT.md)

## Documentation

- [README.md](README.md) — Full project overview
- [DEPLOYMENT.md](DEPLOYMENT.md) — Production deployment
- [Architecture & Design](ARCHITECTURE.md) — System design (coming soon)

---

**Questions?** Check application logs: `docker-compose logs -f`
