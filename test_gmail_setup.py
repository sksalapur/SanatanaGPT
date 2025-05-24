#!/usr/bin/env python3
"""
Gmail Setup Test Script for SanatanaGPT
This script tests your Gmail configuration before using it in the main app.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gmail_connection():
    """Test Gmail SMTP connection and authentication."""
    print("🔧 Testing Gmail Configuration for SanatanaGPT...")
    print("=" * 50)
    
    # Get configuration from environment
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    # Check if all required variables are present
    print("📋 Configuration Check:")
    print(f"   SMTP Server: {smtp_server}")
    print(f"   SMTP Port: {smtp_port}")
    print(f"   Sender Email: {sender_email if sender_email else '❌ NOT SET'}")
    print(f"   Sender Password: {'✅ SET' if sender_password else '❌ NOT SET'}")
    print()
    
    if not sender_email or not sender_password:
        print("❌ ERROR: Missing email credentials!")
        print("Please set SENDER_EMAIL and SENDER_PASSWORD in your .env file")
        return False
    
    # Test SMTP connection
    try:
        print("🔌 Testing SMTP Connection...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("   ✅ Connected to Gmail SMTP server")
            
            print("🔐 Starting TLS encryption...")
            server.starttls()
            print("   ✅ TLS encryption enabled")
            
            print("🔑 Testing authentication...")
            server.login(sender_email, sender_password)
            print("   ✅ Authentication successful!")
            
        print()
        print("🎉 Gmail configuration is working perfectly!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication failed: {e}")
        print()
        print("🔧 Troubleshooting Tips:")
        print("   1. Make sure you're using an App Password, not your regular Gmail password")
        print("   2. Ensure 2-Factor Authentication is enabled on your Google account")
        print("   3. Double-check the app password (16 characters, no spaces)")
        print("   4. Try generating a new app password")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"   ❌ Connection failed: {e}")
        print()
        print("🔧 Troubleshooting Tips:")
        print("   1. Check your internet connection")
        print("   2. Verify SMTP server and port settings")
        print("   3. Check if your firewall is blocking the connection")
        return False
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def send_test_email():
    """Send a test email to verify everything works."""
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        print("❌ Cannot send test email: Missing credentials")
        return False
    
    # Get recipient email
    recipient = input(f"\n📧 Enter email address to send test email (or press Enter to send to {sender_email}): ").strip()
    if not recipient:
        recipient = sender_email
    
    try:
        print(f"📤 Sending test email to {recipient}...")
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = "🕉️ SanatanaGPT - Gmail Setup Test"
        
        # Email body
        body = f"""
🙏 Namaste!

This is a test email from SanatanaGPT to verify your Gmail configuration is working correctly.

✅ Gmail SMTP connection: SUCCESS
✅ Authentication: SUCCESS  
✅ Email sending: SUCCESS

Your email setup is ready for OTP verification!

🕉️ May your journey through Hindu scriptures bring you wisdom and peace.

With blessings,
The SanatanaGPT Team

---
Sent from: {sender_email}
Test time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        print("   ✅ Test email sent successfully!")
        print(f"   📬 Check {recipient} for the test email")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to send test email: {e}")
        return False

def main():
    """Main test function."""
    print("🕉️ SanatanaGPT Gmail Setup Test")
    print("=" * 40)
    print()
    
    # Test connection first
    if test_gmail_connection():
        print()
        send_test = input("Would you like to send a test email? (y/n): ").lower().strip()
        if send_test in ['y', 'yes']:
            send_test_email()
    
    print()
    print("📚 For detailed setup instructions, see EMAIL_SETUP.md")
    print("🔧 If you encounter issues, check the troubleshooting section")

if __name__ == "__main__":
    main() 