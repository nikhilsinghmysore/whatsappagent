# Home Clinic WhatsApp Booking Agent - Deployment & Launch Guide

**Status:** Ready for Meta Approval ✅

---

## Pre-Launch Checklist

### ✅ Backend Setup
- [x] FastAPI server running on port 8000
- [x] PostgreSQL database initialized (9 tables)
- [x] Redis cache configured
- [x] OpenAI integration active (gpt-4o-mini)
- [x] Webhook endpoint operational
- [x] ngrok tunnel active (HTTPS secure)

### ✅ AI Agent Features
- [x] Emergency keyword detection (fever, accident, etc.)
- [x] Multi-turn conversation support
- [x] Provider search functionality
- [x] Booking creation (with AI tool use)
- [x] Booking cancellation
- [x] Booking rescheduling
- [x] Human escalation

### ✅ Security
- [x] HTTPS encryption (ngrok)
- [x] Webhook signature verification
- [x] JWT authentication for admin API
- [x] Fernet encryption for sensitive data
- [x] Environment variable protection

### ✅ Documentation
- [x] Privacy Policy (500+ words)
- [x] Terms of Service (500+ words)
- [x] Webhook Verification Guide
- [x] API Documentation

---

## Step 1: Verify Current Configuration

### Check .env file:
```bash
grep -E "WHATSAPP|OPENAI" /Users/nikhilgsingh/whatsapp-booking-agent/.env
```

Expected output:
```
WHATSAPP_PHONE_NUMBER_ID=1334321436434182
WHATSAPP_BUSINESS_ACCOUNT_ID=1773667110450602
WHATSAPP_API_TOKEN=EAA...
WHATSAPP_VERIFY_TOKEN=test-verify-token
WHATSAPP_APP_SECRET=a3dee305c3a189c8f7a77415f39fd237
WHATSAPP_ACCESS_TOKEN=EAA...
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
```

### Check server status:
```bash
# Verify app is running
docker-compose ps

# Should show: homeclinic-app UP, db UP, redis UP
```

### Test webhook endpoint:
```bash
curl -v "https://nugget-symphonic-grab.ngrok-free.dev/webhook?hub_mode=subscribe&hub_challenge=test123&hub_verify_token=test-verify-token"

# Expected: 200 OK
# Response: {"hub_challenge":"test123"}
```

---

## Step 2: Submit to Meta for Approval

### A. Prepare Documents

Your documents are ready:
- `/PRIVACY_POLICY.md`
- `/TERMS_OF_SERVICE.md`

**Host them publicly:**

**Option 1: GitHub Pages**
```bash
1. Create /docs folder
2. Copy PRIVACY_POLICY.md and TERMS_OF_SERVICE.md
3. Enable GitHub Pages in repo settings
4. URLs:
   - https://youruser.github.io/whatsapp-booking-agent/privacy-policy
   - https://youruser.github.io/whatsapp-booking-agent/terms-of-service
```

**Option 2: Your Domain**
```
- https://yourdomain.com/privacy-policy
- https://yourdomain.com/terms-of-service
```

### B. Go to Meta Developers Console

1. **App Dashboard**
2. **Select Your App**
3. **Products** → **WhatsApp** → **Getting Started**
4. **Set up your WhatsApp Business Account**

### C. Fill in Required Information

| Field | Value |
|-------|-------|
| Business Name | Home Clinic |
| Business Email | your-email@homeclinic.com |
| Business Phone | +91-XXXX-XXXX-XXXX |
| Business Address | [Your Address] |
| Website | https://yourdomain.com (optional) |
| Privacy Policy URL | https://yourdomain.com/privacy-policy |
| Terms of Service URL | https://yourdomain.com/terms-of-service |
| Category | Healthcare |

### D. Webhook Configuration

In **App Setup** → **Webhook**:

1. **Callback URL:**
   ```
   https://nugget-symphonic-grab.ngrok-free.dev/webhook
   ```

2. **Verify Token:**
   ```
   test-verify-token
   ```

3. **Webhook Fields:** Subscribe to:
   - ✅ messages
   - ✅ message_status
   - ✅ message_template_status_update

4. Click **"Verify and Save"**

### E. Click "Submit for Review"

Meta will review:
- ✅ Your privacy policy
- ✅ Your terms of service
- ✅ Your webhook endpoint
- ✅ Your app functionality

