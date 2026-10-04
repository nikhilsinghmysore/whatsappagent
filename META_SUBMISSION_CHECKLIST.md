# Meta WhatsApp App Submission Checklist

## Documents Created ✅
- [x] PRIVACY_POLICY.md (500+ words)
- [x] TERMS_OF_SERVICE.md (500+ words)

## Step 1: Host Your Documents

**Option A: GitHub (Recommended)**
```
1. Create a `docs/` folder in your repository
2. Add PRIVACY_POLICY.md and TERMS_OF_SERVICE.md
3. Get the raw URLs:
   - Privacy Policy: https://raw.githubusercontent.com/youruser/whatsapp-booking-agent/main/docs/PRIVACY_POLICY.md
   - Terms of Service: https://raw.githubusercontent.com/youruser/whatsapp-booking-agent/main/docs/TERMS_OF_SERVICE.md
```

**Option B: Web Host (Better for Meta)**
```
1. Upload to your website:
   - https://yourdomain.com/privacy-policy
   - https://yourdomain.com/terms-of-service
2. Make sure they're publicly accessible
3. Copy the full URLs
```

## Step 2: Submit to Meta

Go to **Meta Developers → Your App → WhatsApp → App Setup**

### Fill in the required fields:

1. **Business Name:** Home Clinic

2. **Privacy Policy URL:**
   ```
   https://yourdomain.com/privacy-policy
   (or your GitHub raw URL)
   ```

3. **Terms of Service URL:**
   ```
   https://yourdomain.com/terms-of-service
   (or your GitHub raw URL)
   ```

4. **Business Email:** your-email@homeclinic.com

5. **Business Phone:** +91-XXXX-XXXX-XXXX

6. **Business Address:**
   ```
   [Your Complete Address]
   [City, State, Postal Code]
   [Country]
   ```

7. **Website:** (Optional)
   ```
   https://yourdomain.com
   ```

8. **Description of Your App:**
   ```
   Home Clinic is a WhatsApp-based healthcare booking platform that 
   connects patients with healthcare providers for medical consultations 
   and services. Users can book appointments, manage their health information, 
   and communicate with providers through our AI-powered chatbot.
   ```

9. **Data You Access:**
   - ✅ Phone number
   - ✅ Name
   - ✅ Message content
   - ✅ Profile picture (if available)

10. **Third-party Services:**
    - OpenAI API (for AI processing)
    - PostgreSQL Database (for data storage)

### Step 3: Click "Submit for Review"

Meta will:
- Review your app (1-2 hours typically)
- Verify your privacy policy and terms
- Check your WhatsApp integration
- Approve and move you to **Live Mode**

### Step 4: After Approval ✅

1. Status changes to **"Live"**
2. QR Code appears in **Getting Started**
3. Scan QR code from WhatsApp
4. Test your booking agent with real messages!

---

## Quick Edits Needed in Your Documents

Update these placeholders:
- `[Your Business Address]` → Your actual address
- `privacy@homeclinic.local` → Your real email
- `support@homeclinic.local` → Your real support email
- `+91-XXXX-XXXX-XXXX` → Your real phone number
- `[Your Country/State]` → Your location

---

## Important Notes

✅ **Both documents are required by Meta**  
✅ **Must be publicly accessible URLs (not file paths)**  
✅ **Review for accuracy before submitting**  
✅ **Keep them updated as your business changes**  

Ready to submit? 🚀
