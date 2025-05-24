# 📧 Email OTP Verification Setup Guide

## Overview
SanatanaGPT now includes email OTP (One-Time Password) verification for new user registrations. This ensures that only users with valid email addresses can create accounts.

## 🔧 Email Configuration

### For Local Development (.env file)

Create or update your `.env` file with the following email configuration:

```env
# Google API Key (existing)
GOOGLE_API_KEY=your_google_api_key_here

# Email Configuration for OTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your.email@gmail.com
SENDER_PASSWORD=your_app_password_here
```

### For Streamlit Cloud (Secrets)

In your Streamlit Cloud app settings, add these secrets:

```toml
# Google API Key (existing)
GOOGLE_API_KEY = "your_google_api_key_here"

# Email Configuration for OTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your.email@gmail.com"
SENDER_PASSWORD = "your_app_password_here"
```

## 📧 Gmail Setup (Recommended)

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to "Security"
3. Enable "2-Step Verification"

### Step 2: Generate App Password
1. In Google Account settings, go to "Security"
2. Under "2-Step Verification", click "App passwords"
3. Select "Mail" and "Other (custom name)"
4. Enter "SanatanaGPT" as the app name
5. Copy the generated 16-character password
6. Use this password as `SENDER_PASSWORD` (not your regular Gmail password)

### Step 3: Configure Email Settings
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your.gmail.address@gmail.com
SENDER_PASSWORD=your_16_character_app_password
```

## 🔧 Other Email Providers

### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your.email@outlook.com
SENDER_PASSWORD=your_password
```

### Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SENDER_EMAIL=your.email@yahoo.com
SENDER_PASSWORD=your_app_password
```

### Custom SMTP Server
```env
SMTP_SERVER=your.smtp.server.com
SMTP_PORT=587
SENDER_EMAIL=your.email@yourdomain.com
SENDER_PASSWORD=your_password
```

## 🚀 How It Works

### Registration Flow
1. **User Registration**: User fills out registration form
2. **Email Validation**: System validates email format
3. **Duplicate Check**: System checks for existing username/email
4. **OTP Generation**: 6-digit random code is generated
5. **Email Sending**: OTP is sent to user's email
6. **OTP Verification**: User enters code from email
7. **Account Creation**: Account is created after successful verification

### Security Features
- **OTP Expiration**: Codes expire after 10 minutes
- **Email Validation**: Proper email format validation
- **Duplicate Prevention**: Prevents duplicate usernames and emails
- **Secure Storage**: Temporary storage of pending registrations
- **Resend Functionality**: Users can request new codes

## 📱 User Experience

### Email Template
Users receive a beautifully formatted email:

```
🙏 Namaste [Name]!

Welcome to SanatanaGPT - Your Personal Guide to Hindu Wisdom!

Your email verification code is: 123456

This code will expire in 10 minutes for security purposes.

If you didn't request this verification, please ignore this email.

🕉️ May your journey through Hindu scriptures bring you wisdom and peace.

With blessings,
The SanatanaGPT Team
```

### Registration Steps
1. Fill registration form
2. Click "📧 Send Verification Code"
3. Check email for 6-digit code
4. Enter code in verification form
5. Click "✅ Verify & Create Account"
6. Account created successfully!

## 🛠️ Troubleshooting

### Common Issues

#### "Email service not configured"
- **Cause**: Missing email credentials in environment variables
- **Solution**: Add `SENDER_EMAIL` and `SENDER_PASSWORD` to your .env file or Streamlit secrets

#### "Failed to send email: Authentication failed"
- **Cause**: Incorrect email credentials or app password
- **Solution**: 
  - For Gmail: Use app password, not regular password
  - Ensure 2FA is enabled for Gmail
  - Double-check email and password

#### "Invalid email format"
- **Cause**: User entered invalid email address
- **Solution**: User should enter a valid email format (user@domain.com)

#### "OTP has expired"
- **Cause**: User took more than 10 minutes to enter OTP
- **Solution**: Click "🔄 Resend Code" to get a new OTP

#### "Username already exists" / "Email already registered"
- **Cause**: User trying to register with existing credentials
- **Solution**: Use different username or email, or login with existing account

### Testing Email Functionality

Create a test script to verify email sending:

```python
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()

def test_email():
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        print("❌ Email credentials not found")
        return
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            print("✅ Email authentication successful!")
    except Exception as e:
        print(f"❌ Email test failed: {e}")

if __name__ == "__main__":
    test_email()
```

## 🔒 Security Considerations

### Best Practices
- **App Passwords**: Always use app passwords for Gmail, never regular passwords
- **Environment Variables**: Never commit email credentials to version control
- **HTTPS**: Ensure your app runs over HTTPS in production
- **Rate Limiting**: Consider implementing rate limiting for OTP requests
- **Logging**: Log OTP attempts for security monitoring

### Privacy
- **Data Protection**: User emails are stored securely
- **Temporary Storage**: OTP data is automatically cleaned up
- **No Spam**: Only verification emails are sent, no marketing

## 📊 Monitoring

### Success Metrics
- Registration completion rate
- Email delivery success rate
- OTP verification success rate
- Time to complete registration

### Error Tracking
- Failed email sends
- Expired OTPs
- Invalid email formats
- Duplicate registration attempts

## 🎯 Future Enhancements

### Planned Features
- **SMS OTP**: Alternative verification via SMS
- **Social Login**: Google/Facebook authentication
- **Email Templates**: Customizable email designs
- **Multi-language**: OTP emails in multiple languages
- **Admin Dashboard**: User registration analytics

### Configuration Options
- **OTP Length**: Configurable code length (4-8 digits)
- **Expiration Time**: Configurable OTP expiration (5-30 minutes)
- **Retry Limits**: Maximum OTP requests per email
- **Email Provider**: Support for more email services

---

**🕉️ Enjoy secure and verified access to Hindu wisdom with SanatanaGPT! 🕉️** 