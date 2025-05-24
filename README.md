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
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env               # Your Google API key (create this)
├── hindu_texts/       # Your scripture text files
└── README.md          # This file
```

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

## 📋 Requirements

- Python 3.8+
- Google API key (free tier available)
- Internet connection for AI API calls
- Hindu scripture text files (.txt format)

## 🔧 Configuration

### Adjustable Settings (in the app sidebar):

- **Number of passages**: Control how many text passages to analyze (1-5)
- More passages = more context but slower responses

### Environment Variables:

- `GOOGLE_API_KEY`: Your Google AI API key (required)

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

3. **"No relevant passages found"**
   - Try rephrasing your question
   - Use different keywords
   - Check if your text files contain relevant content

4. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Make sure you're using Python 3.8+

## 🙏 Acknowledgments

- **Google Gemini AI**: For intelligent text analysis and response generation
- **Streamlit**: For the beautiful and easy-to-use web interface
- **Hindu Scripture Authors**: For the timeless wisdom contained in these texts

## 📜 License

This project is open source and available under the MIT License.

---

*🕉️ May this tool help spread the wisdom and knowledge of Hindu scriptures to seekers around the world. 🕉️* 