**Typical approval time: 1-2 hours**

---

## Step 3: After Meta Approval (Status = "Live")

### A. Get Your QR Code

Once approved, in **Getting Started** tab:
- You'll see a **QR Code**
- This is your test WhatsApp number

### B. Test on WhatsApp

**From your real phone:**

1. Open **WhatsApp**
2. Tap **Camera icon** (top right)
3. **Scan the QR code** from Meta Dashboard
4. A chat opens with your booking agent

### C. Send Test Messages

```
User: "I need to book a doctor visit"
Agent: "Welcome! What's your name?"

User: "I have a fever and body ache"
Agent: "I understand. Would you like to book a doctor visit?"

User: "Yes, I'm in Bangalore"
Agent: "Great! What's your pin code?"
```

### D. Monitor Logs

```bash
docker-compose logs -f app | grep -E "Received|Processing|OpenAI"
```

---

## Step 4: Production Deployment

Once live and tested:

### A. Switch from ngrok to Production URL

1. Get a real domain or static IP
2. Update in Meta Dashboard:
   ```
   https://yourdomain.com/webhook
   ```
3. Update your server to handle HTTPS (use Let's Encrypt)

### B. Database Backup

```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U homeclinic homeclinic > backup.sql

# Restore if needed
docker-compose exec db psql -U homeclinic homeclinic < backup.sql
```

### C. Monitor Health

```bash
# Watch logs
docker-compose logs -f app

# Check database
docker-compose exec db psql -U homeclinic -d homeclinic -c "SELECT COUNT(*) FROM bookings;"

# Check Redis
docker-compose exec redis redis-cli INFO
```

### D. Security Hardening

- [ ] Rotate API tokens quarterly
- [ ] Enable rate limiting on webhook
- [ ] Set up monitoring/alerting
- [ ] Regular security audits
- [ ] Enable database backups
- [ ] Set up error logging (Sentry/LogRocket)

---

## Troubleshooting

### ❌ Webhook Verification Failed
**Solution:**
- Check verify token matches exactly
- Ensure ngrok tunnel is running
- Verify app is listening on port 8000

### ❌ Meta Says "App Not Approved"
**Solution:**
- Verify privacy policy URL is accessible
- Check terms of service URL works
- Ensure business info is complete and accurate
- Wait 24 hours and resubmit

### ❌ Messages Not Being Received
**Solution:**
- Check app is in "Live" mode (not Development)
- Verify webhook is subscribed to "messages" field
- Check .env has correct WHATSAPP_PHONE_NUMBER_ID

### ❌ Agent Not Responding
**Solution:**
- Check OpenAI API key is valid
- Verify database is running: `docker-compose ps`
- Check logs: `docker-compose logs app`
- Restart app: `docker-compose restart app`

---

## Support & Monitoring

### Logs
```bash
# All logs
docker-compose logs

# Only app
docker-compose logs app

# Last 50 lines
docker-compose logs -n 50

# Follow live
docker-compose logs -f
```

### Database Queries
```bash
# Connect to database
docker-compose exec db psql -U homeclinic -d homeclinic

# View bookings
SELECT * FROM bookings ORDER BY created_at DESC LIMIT 10;

# View conversations
SELECT * FROM conversations ORDER BY created_at DESC;

# View messages
SELECT * FROM messages WHERE wa_id = '919999999999' ORDER BY created_at DESC;
```

### API Health Check
```bash
curl http://localhost:8000/health

# Expected: {"status": "healthy"}
```

---

## Timeline

| Step | Status | Time |
|------|--------|------|
| Verify Configuration | ✅ Complete | 5 min |
| Host Privacy/Terms | ⏳ Pending | 10 min |
| Submit to Meta | ⏳ Pending | 5 min |
| Meta Review | ⏳ Pending | 1-2 hours |
| Test on WhatsApp | ⏳ Pending | 10 min |
| Production Deploy | ⏳ Pending | 30 min |

**Total Time: ~2 hours to go live! 🚀**

---

## Contact & Support

For issues or questions:
- **Meta Support:** https://developers.facebook.com/support
- **WhatsApp API Docs:** https://developers.facebook.com/docs/whatsapp/cloud-api/
- **Home Clinic Support:** support@homeclinic.local

---

**Congratulations! Your WhatsApp Booking Agent is ready for the world! 🎉**
