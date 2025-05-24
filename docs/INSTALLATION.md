# 🕉️ Installation Guide

Complete guide to set up the Hindu Scriptures Q&A System on your local machine or deploy to Streamlit Cloud.

## 📋 Prerequisites

- **Python 3.8+** (recommended: Python 3.9 or 3.10)
- **Git** (for cloning the repository)
- **Google API Key** (free from Google AI Studio)

## 🚀 Quick Installation

### Option 1: Automated Setup (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/SanatanaGPT.git
   cd SanatanaGPT
   ```

2. **Run the setup script:**
   ```bash
   python scripts/setup.py
   ```

3. **Add your Google API key to `.env` file:**
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

### Option 2: Manual Installation

1. **Clone and navigate:**
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
   cp config/env_example.txt .env
   ```

4. **Edit `.env` file and add your Google API key:**
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 🔑 Getting Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Add it to your `.env` file

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
   docker run -p 8501:8501 -e GOOGLE_API_KEY=your_key sanatana-gpt
   ```

## ☁️ Streamlit Cloud Deployment

### Prerequisites:
- GitHub account
- Google API key

### Steps:

1. **Fork/Clone this repository to your GitHub**

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Connect your GitHub account**

4. **Deploy new app:**
   - Repository: `your-username/SanatanaGPT`
   - Branch: `main`
   - Main file path: `app.py`

5. **Add secrets in Streamlit Cloud:**
   - Go to App Settings → Secrets
   - Add:
     ```toml
     GOOGLE_API_KEY = "your_actual_api_key_here"
     ```

6. **Your app will be live at:**
   `https://your-username-sanatanagpt-app-xyz123.streamlit.app/`

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

#### 4. Streamlit not starting
- **Solution:** Install Streamlit: `pip install streamlit`
- **Alternative:** Use the setup script: `python scripts/setup.py`

#### 5. API quota exceeded
- **Solution:** Check your Google API usage and billing settings
- **Alternative:** Wait for quota reset or upgrade your plan

### Performance Tips:

1. **Large text files:** Break them into smaller chapters/sections
2. **Slow responses:** Reduce the number of passages to analyze
3. **Memory issues:** Use smaller text files or restart the application

## 📱 System Requirements

### Minimum:
- **RAM:** 2GB
- **Storage:** 1GB free space
- **Internet:** Required for AI API calls

### Recommended:
- **RAM:** 4GB+
- **Storage:** 2GB+ free space
- **Internet:** Stable broadband connection

## 🆘 Getting Help

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Review the logs** in your terminal/command prompt
3. **Create an issue** on the GitHub repository
4. **Include:** Error messages, system info, and steps to reproduce

## 🔄 Updating

To update to the latest version:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

*🕉️ May your journey with Hindu scriptures be enlightening! 🕉️* 