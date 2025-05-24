# 🕉️ Hindu Scriptures Q&A System

A beautiful and intelligent web application that allows you to ask questions about Hindu scriptures and get AI-powered answers based on your text collection.

## ✨ Features

- **🤖 AI-Powered Answers**: Uses Google Gemini AI to provide intelligent responses
- **📚 Multiple Scripture Support**: Load multiple Hindu text files (.txt format)
- **🔍 Smart Search**: Finds relevant passages using advanced text matching
- **🎨 Beautiful Interface**: Clean, modern Streamlit web interface
- **⚡ Fast & Responsive**: Quick search and response generation
- **📖 Source Citations**: Shows exactly which texts the answers come from
- **💡 Example Questions**: Pre-built questions to get you started

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Your Google API Key

1. Get a free Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_api_key_here
```

### 3. Add Your Hindu Scripture Texts

Create a `hindu_texts/` directory and add your scripture files:
```
hindu_texts/
├── bhagavad_gita.txt
├── upanishads.txt
├── vedas.txt
└── ... (any .txt files)
```

**Supported formats**: `.txt` files with UTF-8 encoding

### 4. Run the Application

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

## 📁 Project Structure

```
SanatanaGPT/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env                           # Your Google API key (create this)
├── README.md                      # This file
├── .gitignore                     # Git ignore rules
│
├── hindu_texts/                   # Your scripture text files
│   ├── sample_bhagavad_gita.txt
│   ├── sample_upanishads.txt
│   └── ... (add your .txt files here)
│
├── config/                        # Configuration files
│   ├── env_example.txt           # Environment template
│   ├── secrets_template.toml     # Streamlit secrets template
│   └── .streamlit/               # Streamlit configuration
│       └── config.toml
│
├── scripts/                       # Utility scripts
│   ├── setup.py                 # Automated setup script
│   └── text_processor.py        # Text processing utilities
│
└── docs/                         # Documentation
    ├── INSTALLATION.md           # Detailed installation guide
    └── API_GUIDE.md             # Google Gemini API guide
```

## 📚 Documentation

- **[📖 Installation Guide](docs/INSTALLATION.md)** - Complete setup instructions
- **[🤖 API Guide](docs/API_GUIDE.md)** - Google Gemini integration details
- **[🔧 Text Processing](scripts/text_processor.py)** - Utilities for scripture files

## 💡 Usage Examples

### Example Questions You Can Ask:

- "What is dharma according to the Bhagavad Gita?"
- "What does Om represent in Hindu philosophy?"
- "What is karma and how does it work?"
- "What are the four goals of human life?"
- "What is the nature of the soul (Atman)?"
- "What does Krishna teach about duty?"
- "What is meditation according to the Vedas?"
- "What is the path to liberation (moksha)?"

### How It Works:

1. **Text Loading**: The app loads all `.txt` files from your `hindu_texts/` directory
2. **Smart Search**: When you ask a question, it searches for relevant passages
3. **AI Analysis**: Google Gemini AI analyzes the passages and generates a comprehensive answer
4. **Source Display**: Shows you exactly which texts and passages the answer comes from

## 🛠️ Technical Details

- **Frontend**: Streamlit (Python web framework)
- **AI Model**: Google Gemini 1.5 Flash
- **Text Processing**: Custom relevance scoring algorithm
- **Search**: Keyword-based passage retrieval
- **Caching**: Streamlit caching for fast performance

## ☁️ Streamlit Cloud Deployment

Deploy your app to Streamlit Cloud for free:

1. **Push to GitHub** (this repository)
2. **Go to [share.streamlit.io](https://share.streamlit.io)**
3. **Connect your GitHub account**
4. **Deploy the app** using `app.py`
5. **Add your Google API key** in App Settings → Secrets

**Detailed deployment guide**: [docs/INSTALLATION.md](docs/INSTALLATION.md)

## 🔧 Utility Scripts

### Automated Setup
```bash
python scripts/setup.py
```
Automatically installs dependencies, creates config files, and sets up the project.

### Text Processing
```bash
python scripts/text_processor.py
```
Analyzes your Hindu scripture files and generates processing reports.

## 📋 Requirements

- Python 3.8+
- Google API key (free tier available)
- Internet connection for AI API calls
- Hindu scripture text files (.txt format)

## 🎯 Tips for Best Results

1. **Quality Text Files**: Use well-formatted, clean text files
2. **Specific Questions**: Ask specific questions for better results
3. **Use Keywords**: Include relevant Sanskrit terms or concepts
4. **Multiple Files**: Add multiple scripture files for comprehensive answers

## 🔍 Troubleshooting

### Common Issues:

1. **"GOOGLE_API_KEY not found"**
   - Make sure you have a `.env` file with your API key
   - Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. **"No .txt files found"**
   - Add Hindu scripture text files to the `hindu_texts/` directory
   - Make sure files have `.txt` extension

3. **Import Errors**
   - Run `python scripts/setup.py` for automated setup
   - Or manually: `pip install -r requirements.txt`

**Full troubleshooting guide**: [docs/INSTALLATION.md](docs/INSTALLATION.md)

## 🙏 Acknowledgments

- **Google Gemini AI**: For intelligent text analysis and response generation
- **Streamlit**: For the beautiful and easy-to-use web interface
- **Hindu Scripture Authors**: For the timeless wisdom contained in these texts

## 📜 License

This project is open source and available under the MIT License.

---

*🕉️ May this tool help spread the wisdom and knowledge of Hindu scriptures to seekers around the world. 🕉️* 