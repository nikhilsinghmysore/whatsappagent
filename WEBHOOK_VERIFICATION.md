# WhatsApp Webhook Verification Guide

## Your Credentials ✅

```
Phone Number ID: 1334321436434182
Business Account ID: 1773667110450602
Verify Token: test-verify-token
App Secret: a3dee305c3a189c8f7a77415f39fd237
Access Token: EAAXRGAmh2PYBSsYEzlc8ebrmMwZCHQF9NcqingZCkzvwXfFhne1fXAeuF75zaprhkVfddIZAQINb8GIk2Pi9YVpfcJYZAZBkNHvmVxRoZAPbZB1pcl1ezGG2LNhvA2S8R8KRPJZCe02GR914FuKu1wze75zY40jl5bpAYZBhq9g73zC9MkH1Xe8ZAlZCNij3CzUHQBu3QZDZD
```

## Step 1: Verify Webhook with Meta

### In Meta Developers Console:

1. Go to **Developers.Facebook.com** → Your App
2. Select **WhatsApp** → **Configuration**
3. Under **Webhook URL**, enter your ngrok URL:
   ```
   https://nugget-symphonic-grab.ngrok-free.dev/webhook
   ```

4. **Verify Token:** `test-verify-token`

5. Click **Verify and Save**

Meta will send a GET request:
```
GET /webhook?hub.mode=subscribe&hub.challenge=xxx&hub.verify_token=test-verify-token
```

Your endpoint returns: `{"hub_challenge": "xxx"}`

### Test Locally:

```bash
curl -X GET "http://localhost:8000/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=test-verify-token"
```

Expected response:
```json
{"hub_challenge":"test123"}
```

---

## Step 2: Subscribe to Webhook Events

In Meta Console under **Webhook Fields**, subscribe to:

- ✅ **messages** - Receive incoming messages
- ✅ **message_status** - Track message delivery
- ✅ **message_template_status_update** - Template status

---

## Step 3: Test Message Sending

Your access token allows your app to:
- Send messages to users who messaged you
- Send template messages
- Send media (images, documents, etc.)

### Test sending a message:

```bash
curl -X POST "https://graph.instagram.com/v21.0/1334321436434182/messages" \
  -H "Authorization: Bearer EAAXRGAmh2PYBSsYEzlc8ebrmMwZCHQF9NcqingZCkzvwXfFhne1fXAeuF75zaprhkVfddIZAQINb8GIk2Pi9YVpfcJYZAZBkNHvmVxRoZAPbZB1pcl1ezGG2LNhvA2S8R8KRPJZCe02GR914FuKu1wze75zY40jl5bpAYZBhq9g73zC9MkH1Xe8ZAlZCNij3CzUHQBu3QZDZD" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "919999999999",
    "type": "text",
    "text": {
      "body": "Hello from Home Clinic!"
    }
  }'
```

---

## Step 4: Verify Webhook Signature

Your webhook verifies message authenticity using the app secret:

```python
import hmac
import hashlib

def verify_signature(body: str, signature: str, secret: str) -> bool:
    expected_signature = f"sha256={hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()}"
    return hmac.compare_digest(expected_signature, signature)

# Usage:
is_valid = verify_signature(request_body, x_hub_signature, "a3dee305c3a189c8f7a77415f39fd237")
```

Your app already does this in `src/api/webhook.py`

---

## Step 5: Configure Webhook in Meta Dashboard

1. **App Dashboard** → **WhatsApp** → **Configuration**
2. **Callback URL:** `https://nugget-symphonic-grab.ngrok-free.dev/webhook`
3. **Verify Token:** `test-verify-token`
4. **Webhook Fields:**
   - ✅ messages
   - ✅ message_status
   - ✅ message_template_status_update

5. Click **Verify and Save**

---

## Troubleshooting

### ❌ "Webhook verification failed"
- Check verify token matches exactly
- Verify ngrok tunnel is active
- Check app secret in .env

### ❌ "401 Unauthorized" sending messages
- Access token may have expired
- Regenerate token in Meta Console
- Update .env with new token

### ❌ No messages being received
- Webhook not subscribed to "messages" field
- Callback URL incorrect
- App not in Live mode yet

---

## Next: Submit for Meta Approval

Once webhook is verified and working:

1. Go to **Getting Started** in WhatsApp Console
2. Fill business information
3. Add Privacy Policy URL
4. Add Terms of Service URL
5. Submit for Review
6. Wait 1-2 hours for approval
7. Once Live, scan QR code to test!

---

## Credentials Security Notes

⚠️ **These credentials are currently for testing only**

When going live:
- ✅ Regenerate all tokens
- ✅ Use environment variables (do NOT hardcode)
- ✅ Rotate tokens quarterly
- ✅ Never commit .env to git
- ✅ Add .env to .gitignore

Your `.env` file is already gitignored ✅
