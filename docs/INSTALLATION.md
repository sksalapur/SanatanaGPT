# 🕉️ Installation & Deployment Guide

Complete guide to set up the Hindu Scriptures Q&A System on your local machine or deploy to Streamlit Cloud.

## 📋 Prerequisites

- **Python 3.8+** (recommended: Python 3.9 or 3.10)
- **Git** (for cloning the repository)
- **Google API Key** (free from Google AI Studio)
- **Gmail Account** (for email OTP functionality)

## 🚀 Quick Installation

### Option 1: Standard Setup (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/SanatanaGPT.git
   cd SanatanaGPT
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file:**
   ```bash
   cp env_example.txt .env
   ```

4. **Edit `.env` file and add your credentials:**
   ```env
   # Google Gemini AI API Key (Required)
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Gmail Configuration for Email OTP (Required for user registration)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your.email@gmail.com
   SENDER_PASSWORD=your_16_character_app_password_here
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 🔑 Getting Required Credentials

### Google Gemini AI API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Add it to your `.env` file

### Gmail App Password (for OTP emails)
1. **Enable 2-Factor Authentication** on your Google account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Select "Mail" as the app type
4. Generate a new 16-character app password
5. Use this password (not your regular Gmail password) in your `.env` file

## 📚 Adding Hindu Scripture Texts

The application comes with sample texts, but you can add your own:

1. **Supported formats:** `.txt` files with UTF-8 encoding
2. **Location:** Place files in the `hindu_texts/` directory
3. **Naming:** Use descriptive names like `bhagavad_gita.txt`, `upanishads.txt`

### Example file structure:
```
hindu_texts/
├── bhagavad_gita.txt
├── upanishads.txt
├── vedas.txt
├── puranas.txt
└── manusmriti.txt
```

## 🐳 Docker Installation (Optional)

If you prefer using Docker:

1. **Build the image:**
   ```bash
   docker build -t sanatana-gpt .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8501:8501 \
     -e GOOGLE_API_KEY=your_key \
     -e SENDER_EMAIL=your.email@gmail.com \
     -e SENDER_PASSWORD=your_app_password \
     sanatana-gpt
   ```

## 🔧 Troubleshooting

### Common Issues:

#### 1. "GOOGLE_API_KEY not found"
- **Solution:** Make sure you have a `.env` file with your API key
- **Check:** The `.env` file should be in the project root directory

#### 2. "No .txt files found"
- **Solution:** Add Hindu scripture text files to the `hindu_texts/` directory
- **Format:** Files must have `.txt` extension and UTF-8 encoding

#### 3. Import errors
- **Solution:** Install requirements: `pip install -r requirements.txt`
- **Check:** Make sure you're using Python 3.8+

#### 4. Email OTP not working
- **Solution:** Verify Gmail app password is correct (16 characters, no spaces)
- **Check:** Ensure 2-Factor Authentication is enabled on your Google account
- **Alternative:** Try generating a new app password

#### 5. Streamlit not starting
- **Solution:** Install Streamlit: `pip install streamlit`
- **Check:** Verify all dependencies are installed

#### 6. API quota exceeded
- **Solution:** Check your Google API usage and billing settings
- **Alternative:** Wait for quota reset or upgrade your plan

#### 7. User registration failing
- **Solution:** Check email configuration in `.env` file
- **Debug:** Look for error messages in the terminal/logs

#### 8. Conversation sharing not working
- **Solution:** Ensure the app is deployed and accessible via public URL
- **Check:** Verify conversation IDs are being generated correctly

### Performance Tips:

1. **Large text files:** Break them into smaller chapters/sections
2. **Slow responses:** Reduce the number of passages to analyze
3. **Memory issues:** Use smaller text files or restart the application
4. **Email delivery:** Check spam folder for OTP emails

## 📱 System Requirements

### Minimum:
- **RAM:** 2GB
- **Storage:** 1GB free space
- **Internet:** Required for AI API calls and email OTP

### Recommended:
- **RAM:** 4GB+
- **Storage:** 2GB+ free space
- **Internet:** Stable broadband connection

## 🔒 Security Considerations

### Local Development:
- Never commit your `.env` file to version control
- Use strong passwords for user accounts
- Keep your API keys secure

### Production Deployment:
- Use Streamlit Cloud secrets for sensitive data
- Enable HTTPS (automatic with Streamlit Cloud)
- Monitor API usage and costs
- Regularly update dependencies

## 🆘 Getting Help

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Review the logs** in your terminal/command prompt
3. **Test email configuration** using a simple SMTP test
4. **Verify API keys** are correctly set
5. **Create an issue** on the GitHub repository
6. **Include:** Error messages, system info, and steps to reproduce

## 🔄 Updating

To update to the latest version:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
streamlit run app.py
```

For Streamlit Cloud deployments, simply push your changes to GitHub and the app will auto-redeploy.

## ✨ Features After Setup

Once properly installed and deployed, your SanatanaGPT will have:

- 🤖 **AI-powered Q&A** about Hindu scriptures
- 👤 **User authentication** with email verification
- 💬 **Conversation management** with save/load functionality
- 🔗 **Shareable conversation links**
- 📚 **Source citations** with expandable details
- 📱 **Responsive design** for all devices
- 🔒 **Secure user data** storage

---

*🕉️ May your journey with Hindu scriptures be enlightening! 🕉️* 