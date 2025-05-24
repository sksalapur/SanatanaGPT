# 🕉️ SanatanaGPT - Hindu Scriptures Q&A System

An AI-powered question-answering system for Hindu scriptures, built with Streamlit and Google's Gemini AI. Ask questions about the Bhagavad Gita, Upanishads, Vedas, and other sacred texts in natural language.

## ✨ Features

- 🤖 **AI-Powered Q&A**: Ask questions about Hindu scriptures in natural language
- 📚 **Multiple Scripture Support**: Bhagavad Gita, Upanishads, Vedas, Puranas, and more
- 💬 **Conversation Management**: Create, save, and manage multiple conversations
- 🔗 **Shareable Links**: Generate links to share specific conversations
- 👤 **User Authentication**: Secure registration and login with email OTP verification
- 📊 **Source Citations**: See exact passages that answer your questions
- 🎯 **Balanced Search**: Intelligent distribution across different texts
- 📱 **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/SanatanaGPT.git
cd SanatanaGPT
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
```bash
cp env_example.txt .env
```

Edit `.env` and add your credentials:
```env
# Google Gemini AI API Key (Required)
GOOGLE_API_KEY=your_google_api_key_here

# Gmail Configuration for Email OTP (Required for user registration)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your.email@gmail.com
SENDER_PASSWORD=your_16_character_app_password_here
```

### 4. Run the Application
```bash
streamlit run app.py
```

## 🔑 Getting API Keys

### Google Gemini AI API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key to your `.env` file

### Gmail App Password (for OTP emails)
1. Enable 2-Factor Authentication on your Google account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Generate a new app password for "Mail"
4. Use this 16-character password in your `.env` file

## 📁 Project Structure

```
SanatanaGPT/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── env_example.txt            # Environment variables template
├── users_config.yaml          # User authentication config
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── hindu_texts/               # Scripture text files
│   ├── bhagavad_gita.txt
│   ├── upanishads.txt
│   └── ...
├── docs/                      # Documentation
│   ├── API_GUIDE.md          # API usage guide
│   └── INSTALLATION.md       # Detailed installation guide
├── config/                    # Configuration files
│   ├── secrets_template.toml # Streamlit secrets template
│   └── .streamlit/
│       └── config.toml       # Streamlit configuration
└── .devcontainer/            # VS Code dev container config
```

## 📚 Adding Scripture Texts

1. Place your Hindu scripture text files in the `hindu_texts/` directory
2. Use `.txt` format with UTF-8 encoding
3. Name files descriptively (e.g., `bhagavad_gita.txt`, `upanishads.txt`)

## ☁️ Deployment

### Streamlit Cloud
1. Fork this repository to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account and select your repository
4. Set main file as `app.py`
5. Add your environment variables in App Settings → Secrets:
   ```toml
   GOOGLE_API_KEY = "your_api_key_here"
   SENDER_EMAIL = "your.email@gmail.com"
   SENDER_PASSWORD = "your_app_password"
   ```

### Local Development
```bash
streamlit run app.py
```

## 🔧 Configuration

### Streamlit Configuration
The app includes optimized Streamlit settings in `config/.streamlit/config.toml`:
- Wide layout mode
- Dark theme
- Optimized caching
- Performance improvements

### User Authentication
- File-based user storage using `users_config.yaml`
- Email OTP verification for new registrations
- Secure password hashing with bcrypt
- Session-based authentication

## 🛠️ Development

### Requirements
- Python 3.8+
- Streamlit
- Google Generative AI
- Streamlit Authenticator
- Other dependencies in `requirements.txt`

### Key Components
- **Authentication**: User registration, login, OTP verification
- **Text Processing**: Scripture text loading and chunking
- **AI Integration**: Google Gemini API for Q&A
- **Conversation Management**: Save, load, and share conversations
- **UI/UX**: Responsive Streamlit interface

## 📖 Usage

1. **Register/Login**: Create an account or log in with existing credentials
2. **Ask Questions**: Type your question about Hindu scriptures
3. **Get Answers**: Receive AI-generated answers with source citations
4. **Manage Conversations**: Create, rename, and organize your conversations
5. **Share**: Generate shareable links for specific conversations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hindu Scriptures**: Ancient wisdom texts that inspire this project
- **Google Gemini AI**: Powerful AI capabilities for understanding and answering questions
- **Streamlit**: Amazing framework for building data applications
- **Open Source Community**: For the tools and libraries that make this possible

## 📞 Support

For support, please:
1. Check the [Installation Guide](docs/INSTALLATION.md)
2. Review the [API Guide](docs/API_GUIDE.md)
3. Create an issue on GitHub
4. Include error messages and system information

---

*🕉️ May this tool help you explore the profound wisdom of Hindu scriptures! 🕉️* 