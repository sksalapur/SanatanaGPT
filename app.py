import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import time
import re

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🕉️ Hindu Scriptures Q&A",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def setup_gemini():
    """Setup Google Gemini API."""
    # Try to get API key from Streamlit secrets first (for cloud deployment)
    api_key = None
    
    # Check Streamlit secrets (for cloud deployment)
    if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
    # Fallback to environment variable (for local development)
    elif os.getenv("GOOGLE_API_KEY"):
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        st.error("❌ GOOGLE_API_KEY not found")
        st.info("""
        **For local development:** Add your Google API key to the .env file
        
        **For Streamlit Cloud:** Add your API key in App Settings > Secrets:
        ```
        GOOGLE_API_KEY = "your_api_key_here"
        ```
        
        Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        """)
        st.stop()
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        st.error(f"❌ Error setting up Gemini: {str(e)}")
        st.stop()

@st.cache_data
def load_hindu_texts():
    """Load all text files from hindu_texts directory."""
    texts = {}
    texts_dir = Path("hindu_texts")
    
    if not texts_dir.exists():
        st.error("❌ hindu_texts directory not found!")
        st.info("Please create a 'hindu_texts' directory and add your scripture files (.txt)")
        return {}
    
    # Load .txt files
    txt_files = list(texts_dir.glob("*.txt"))
    
    if not txt_files:
        st.warning("⚠️ No .txt files found in hindu_texts directory")
        st.info("Please add some Hindu scripture text files (.txt) to the hindu_texts folder")
        return {}
    
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():  # Only add non-empty files
                    texts[file_path.name] = content
        except Exception as e:
            st.warning(f"⚠️ Could not read {file_path.name}: {str(e)}")
    
    return texts

def search_relevant_passages(texts, query, max_passages=3):
    """Search for relevant passages in the texts."""
    results = []
    query_words = [word.lower().strip() for word in re.split(r'[^\w]+', query) if len(word.strip()) > 2]
    
    for filename, content in texts.items():
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 100]
        
        for i, paragraph in enumerate(paragraphs):
            paragraph_lower = paragraph.lower()
            
            # Calculate relevance score
            score = 0
            for word in query_words:
                if word in paragraph_lower:
                    score += paragraph_lower.count(word) * (len(word) / 10)  # Longer words get higher weight
            
            if score > 0:
                results.append({
                    'filename': filename,
                    'text': paragraph,
                    'score': score,
                    'paragraph_id': i
                })
    
    # Sort by relevance score and return top results
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:max_passages]

def generate_answer(model, query, passages):
    """Generate answer using Gemini with relevant passages."""
    if not passages:
        return "I couldn't find relevant passages in the Hindu scriptures for your question. Please try rephrasing or asking about different topics."
    
    # Prepare context from passages
    context = "\n\n".join([
        f"From {passage['filename']}:\n{passage['text']}"
        for passage in passages
    ])
    
    prompt = f"""You are a knowledgeable scholar of Hindu scriptures. Based on the following excerpts from Hindu texts, please provide a comprehensive and accurate answer to the question.

CONTEXT FROM HINDU SCRIPTURES:
{context}

QUESTION: {query}

Please provide a detailed answer based on the provided context. If the context doesn't fully answer the question, mention what information is available and suggest what additional sources might be helpful. Always cite which text the information comes from.

ANSWER:"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating answer: {str(e)}"

def main():
    """Main Streamlit application."""
    
    # Header
    st.title("🕉️ Hindu Scriptures Q&A")
    st.markdown("*Explore the wisdom of ancient Hindu texts with AI-powered search*")
    
    # Setup Gemini
    model = setup_gemini()
    st.success("✅ Google Gemini AI connected!")
    
    # Load texts
    with st.spinner("📚 Loading Hindu scriptures..."):
        texts = load_hindu_texts()
    
    if not texts:
        st.stop()
    
    st.success(f"✅ Loaded {len(texts)} scripture files")
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Available Texts")
        for filename in texts.keys():
            st.write(f"• {filename}")
        
        st.header("⚙️ Settings")
        max_passages = st.slider(
            "Number of passages to analyze",
            min_value=1,
            max_value=5,
            value=3,
            help="More passages provide more context but slower responses"
        )
        
        st.header("💡 Example Questions")
        examples = [
            "What is dharma according to the Bhagavad Gita?",
            "What does Om represent in Hindu philosophy?",
            "What is karma and how does it work?",
            "What are the four goals of human life?",
            "What is the nature of the soul (Atman)?",
            "What does Krishna teach about duty?",
            "What is meditation according to the Vedas?",
            "What is the path to liberation (moksha)?"
        ]
        
        for i, example in enumerate(examples):
            if st.button(f"📝 {example}", key=f"example_{i}"):
                st.session_state.user_question = example

    # Main content area
    st.header("🔍 Ask Your Question")
    
    # Initialize session state
    if 'user_question' not in st.session_state:
        st.session_state.user_question = ""
    
    # Question input
    question = st.text_area(
        "What would you like to know about Hindu scriptures?",
        value=st.session_state.user_question,
        height=100,
        placeholder="e.g., What does the Bhagavad Gita say about the nature of reality?",
        key="question_input"
    )
    
    # Search button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_button = st.button("🔍 Search Scriptures", type="primary", use_container_width=True)
    
    # Process question
    if search_button and question.strip():
        with st.spinner("🔍 Searching through Hindu scriptures..."):
            start_time = time.time()
            
            # Find relevant passages
            passages = search_relevant_passages(texts, question, max_passages)
            
            if passages:
                # Generate answer
                answer = generate_answer(model, question, passages)
                
                search_time = time.time() - start_time
                
                # Display results
                st.markdown("### 📖 Answer")
                st.markdown(f"*Response generated in {search_time:.1f} seconds*")
                st.write(answer)
                
                # Show sources
                st.markdown("### 📚 Source Passages")
                for i, passage in enumerate(passages, 1):
                    with st.expander(f"📜 Source {i}: {passage['filename']} (Relevance: {passage['score']:.1f})"):
                        st.write(passage['text'])
            else:
                st.warning("🔍 No relevant passages found. Try rephrasing your question or using different keywords.")
    
    elif search_button:
        st.warning("⚠️ Please enter a question to search.")
    
    # Clear button
    if st.button("🗑️ Clear Question"):
        st.session_state.user_question = ""
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🕉️ <strong>Hindu Scriptures Q&A</strong> 🕉️</p>
        <p>Powered by Google Gemini AI • Built with ❤️ for spiritual seekers</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 