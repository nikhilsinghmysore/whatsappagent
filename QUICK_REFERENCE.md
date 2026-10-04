# Home Clinic WhatsApp Booking Agent - Quick Reference

## 🚀 Ready to Launch? Follow This Order:

### 1️⃣ **Read:** DEPLOYMENT_LAUNCH_GUIDE.md
→ Understand the full process (5 min read)

### 2️⃣ **Verify:** Test Webhook Locally
```bash
curl -X GET "http://localhost:8000/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=test-verify-token"
# Expected: {"hub_challenge":"test123"}
```

### 3️⃣ **Host:** Privacy Policy & Terms
- Upload `PRIVACY_POLICY.md` to your domain
- Upload `TERMS_OF_SERVICE.md` to your domain
- Get public URLs for both

### 4️⃣ **Submit:** Go to Meta Developers
1. App → WhatsApp → Getting Started
2. Fill business info
3. Paste Privacy Policy URL
4. Paste Terms of Service URL
5. Click "Submit for Review"

### 5️⃣ **Wait:** Meta Approval (1-2 hours)

### 6️⃣ **Test:** Scan QR Code & Message

### 7️⃣ **Monitor:** Watch Logs
```bash
docker-compose logs -f app | grep -i "received\|openai"
```

---

## 📋 Your Credentials (Already in .env)

```
Phone ID: 1334321436434182
Business ID: 1773667110450602
Verify Token: test-verify-token
App Secret: a3dee305c3a189c8f7a77415f39fd237
Access Token: EAAXRGAmh2PYBSsYEzlc8ebrmMwZCHQF9NcqingZCkzvwXfFhne1fXAeuF75zaprhkVfddIZAQINb8GIk2Pi9YVpfcJYZAZBkNHvmVxRoZAPbZB1pcl1ezGG2LNhvA2S8R8KRPJZCe02GR914FuKu1wze75zY40jl5bpAYZBhq9g73zC9MkH1Xe8ZAlZCNij3CzUHQBu3QZDZD
```

---

## 🔧 Core Files Structure

```
whatsapp-booking-agent/
├── .env                              ← Your credentials (SECRET!)
├── docker-compose.yml               ← Services: app, db, redis
├── src/
│   ├── api/webhook.py              ← Receives WhatsApp messages
│   ├── agent/claude.py             ← OpenAI integration & tools
│   ├── agent/tools.py              ← Booking operations
│   └── models/                      ← Database schemas
├── PRIVACY_POLICY.md                ← For Meta submission
├── TERMS_OF_SERVICE.md              ← For Meta submission
├── DEPLOYMENT_LAUNCH_GUIDE.md       ← Step-by-step guide
├── WEBHOOK_VERIFICATION.md          ← Technical details
└── META_SUBMISSION_CHECKLIST.md     ← What to add where
```

---

## 📊 System Status

| Component | Status | Port |
|-----------|--------|------|
| FastAPI App | ✅ Running | 8000 |
| PostgreSQL | ✅ Running | 5432 |
| Redis | ✅ Running | 6379 |
| ngrok Tunnel | ✅ Active | HTTPS |
| OpenAI API | ✅ Connected | API |
| Webhook | ✅ Verified | /webhook |

---

## 🧪 Quick Tests

### Test 1: Webhook
```bash
curl -v "https://nugget-symphonic-grab.ngrok-free.dev/webhook?hub_mode=subscribe&hub_challenge=test123&hub_verify_token=test-verify-token"
# Expected: 200 OK
```

### Test 2: Send Message
```bash
python3 test_webhook.py 919999999999 "I need to book a doctor"
# Expected: status 200, {"status":"ok"}
```

### Test 3: Check Database
```bash
docker-compose exec db psql -U homeclinic -d homeclinic -c "SELECT COUNT(*) FROM messages;"
```

### Test 4: View Logs
```bash
docker-compose logs app --tail=20
```

---

## 📱 Expected Conversation Flow

```
User: "I need to book a doctor"
Agent: "Welcome! What's your name?"

User: "John Smith"
Agent: "Nice to meet you, John! What's your main concern?"

User: "I have a fever"
Agent: "I'm sorry to hear that. What's your location/pin code?"

User: "560001"
Agent: "Great! Let me search for available doctors in your area..."

Agent: "Here are 3 available doctors. Which one would you like to book?"

User: "Dr. Sharma"
Agent: "Perfect! When would you like to schedule? (Date and time)"

User: "Tomorrow 10 AM"
Agent: "Booking confirmed! Your appointment is scheduled for tomorrow at 10 AM with Dr. Sharma."
```

---

## 🚨 Emergency Keywords Detected

If user mentions:
- "accident", "emergency", "help", "serious", "critical"
- "bleeding", "chest pain", "shortness of breath"
- "ambulance", "hospital", "severe"

**Agent automatically:**
1. ⚠️ Flags as emergency
2. 🚑 Says: "Please call 108 immediately or go to nearest hospital"
3. 📢 Escalates to human admin
4. 📧 Sends alert email

---

## 💻 Useful Commands

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f app

# Restart app
docker-compose restart app

# Connect to database
docker-compose exec db psql -U homeclinic -d homeclinic

# Test webhook
python3 test_webhook.py <wa_id> "<message>"

# Check running services
docker-compose ps
```

---

## ⏰ Timeline to Live

| Task | Time | Status |
|------|------|--------|
| Setup & Config | ✅ Done | 0 min |
| Verify Credentials | ✅ Done | 0 min |
| Host Documentation | ⏳ 10 min | Next |
| Submit to Meta | ⏳ 5 min | Next |
| Meta Review | ⏳ 1-2 hrs | Waiting |
| Test on WhatsApp | ⏳ 10 min | After approval |
| **Total Time** | **~2 hours** | 🚀 |

---

## ✅ Checklist Before Launch

- [ ] Privacy Policy URL is public and accessible
- [ ] Terms of Service URL is public and accessible
- [ ] .env file has all credentials filled
- [ ] Docker containers are running (docker-compose ps)
- [ ] Webhook test passes (curl command above)
- [ ] OpenAI API key is valid
- [ ] Business name, email, phone added to Meta
- [ ] Submitted for Meta review
- [ ] Waiting for approval (check every 15 min)
- [ ] Once approved, scanned QR code
- [ ] Sent first test message to agent
- [ ] Agent responded with welcome message
- [ ] Logs show messages being processed

---

## 🆘 Emergency Help

**Webhook not working?**
```bash
# Check if running
docker-compose logs app | grep webhook

# Check ngrok status
curl https://nugget-symphonic-grab.ngrok-free.dev/
```

**Agent not responding?**
```bash
# Check OpenAI
docker-compose logs app | grep OpenAI

# Check database
docker-compose exec db psql -U homeclinic -d homeclinic -c "SELECT * FROM conversations LIMIT 1;"
```

**Messages not saving?**
```bash
# Check database connection
docker-compose logs app | grep DATABASE

# Restart database
docker-compose restart db
docker-compose restart app
```

---

## 📞 Support Resources

- **Meta WhatsApp Docs:** https://developers.facebook.com/docs/whatsapp/
- **OpenAI API:** https://platform.openai.com/docs
- **FastAPI:** https://fastapi.tiangolo.com
- **PostgreSQL:** https://www.postgresql.org/docs

---

**🎉 You're 2 hours away from a live WhatsApp booking agent! Let's go! 🚀**
