# Home Clinic WhatsApp Booking Agent

A production-ready WhatsApp booking agent for "Home Clinic", a home healthcare aggregator platform in Mysuru, India. Doctors and nurses (independent partners) visit patients at home. Home Clinic only connects patients and providers and does not give medical care.

## Tech Stack

- **Python 3.12**, FastAPI, async everywhere
- **PostgreSQL** with SQLAlchemy 2.0 and Alembic migrations
- **Redis** for job queue (ARQ), dedup, and rate limiting
- **WhatsApp Cloud API** (Meta Graph API)
- **Google Gemini API** with tool use for the agent
- **Docker** and docker-compose for local dev

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- A WhatsApp Business Account (Meta Business Platform)
- Google Gemini API key

### 2. Clone and Setup

```bash
git clone <repo> whatsapp-booking-agent
cd whatsapp-booking-agent
cp .env.example .env
```

### 3. Configure .env

Edit `.env` with your actual values:

```bash
# WhatsApp (from Meta Business Platform)
WHATSAPP_PHONE_NUMBER_ID=<your-phone-number-id>
WHATSAPP_BUSINESS_ACCOUNT_ID=<your-biz-account-id>
WHATSAPP_API_TOKEN=<your-graph-api-token>
WHATSAPP_VERIFY_TOKEN=<generate-a-random-string>
WHATSAPP_APP_SECRET=<your-app-secret>

# Gemini
GOOGLE_GENERATIVEAI_API_KEY=<your-api-key>

# Encryption (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
FERNET_KEY=<generated-key>

# Admin JWT (openssl rand -hex 32)
ADMIN_JWT_SECRET=<generated-secret>
```

### 4. Start Docker

```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI app (port 8000)
- ARQ worker

### 5. Initialize Database

```bash
docker-compose exec app alembic upgrade head
docker-compose exec app python scripts/seed_providers.py
```

### 6. Test Locally

The app is now running at `http://localhost:8000`.

- **Health check**: `curl http://localhost:8000/health`
- **Root**: `curl http://localhost:8000/`

## WhatsApp Integration Setup

### Step 1: Create Meta App

1. Go to [Meta Developers](https://developers.facebook.com/)
2. Create a new app → **Business**
3. Add **WhatsApp** product

### Step 2: Get Credentials

1. In **WhatsApp** → **Configuration**:
   - Copy `Phone Number ID`, `Business Account ID`, `Graph API Token`, `App Secret`
2. In **Settings** → **Basic**:
   - Copy `App Secret` (again, for verification)

### Step 3: Webhook Setup

1. In **WhatsApp** → **Configuration** → **Webhooks**:
   - **Callback URL**: `https://<your-domain>/webhook` (use ngrok locally)
   - **Verify Token**: The value you set in `.env` as `WHATSAPP_VERIFY_TOKEN`
   - **Subscribe to fields**: `messages`, `message_status`, `message_template_status_update`

### Step 4: Test Number (Sandbox)

1. In **WhatsApp** → **Getting started**:
   - Find the **Test** section
   - Scan QR code with WhatsApp to add your number
   - Send a message to the test number

### Step 5: Production System User Token

For production, get a permanent token:

1. Go to **Settings** → **Business accounts**
2. Create a **System User** with **Admin** role
3. Generate an access token (never expires if done right)
4. Add it to `.env`

### Step 6: Production Message Templates

1. In **WhatsApp** → **Message Templates**:
   - Create approved templates:
     - `booking_confirmation`
     - `visit_reminder`
     - `provider_new_request`
     - `provider_on_the_way`
     - `feedback_request`

## Local Testing with ngrok

Use ngrok to expose your local server:

```bash
ngrok http 8000
```

Copy the ngrok URL and use it in the webhook callback URL above.

## Project Structure

```
whatsapp-booking-agent/
├── alembic/                   # Database migrations
├── src/
│   ├── api/                   # FastAPI endpoints (webhook, health, admin)
│   ├── agent/                 # Claude agent with tools
│   ├── whatsapp/              # WhatsApp Cloud API client
│   ├── models/                # SQLAlchemy models
│   ├── services/              # Business logic (booking, provider, messaging)
│   ├── workers/               # Background tasks (ARQ)
│   ├── db/                    # Database connection
│   ├── utils/                 # Encryption, logging, middleware
│   └── config.py, main.py
├── tests/
├── scripts/                   # Seed data, webhook simulation
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## API Endpoints

### Webhook

- `GET /webhook` — Meta verification handshake
- `POST /webhook` — Receive messages and status updates

### Health

- `GET /health` — Health check

### Admin (requires JWT token)

- `POST /admin/providers/{id}/approve`
- `GET /admin/bookings`
- `GET /admin/conversations/{wa_id}`
- `POST /admin/conversations/{wa_id}/takeover`

## Testing

Run tests:

```bash
docker-compose exec app pytest tests/
```

Simulate incoming webhooks:

```bash
docker-compose exec app python scripts/simulate_webhooks.py
```

## Database Migrations

Create a new migration:

```bash
docker-compose exec app alembic revision --autogenerate -m "Description"
```

Apply migrations:

```bash
docker-compose exec app alembic upgrade head
```

## Logging

Logs are streamed to stdout. Check them:

```bash
docker-compose logs -f app
docker-compose logs -f worker
```

## Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Use permanent System User token for WhatsApp
- [ ] Set up message templates in Meta Business Platform
- [ ] Configure PostgreSQL with a strong password
- [ ] Use a Redis cluster (not single instance)
- [ ] Set up rate limiting per user
- [ ] Add monitoring/alerting for webhook failures
- [ ] Encrypt sensitive fields at rest
- [ ] Add data deletion endpoint (DPDP Act compliance)
- [ ] Test emergency escalation flow
- [ ] Set up human handoff admin interface

## Architecture Notes

### Async & FastAPI

All operations are async using `httpx.AsyncClient` and async context managers.

### Webhook Deduplication

Messages are deduplicated by `message.id` (Meta retries). Database-level unique constraint prevents duplicates.

### Conversation State

Stored in Postgres with a hot cache in Redis (keyed by `wa_id`). Old turns are trimmed; summarization TBD.

### Agent Tools

Claude has access to:
- `search_providers` — Find providers by service type and location
- `create_booking` — Create a new booking
- `get_booking` — Retrieve booking status
- `cancel_booking` — Cancel a booking
- `reschedule_booking` — Reschedule a booking
- `escalate_to_human` — Hand off to human admin

### 24-Hour Window

Messages outside Meta's 24-hour customer service window must use approved templates.

### Rate Limiting

Throttled to ~1 message per 6 seconds per user. Retries use exponential backoff on 429/5xx.

## Support & Contribution

For issues, bugs, or feature requests, open an issue on GitHub.

---

**Disclaimer**: Home Clinic is a booking platform. Services are provided by independent doctors/nurses.
