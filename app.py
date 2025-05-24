import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import time
import re
import datetime
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pickle
import hashlib
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError

# PDF support
try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Load environment variables
load_dotenv()

# User data file
USER_DATA_FILE = "user_data.pkl"
USERS_CONFIG_FILE = "users_config.yaml"

# Initialize persistent storage
def init_persistent_storage():
    """Initialize persistent storage using session state and secrets."""
    if 'persistent_users' not in st.session_state:
        # Try to load from secrets first (for pre-configured users)
        try:
            if hasattr(st, 'secrets') and 'users' in st.secrets:
                st.session_state.persistent_users = dict(st.secrets['users'])
            else:
                # Start with empty users - no default admin
                st.session_state.persistent_users = {}
        except Exception:
            # Fallback to empty users
            st.session_state.persistent_users = {}
    
    if 'persistent_user_data' not in st.session_state:
        st.session_state.persistent_user_data = {}

def load_user_data():
    """Load user conversation data from session state."""
    init_persistent_storage()
    return st.session_state.persistent_user_data

def save_user_data(user_data):
    """Save user conversation data to session state."""
    init_persistent_storage()
    st.session_state.persistent_user_data = user_data

def create_users_config():
    """Create initial users configuration."""
    init_persistent_storage()
    
    # Create config from persistent storage
    config = {
        'credentials': {
            'usernames': {}
        },
        'cookie': {
            'expiry_days': 30,
            'key': 'sanatana_gpt_auth',
            'name': 'sanatana_gpt_cookie'
        },
        'preauthorized': {
            'emails': []
        }
    }
    
    # Copy users from persistent storage
    for username, user_info in st.session_state.persistent_users.items():
        config['credentials']['usernames'][username] = user_info.copy()
    
    # Hash passwords if they aren't already hashed
    for username, user_info in config['credentials']['usernames'].items():
        if not user_info['password'].startswith('$2b$'):
            # Password needs to be hashed
            temp_config = {'credentials': {'usernames': {username: user_info}}}
            stauth.Hasher.hash_passwords(temp_config['credentials'])
            config['credentials']['usernames'][username]['password'] = temp_config['credentials']['usernames'][username]['password']
            # Update persistent storage with hashed password
            st.session_state.persistent_users[username]['password'] = config['credentials']['usernames'][username]['password']
    
    return config

def load_users_config():
    """Load users configuration from session state."""
    return create_users_config()

def save_users_config(config):
    """Save users configuration to session state."""
    init_persistent_storage()
    # Update persistent storage
    st.session_state.persistent_users = config['credentials']['usernames'].copy()

def register_new_user(username, name, email, password):
    """Register a new user in persistent storage."""
    init_persistent_storage()
    
    # Check if username already exists
    if username in st.session_state.persistent_users:
        return False, "Username already exists"
    
    # Add new user
    st.session_state.persistent_users[username] = {
        'email': email,
        'name': name,
        'password': password
    }
    
    # Hash the password
    temp_config = {
        'credentials': {
            'usernames': {username: st.session_state.persistent_users[username]}
        }
    }
    stauth.Hasher.hash_passwords(temp_config['credentials'])
    st.session_state.persistent_users[username]['password'] = temp_config['credentials']['usernames'][username]['password']
    
    return True, "User registered successfully!"

def generate_otp():
    """Generate a 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp, name):
    """Send OTP via email."""
    try:
        # Email configuration - you'll need to set these in your .env file or Streamlit secrets
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        
        # Check if email credentials are configured
        if not sender_email or not sender_password:
            return False, "Email service not configured. Please contact administrator."
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = "🕉️ SanatanaGPT - Email Verification Code"
        
        # Email body
        body = f"""
        🙏 Namaste {name}!
        
        Welcome to SanatanaGPT - Your Personal Guide to Hindu Wisdom!
        
        Your email verification code is: {otp}
        
        This code will expire in 10 minutes for security purposes.
        
        If you didn't request this verification, please ignore this email.
        
        🕉️ May your journey through Hindu scriptures bring you wisdom and peace.
        
        With blessings,
        The SanatanaGPT Team
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return True, "OTP sent successfully!"
        
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

def validate_email_format(email):
    """Validate email format."""
    try:
        validate_email(email)
        return True, "Valid email"
    except EmailNotValidError:
        return False, "Invalid email format"

def store_pending_user(username, name, email, password, otp):
    """Store user data temporarily until OTP verification."""
    if 'pending_users' not in st.session_state:
        st.session_state.pending_users = {}
    
    st.session_state.pending_users[email] = {
        'username': username,
        'name': name,
        'email': email,
        'password': password,
        'otp': otp,
        'timestamp': time.time()
    }

def verify_otp_and_register(email, entered_otp):
    """Verify OTP and register user if valid."""
    if 'pending_users' not in st.session_state or email not in st.session_state.pending_users:
        return False, "No pending registration found for this email"
    
    pending_user = st.session_state.pending_users[email]
    
    # Check if OTP has expired (10 minutes)
    if time.time() - pending_user['timestamp'] > 600:
        del st.session_state.pending_users[email]
        return False, "OTP has expired. Please register again."
    
    # Verify OTP
    if entered_otp != pending_user['otp']:
        return False, "Invalid OTP. Please try again."
    
    # Register the user
    success, message = register_new_user(
        pending_user['username'],
        pending_user['name'],
        pending_user['email'],
        pending_user['password']
    )
    
    if success:
        # Clean up pending user data
        del st.session_state.pending_users[email]
        return True, "Account created successfully! You can now login."
    else:
        return False, f"Registration failed: {message}"

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
    
    # Check Streamlit secrets (for cloud deployment) - handle gracefully if no secrets file
    try:
        if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
            api_key = st.secrets['GOOGLE_API_KEY']
    except Exception:
        # No secrets file found, that's okay for local development
        pass
    
    # Fallback to environment variable (for local development)
    if not api_key and os.getenv("GOOGLE_API_KEY"):
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
    """Load all text and PDF files from hindu_texts directory."""
    texts = {}
    texts_dir = Path("hindu_texts")
    
    if not texts_dir.exists():
        st.error("❌ hindu_texts directory not found!")
        st.info("Please create a 'hindu_texts' directory and add your scripture files (.txt or .pdf)")
        return {}
    
    # Load .txt files
    txt_files = list(texts_dir.glob("*.txt"))
    
    # Load .pdf files if PDF support is available
    pdf_files = []
    if PDF_SUPPORT:
        pdf_files = list(texts_dir.glob("*.pdf"))
    
    all_files = txt_files + pdf_files
    
    if not all_files:
        if PDF_SUPPORT:
            st.warning("⚠️ No .txt or .pdf files found in hindu_texts directory")
            st.info("Please add some Hindu scripture files (.txt or .pdf) to the hindu_texts folder")
        else:
            st.warning("⚠️ No .txt files found in hindu_texts directory")
            st.info("Please add some Hindu scripture text files (.txt) to the hindu_texts folder")
        return {}
    
    # Process text files
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():  # Only add non-empty files
                    texts[file_path.name] = content
        except Exception as e:
            st.warning(f"⚠️ Could not read {file_path.name}: {str(e)}")
    
    # Process PDF files
    for file_path in pdf_files:
        try:
            reader = PdfReader(file_path)
            content = ""
            
            # Extract text from all pages
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        content += f"\n\n--- Page {page_num + 1} ---\n\n"
                        content += page_text
                except Exception as e:
                    st.warning(f"⚠️ Could not read page {page_num + 1} from {file_path.name}: {str(e)}")
                    continue
            
            if content.strip():  # Only add non-empty files
                texts[file_path.name] = content.strip()
            else:
                st.warning(f"⚠️ No readable text found in {file_path.name}")
                
        except Exception as e:
            st.warning(f"⚠️ Could not read PDF {file_path.name}: {str(e)}")
    
    return texts

def search_relevant_passages(texts, query, max_passages=3, balance_sources=True):
    """Search for relevant passages in the texts with balanced representation."""
    results = []
    query_words = [word.lower().strip() for word in re.split(r'[^\w]+', query) if len(word.strip()) > 2]
    
    # First, collect results from each text separately
    text_results = {}
    
    for filename, content in texts.items():
        text_results[filename] = []
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
                text_results[filename].append({
                    'filename': filename,
                    'text': paragraph,
                    'score': score,
                    'paragraph_id': i
                })
        
        # Sort results for this text by score
        text_results[filename].sort(key=lambda x: x['score'], reverse=True)
    
    # Now ensure balanced representation from all texts
    # Take the best passages from each text, then fill remaining slots with highest scores overall
    passages_per_text = max(1, max_passages // len(texts))  # At least 1 passage per text if possible
    
    if balance_sources:
        # First pass: get top passages from each text
        for filename, file_results in text_results.items():
            if file_results:  # Only if this text has relevant passages
                # Take top passages from this text
                for passage in file_results[:passages_per_text]:
                    results.append(passage)
        
        # Second pass: if we still have slots, fill with remaining highest-scoring passages
        remaining_slots = max_passages - len(results)
        if remaining_slots > 0:
            # Collect all remaining passages
            all_remaining = []
            for filename, file_results in text_results.items():
                # Add passages beyond what we already took
                all_remaining.extend(file_results[passages_per_text:])
            
            # Sort by score and take the best remaining ones
            all_remaining.sort(key=lambda x: x['score'], reverse=True)
            results.extend(all_remaining[:remaining_slots])
    else:
        # Just take the highest scoring passages regardless of source
        all_passages = []
        for filename, file_results in text_results.items():
            all_passages.extend(file_results)
        
        # Sort by score and take the best ones
        all_passages.sort(key=lambda x: x['score'], reverse=True)
        results = all_passages[:max_passages]
    
    # Final sort by relevance score and return top results
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:max_passages]

def generate_answer(model, query, passages, conversation_context=None):
    """Generate answer using Gemini with relevant passages and conversation context."""
    if not passages:
        return "I couldn't find relevant passages in the Hindu scriptures for your question. Please try rephrasing or asking about different topics."
    
    # Prepare context from passages
    context = "\n\n".join([
        f"From {passage['filename']}:\n{passage['text']}"
        for passage in passages
    ])
    
    # Prepare conversation context if available
    conversation_history = ""
    if conversation_context and len(conversation_context) > 0:
        conversation_history = "\n\nPREVIOUS CONVERSATION:\n"
        for i, exchange in enumerate(conversation_context[-3:]):  # Last 3 exchanges for context
            conversation_history += f"Q{i+1}: {exchange['question']}\nA{i+1}: {exchange['answer'][:200]}...\n\n"
    
    prompt = f"""You are a wise and friendly guide who loves discussing Hindu philosophy and spirituality. You're having a casual, warm conversation with someone who's curious about these topics. Based on the following excerpts from Hindu texts and our previous conversation, please provide a thoughtful, conversational response.

CONTEXT FROM HINDU SCRIPTURES:
{context}{conversation_history}

WHAT THEY'RE SHARING/ASKING: {query}

Please respond in a warm, conversational way as if you're talking to a friend. If this relates to our previous conversation, acknowledge that naturally. Share insights from the scriptures in an accessible, relatable way. If you don't have enough context to fully address their thoughts, mention what you can share and suggest we could explore more together.

YOUR RESPONSE:"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating answer: {str(e)}"

def generate_conversation_name(first_question):
    """Generate a short, meaningful name for the conversation based on the first question."""
    # Remove common prefixes
    title = first_question
    
    prefixes_to_remove = [
        "I've been thinking about",
        "Tell me about",
        "Can you explain",
        "What's this concept of",
        "I'm curious about",
        "I want to understand",
        "How do I",
        "What does",
        "I'm struggling with understanding",
        "I'm interested in",
        "How can I",
        "What is",
        "Help me understand",
        "I want to know about"
    ]
    
    for prefix in prefixes_to_remove:
        if title.lower().startswith(prefix.lower()):
            title = title[len(prefix):].strip()
            break
    
    # Remove trailing punctuation
    title = title.rstrip('?!.').strip()
    
    # Extract key concepts and create a meaningful name
    key_words = []
    important_concepts = [
        'karma', 'dharma', 'atman', 'brahman', 'moksha', 'meditation', 'yoga',
        'soul', 'god', 'krishna', 'arjuna', 'gita', 'upanishads', 'vedas',
        'liberation', 'enlightenment', 'consciousness', 'self', 'reality',
        'truth', 'wisdom', 'spiritual', 'divine', 'sacred', 'holy'
    ]
    
    words = title.lower().split()
    for word in words:
        clean_word = word.strip('.,!?()[]{}":;')
        if clean_word in important_concepts:
            key_words.append(clean_word.title())
        elif len(clean_word) > 4 and clean_word not in ['about', 'really', 'actually', 'means', 'works']:
            key_words.append(clean_word.title())
    
    if key_words:
        if len(key_words) == 1:
            return f"{key_words[0]} Discussion"
        elif len(key_words) == 2:
            return f"{key_words[0]} & {key_words[1]}"
        else:
            return f"{key_words[0]} & {key_words[1]} Chat"
    
    # Fallback: use first few words
    words = title.split()[:3]
    if words:
        return ' '.join(words).title()
    
    return "Philosophy Chat"

def get_current_conversation():
    """Get the current conversation data."""
    if st.session_state.current_conversation_id is None:
        return {'chat_history': [], 'conversation_context': []}
    
    return st.session_state.conversations.get(st.session_state.current_conversation_id, 
                                            {'chat_history': [], 'conversation_context': []})

def create_new_conversation():
    """Create a new conversation."""
    st.session_state.conversation_counter += 1
    new_id = f"conv_{st.session_state.conversation_counter}"
    st.session_state.conversations[new_id] = {
        'chat_history': [],
        'conversation_context': [],
        'created_at': time.time()
    }
    st.session_state.current_conversation_id = new_id
    return new_id

def update_current_conversation(chat_history, conversation_context):
    """Update the current conversation data."""
    if st.session_state.current_conversation_id is None:
        create_new_conversation()
    
    st.session_state.conversations[st.session_state.current_conversation_id]['chat_history'] = chat_history
    st.session_state.conversations[st.session_state.current_conversation_id]['conversation_context'] = conversation_context

def main():
    """Main Streamlit application with user authentication."""
    
    # Create users config if it doesn't exist
    config = create_users_config()
    if not config:
        st.error("Failed to load authentication configuration")
        st.stop()
    
    # Create authenticator
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    # Login
    authenticator.login(location='main')
    
    # Get authentication status from session state
    name = st.session_state.get('name')
    authentication_status = st.session_state.get('authentication_status')
    username = st.session_state.get('username')
    
    # Clean up user-specific session state if not authenticated
    if authentication_status != True:
        user_keys_to_clear = [
            'conversations', 'current_conversation_id', 'conversation_counter', 
            'user_question', 'pending_example', 'username'
        ]
        for key in user_keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    if authentication_status == False:
        st.error('Username/password is incorrect')
        
        # Registration section with OTP verification
        st.markdown("---")
        st.subheader("🆕 Create New Account")
        
        # Check if we're in OTP verification mode
        if 'otp_verification_email' in st.session_state:
            # OTP Verification Form
            st.info(f"📧 We've sent a verification code to **{st.session_state.otp_verification_email}**")
            st.markdown("Please check your email and enter the 6-digit code below:")
            
            with st.form("otp_verification_form"):
                entered_otp = st.text_input("Enter 6-digit verification code", max_chars=6, placeholder="123456")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ Verify & Create Account", use_container_width=True, type="primary"):
                        if not entered_otp:
                            st.error("Please enter the verification code")
                        elif len(entered_otp) != 6 or not entered_otp.isdigit():
                            st.error("Please enter a valid 6-digit code")
                        else:
                            success, message = verify_otp_and_register(st.session_state.otp_verification_email, entered_otp)
                            if success:
                                st.success(message)
                                # Clear OTP verification state
                                del st.session_state.otp_verification_email
                                st.info("You can now login with your new credentials")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(message)
                
                with col2:
                    if st.form_submit_button("🔄 Resend Code", use_container_width=True):
                        if st.session_state.otp_verification_email in st.session_state.get('pending_users', {}):
                            pending_user = st.session_state.pending_users[st.session_state.otp_verification_email]
                            new_otp = generate_otp()
                            
                            # Update OTP and timestamp
                            pending_user['otp'] = new_otp
                            pending_user['timestamp'] = time.time()
                            
                            # Send new OTP
                            success, message = send_otp_email(pending_user['email'], new_otp, pending_user['name'])
                            if success:
                                st.success("New verification code sent!")
                            else:
                                st.error(message)
                        else:
                            st.error("Registration session expired. Please register again.")
                            del st.session_state.otp_verification_email
                            st.rerun()
            
            # Option to go back to registration
            if st.button("⬅️ Back to Registration"):
                if st.session_state.otp_verification_email in st.session_state.get('pending_users', {}):
                    del st.session_state.pending_users[st.session_state.otp_verification_email]
                del st.session_state.otp_verification_email
                st.rerun()
        
        else:
            # Registration Form
            with st.form("registration_form"):
                new_username = st.text_input("Username", placeholder="Choose a unique username")
                new_name = st.text_input("Full Name", placeholder="Your full name")
                new_email = st.text_input("Email", placeholder="your.email@example.com")
                new_password = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
                
                if st.form_submit_button("📧 Send Verification Code", use_container_width=True, type="primary"):
                    if not all([new_username, new_name, new_email, new_password]):
                        st.error("Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        # Validate email format
                        email_valid, email_message = validate_email_format(new_email)
                        if not email_valid:
                            st.error(email_message)
                        else:
                            # Check if username or email already exists
                            config = load_users_config()
                            if config and new_username in config['credentials']['usernames']:
                                st.error("Username already exists")
                            elif config:
                                # Check if email already exists
                                email_exists = False
                                for user_data in config['credentials']['usernames'].values():
                                    if user_data.get('email', '').lower() == new_email.lower():
                                        email_exists = True
                                        break
                                
                                if email_exists:
                                    st.error("Email already registered")
                                else:
                                    # Generate and send OTP
                                    otp = generate_otp()
                                    success, message = send_otp_email(new_email, otp, new_name)
                                    
                                    if success:
                                        # Store pending user data
                                        store_pending_user(new_username, new_name, new_email, new_password, otp)
                                        st.session_state.otp_verification_email = new_email
                                        st.success("Verification code sent to your email!")
                                        st.rerun()
                                    else:
                                        st.error(message)
                            else:
                                st.error("Error loading configuration")
        
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        
        # Show registration option
        st.markdown("---")
        st.info("Don't have an account? Create one below with email verification!")
        
        # Registration section with OTP verification
        st.subheader("🆕 Create New Account")
        
        # Check if we're in OTP verification mode
        if 'otp_verification_email' in st.session_state:
            # OTP Verification Form
            st.info(f"📧 We've sent a verification code to **{st.session_state.otp_verification_email}**")
            st.markdown("Please check your email and enter the 6-digit code below:")
            
            with st.form("otp_verification_form_none"):
                entered_otp = st.text_input("Enter 6-digit verification code", max_chars=6, placeholder="123456")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ Verify & Create Account", use_container_width=True, type="primary"):
                        if not entered_otp:
                            st.error("Please enter the verification code")
                        elif len(entered_otp) != 6 or not entered_otp.isdigit():
                            st.error("Please enter a valid 6-digit code")
                        else:
                            success, message = verify_otp_and_register(st.session_state.otp_verification_email, entered_otp)
                            if success:
                                st.success(message)
                                # Clear OTP verification state
                                del st.session_state.otp_verification_email
                                st.info("You can now login with your new credentials")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(message)
                
                with col2:
                    if st.form_submit_button("🔄 Resend Code", use_container_width=True):
                        if st.session_state.otp_verification_email in st.session_state.get('pending_users', {}):
                            pending_user = st.session_state.pending_users[st.session_state.otp_verification_email]
                            new_otp = generate_otp()
                            
                            # Update OTP and timestamp
                            pending_user['otp'] = new_otp
                            pending_user['timestamp'] = time.time()
                            
                            # Send new OTP
                            success, message = send_otp_email(pending_user['email'], new_otp, pending_user['name'])
                            if success:
                                st.success("New verification code sent!")
                            else:
                                st.error(message)
                        else:
                            st.error("Registration session expired. Please register again.")
                            del st.session_state.otp_verification_email
                            st.rerun()
            
            # Option to go back to registration
            if st.button("⬅️ Back to Registration", key="back_to_reg_none"):
                if st.session_state.otp_verification_email in st.session_state.get('pending_users', {}):
                    del st.session_state.pending_users[st.session_state.otp_verification_email]
                del st.session_state.otp_verification_email
                st.rerun()
        
        else:
            # Registration Form
            with st.form("registration_form_none"):
                new_username = st.text_input("Username", placeholder="Choose a unique username")
                new_name = st.text_input("Full Name", placeholder="Your full name")
                new_email = st.text_input("Email", placeholder="your.email@example.com")
                new_password = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
                
                if st.form_submit_button("📧 Send Verification Code", use_container_width=True, type="primary"):
                    if not all([new_username, new_name, new_email, new_password]):
                        st.error("Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        # Validate email format
                        email_valid, email_message = validate_email_format(new_email)
                        if not email_valid:
                            st.error(email_message)
                        else:
                            # Check if username or email already exists
                            config = load_users_config()
                            if config and new_username in config['credentials']['usernames']:
                                st.error("Username already exists")
                            elif config:
                                # Check if email already exists
                                email_exists = False
                                for user_data in config['credentials']['usernames'].values():
                                    if user_data.get('email', '').lower() == new_email.lower():
                                        email_exists = True
                                        break
                                
                                if email_exists:
                                    st.error("Email already registered")
                                else:
                                    # Generate and send OTP
                                    otp = generate_otp()
                                    success, message = send_otp_email(new_email, otp, new_name)
                                    
                                    if success:
                                        # Store pending user data
                                        store_pending_user(new_username, new_name, new_email, new_password, otp)
                                        st.session_state.otp_verification_email = new_email
                                        st.success("Verification code sent to your email!")
                                        st.rerun()
                                    else:
                                        st.error(message)
                            else:
                                st.error("Error loading configuration")
        
    elif authentication_status:
        # User is authenticated - show the main app
        
        # Load user-specific data
        user_data = load_user_data()
        if username not in user_data:
            user_data[username] = {
                'conversations': {},
                'current_conversation_id': None,
                'conversation_counter': 0
            }
        
        # Initialize session state with user-specific data
        st.session_state.setdefault('user_question', "")
        st.session_state.conversations = user_data[username]['conversations']
        st.session_state.current_conversation_id = user_data[username]['current_conversation_id']
        st.session_state.conversation_counter = user_data[username]['conversation_counter']
        st.session_state.setdefault('pending_example', None)
        st.session_state.username = username
        
        # Save user data function
        def save_current_user_data():
            user_data[username] = {
                'conversations': st.session_state.conversations,
                'current_conversation_id': st.session_state.current_conversation_id,
                'conversation_counter': st.session_state.conversation_counter
            }
            save_user_data(user_data)
        
        # Header with logout
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("🕉️ Hindu Scriptures Q&A")
            st.markdown("*Explore the wisdom of ancient Hindu texts with AI-powered search*")
        with col2:
            st.write(f"Welcome, **{name}**!")
            if st.button("🚪 Logout"):
                # Save user data before logout
                save_current_user_data()
                
                # Perform logout first
                try:
                    authenticator.logout(location='main')
                except Exception as e:
                    st.error(f"Logout error: {e}")
                
                # Clear ALL session state to ensure clean logout
                keys_to_clear = [
                    'conversations', 'current_conversation_id', 'conversation_counter', 
                    'user_question', 'pending_example', 'username', 'pending_users', 
                    'otp_verification_email', 'name', 'authentication_status',
                    'persistent_users', 'persistent_user_data'
                ]
                
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                
                # Clear any remaining authentication-related keys
                auth_keys = [k for k in st.session_state.keys() if 'auth' in k.lower() or 'login' in k.lower()]
                for key in auth_keys:
                    del st.session_state[key]
                
                # Show success message and force immediate refresh
                st.success("✅ Logged out successfully!")
                st.rerun()
        
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
            
            # Show file type breakdown
            txt_files = [f for f in texts.keys() if f.endswith('.txt')]
            pdf_files = [f for f in texts.keys() if f.endswith('.pdf')]
            
            if txt_files:
                st.markdown(f"**📄 Text Files ({len(txt_files)}):**")
                for filename in txt_files:
                    st.write(f"• {filename}")
            
            if pdf_files:
                st.markdown(f"**📕 PDF Files ({len(pdf_files)}):**")
                for filename in pdf_files:
                    st.write(f"• {filename}")
            
            # Show supported formats info
            if PDF_SUPPORT:
                st.info("💡 **Supported formats:** .txt and .pdf files")
            else:
                st.info("💡 **Supported formats:** .txt files only")
                st.caption("Install pypdf to enable PDF support")
            
            st.caption(f"📊 Total: {len(texts)} scripture files loaded")
            
            # User info - protect against KeyError during logout
            st.markdown("---")
            st.markdown(f"**👤 Logged in as:** {name}")
            try:
                user_email = config['credentials']['usernames'][username]['email']
                st.markdown(f"**📧 Email:** {user_email}")
            except (KeyError, TypeError):
                # Handle case where user data is being cleared during logout
                st.markdown("**📧 Email:** Logging out...")
            
            # Conversation management
            st.header("💬 Your Conversations")
            
            # New conversation button with better styling
            if st.button("✨ Start New Chat", use_container_width=True, type="primary"):
                create_new_conversation()
                save_current_user_data()
                st.rerun()
            
            # Show existing conversations
            st.markdown("### 📋 Chat History")
            
            if st.session_state.conversations:
                # Sort conversations by creation time (newest first)
                sorted_conversations = sorted(
                    st.session_state.conversations.items(),
                    key=lambda x: x[1]['created_at'],
                    reverse=True
                )
                
                for conv_id, conv_data in sorted_conversations:
                    # Highlight current conversation
                    is_current = conv_id == st.session_state.current_conversation_id
                    
                    # Create conversation card with expandable design
                    with st.container():
                        # Get conversation title using AI-generated name
                        chat_history = conv_data['chat_history']
                        if chat_history and len(chat_history) > 0:
                            # Generate AI-based conversation name
                            first_question = chat_history[0]['question']
                            title = generate_conversation_name(first_question)
                        else:
                            title = "New Chat"
                        
                        # Display conversation as expandable item
                        if is_current:
                            # Current conversation - highlighted
                            current_indicator = "🔥"
                            expanded_default = True
                        else:
                            current_indicator = "💭"
                            expanded_default = False
                        
                        # Create expandable conversation
                        with st.expander(f"{current_indicator} {title}", expanded=expanded_default):
                            if chat_history:
                                # Show conversation statistics
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Messages", len(chat_history))
                                with col2:
                                    # Calculate total sources used
                                    total_sources = 0
                                    unique_sources = set()
                                    for chat in chat_history:
                                        if 'passages' in chat and chat['passages']:
                                            total_sources += len(chat['passages'])
                                            for passage in chat['passages']:
                                                unique_sources.add(passage['filename'])
                                    st.metric("Sources Used", len(unique_sources))
                                
                                # Show timestamp info
                                timestamp = datetime.datetime.fromtimestamp(conv_data['created_at'])
                                time_ago = datetime.datetime.now() - timestamp
                                
                                if time_ago.days > 0:
                                    time_str = f"{time_ago.days} days ago"
                                elif time_ago.seconds > 3600:
                                    time_str = f"{time_ago.seconds // 3600} hours ago"
                                elif time_ago.seconds > 60:
                                    time_str = f"{time_ago.seconds // 60} minutes ago"
                                else:
                                    time_str = "Just now"
                                
                                st.caption(f"⏰ Created: {timestamp.strftime('%B %d, %Y at %I:%M %p')} ({time_str})")
                                
                                # Show last message preview
                                last_msg = chat_history[-1]
                                st.markdown("**Last Question:**")
                                st.markdown(f"*{last_msg['question'][:100]}{'...' if len(last_msg['question']) > 100 else ''}*")
                                
                                # Show sources from last message if available
                                if 'passages' in last_msg and last_msg['passages']:
                                    sources = set()
                                    for passage in last_msg['passages']:
                                        filename = passage['filename'].replace('.txt', '').replace('_', ' ').title()
                                        sources.add(filename)
                                    st.markdown(f"**Recent Sources:** {', '.join(sources)}")
                                
                                st.markdown("---")
                                
                                # Action buttons
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    if not is_current:
                                        if st.button("🔄 Switch to this chat", key=f"switch_exp_{conv_id}", use_container_width=True):
                                            st.session_state.current_conversation_id = conv_id
                                            save_current_user_data()
                                            st.rerun()
                                    else:
                                        st.info("📍 Current conversation")
                                
                                with col2:
                                    if st.button("🗑️ Delete Chat", key=f"delete_exp_{conv_id}", use_container_width=True, type="secondary"):
                                        # Confirmation before deletion
                                        if st.button("⚠️ Confirm Delete", key=f"confirm_delete_{conv_id}", type="primary"):
                                            del st.session_state.conversations[conv_id]
                                            if st.session_state.current_conversation_id == conv_id:
                                                if st.session_state.conversations:
                                                    st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]
                                                else:
                                                    st.session_state.current_conversation_id = None
                                            save_current_user_data()
                                            st.rerun()
                                        else:
                                            st.warning("Click 'Confirm Delete' to permanently delete this conversation.")
                            else:
                                # Empty conversation
                                st.info("💭 This conversation is empty")
                                st.caption("Start chatting to see conversation details here.")
                                
                                # Delete button for empty conversations
                                if st.button("🗑️ Remove Empty Chat", key=f"delete_empty_exp_{conv_id}", use_container_width=True):
                                    del st.session_state.conversations[conv_id]
                                    if st.session_state.current_conversation_id == conv_id:
                                        if st.session_state.conversations:
                                            st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]
                                        else:
                                            st.session_state.current_conversation_id = None
                                    save_current_user_data()
                                    st.rerun()
                
                # Show total count in a more appealing way
                total_convs = len(st.session_state.conversations)
                if total_convs == 1:
                    st.markdown(f"<div style='text-align: center; color: #666; font-size: 12px;'>💫 {total_convs} conversation</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: center; color: #666; font-size: 12px;'>💫 {total_convs} conversations</div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    text-align: center; 
                    padding: 20px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px;
                    margin: 10px 0;
                ">
                    <div style="color: white; font-size: 16px; margin-bottom: 8px;">🌟</div>
                    <div style="color: white; font-size: 14px;">Start your first conversation!</div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 12px; margin-top: 5px;">Ask about Hindu philosophy</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.header("⚙️ Settings")
            max_passages = st.slider(
                "Number of passages to analyze",
                min_value=1,
                max_value=10,
                value=3,
                step=1,
                help="More passages provide more context but slower responses. Recommended: 3-5 for balanced results."
            )
            
            # Advanced settings in an expander
            with st.expander("🔧 Advanced Settings"):
                st.info("💡 **Tip:** Just press Enter to send your message!")
                balance_sources = st.checkbox(
                    "Balance sources equally",
                    value=True,
                    help="Ensures representation from all available texts when possible"
                )
            
            st.header("💡 Example Topics")
            examples = [
                "I've been thinking about what dharma really means...",
                "Tell me about karma - how does it actually work?",
                "I'm curious about meditation and how to start",
                "What's this concept of Atman I keep hearing about?",
                "I'm struggling with understanding my purpose in life",
                "Can you explain what Brahman is in simple terms?",
                "I want to understand the soul better",
                "How can I live more spiritually?",
                "What does liberation actually mean?",
                "I'm interested in the Bhagavad Gita's teachings",
                "Tell me about the Upanishads",
                "How do I deal with difficult emotions spiritually?"
            ]
            
            for i, example in enumerate(examples):
                if st.button(f"💭 {example}", key=f"example_{i}"):
                    # Create new conversation if none exists
                    if st.session_state.current_conversation_id is None:
                        create_new_conversation()
                    
                    # Get current conversation data
                    current_conv = get_current_conversation()
                    chat_history = current_conv['chat_history']
                    
                    # Add the example to chat history and trigger processing
                    chat_history.append({
                        'question': example,
                        'answer': "Processing your question...",
                        'passages': [],
                        'timestamp': time.time()
                    })
                    
                    # Update the conversation
                    update_current_conversation(chat_history, current_conv['conversation_context'])
                    st.session_state.pending_example = example
                    save_current_user_data()
                    st.rerun()
            
            # Clear conversation button
            st.markdown("---")
            if st.button("🧹 New Conversation", use_container_width=True):
                create_new_conversation()
                save_current_user_data()
                st.rerun()

        # Main content area
        st.header("💬 Chat with Hindu Scriptures")
        
        # Get current conversation data
        current_conv = get_current_conversation()
        chat_history = current_conv['chat_history']
        conversation_context = current_conv['conversation_context']
        
        # Display conversation history as chat messages
        if chat_history:
            st.markdown("### 🗨️ Conversation")
            
            # Create a container for the chat messages
            chat_container = st.container()
            
            with chat_container:
                for i, chat in enumerate(chat_history):
                    # User message
                    with st.chat_message("user"):
                        st.write(chat['question'])
                    
                    # Assistant message
                    with st.chat_message("assistant"):
                        st.write(chat['answer'])
                        
                        # Show sources button if passages are available
                        if 'passages' in chat and chat['passages']:
                            # Create a unique key for this chat's source button
                            source_key = f"sources_{st.session_state.current_conversation_id}_{i}"
                            
                            # Count sources
                            source_counts = {}
                            for passage in chat['passages']:
                                filename = passage['filename']
                                source_counts[filename] = source_counts.get(filename, 0) + 1
                            
                            source_text = ", ".join([f"{filename.replace('.txt', '').replace('_', ' ').title()}" for filename in source_counts.keys()])
                            
                            # Source button
                            if st.button(f"📚 View Sources ({len(chat['passages'])} passages)", key=source_key, help=f"Sources: {source_text}"):
                                # Toggle source display
                                if f"show_{source_key}" not in st.session_state:
                                    st.session_state[f"show_{source_key}"] = False
                                st.session_state[f"show_{source_key}"] = not st.session_state[f"show_{source_key}"]
                                st.rerun()
                            
                            # Show detailed sources if toggled
                            if st.session_state.get(f"show_{source_key}", False):
                                st.markdown("**📖 Source Passages:**")
                                for j, passage in enumerate(chat['passages']):
                                    with st.expander(f"📜 {passage['filename'].replace('.txt', '').replace('_', ' ').title()} - Passage {j+1}", expanded=False):
                                        st.markdown(f"**Relevance Score:** {passage['score']:.2f}")
                                        st.markdown("**Text:**")
                                        st.markdown(f"*{passage['text']}*")
                        else:
                            # Show subtle caption for responses without sources
                            st.caption("💭 Response generated from general knowledge")
            
            st.markdown("---")
        else:
            # Welcome message for new users
            st.markdown("### 🙏 Welcome!")
            with st.chat_message("assistant"):
                st.write(f"""
                Hello {name}! I'm here to help you explore the wisdom of Hindu scriptures. I have access to the Bhagavad Gita and Upanishads, and I can discuss topics like:
                
                - **Dharma** and righteous living
                - **Karma** and the law of action
                - **Atman** and the nature of the soul
                - **Brahman** and ultimate reality
                - **Meditation** and spiritual practices
                - **Liberation (Moksha)** and the spiritual path
                
                Feel free to ask me anything or just start a conversation about what interests you! 😊
                """)
            st.markdown("---")

        # Process pending example if any
        if 'pending_example' in st.session_state and st.session_state.pending_example:
            prompt = st.session_state.pending_example
            st.session_state.pending_example = None  # Clear the pending example
            
            # Get current conversation data
            current_conv = get_current_conversation()
            chat_history = current_conv['chat_history']
            conversation_context = current_conv['conversation_context']
            
            # Process the example message
            with st.spinner("🤔 Reflecting on the scriptures..."):
                start_time = time.time()
                
                # Find relevant passages
                passages = search_relevant_passages(texts, prompt, max_passages, balance_sources)
                
                if passages:
                    # Generate answer
                    answer = generate_answer(model, prompt, passages, conversation_context)
                    
                    search_time = time.time() - start_time
                    
                    # Update the last message in chat history with the real answer
                    if chat_history:
                        chat_history[-1] = {
                            'question': prompt,
                            'answer': answer,
                            'passages': passages,
                            'timestamp': time.time()
                        }
                    
                    # Add to conversation context (for AI)
                    conversation_context.append({
                        'question': prompt,
                        'answer': answer
                    })
                    
                    # Keep only last 10 conversations to avoid token limits
                    if len(conversation_context) > 10:
                        conversation_context = conversation_context[-10:]
                        
                    # Update the conversation
                    update_current_conversation(chat_history, conversation_context)
                    save_current_user_data()
                else:
                    # Update with no results message
                    if chat_history:
                        chat_history[-1] = {
                            'question': prompt,
                            'answer': "I couldn't find relevant passages in the Hindu scriptures for your thoughts. Could you try rephrasing or exploring a different aspect of Hindu philosophy?",
                            'passages': [],
                            'timestamp': time.time()
                        }
                        # Update the conversation
                        update_current_conversation(chat_history, conversation_context)
                        save_current_user_data()
            
            st.rerun()
        
        # Chat input at the bottom (modern AI bot style)
        if prompt := st.chat_input("Share your thoughts about Hindu philosophy..."):
            # Create new conversation if none exists
            if st.session_state.current_conversation_id is None:
                create_new_conversation()
            
            # Get current conversation data
            current_conv = get_current_conversation()
            chat_history = current_conv['chat_history']
            conversation_context = current_conv['conversation_context']
            
            # Process the message immediately
            with st.spinner("🤔 Reflecting on the scriptures..."):
                start_time = time.time()
                
                # Find relevant passages
                passages = search_relevant_passages(texts, prompt, max_passages, balance_sources)
                
                if passages:
                    # Generate answer
                    answer = generate_answer(model, prompt, passages, conversation_context)
                    
                    search_time = time.time() - start_time
                    
                    # Add to conversation history
                    chat_history.append({
                        'question': prompt,
                        'answer': answer,
                        'passages': passages,
                        'timestamp': time.time()
                    })
                    
                    # Add to conversation context (for AI)
                    conversation_context.append({
                        'question': prompt,
                        'answer': answer
                    })
                    
                    # Keep only last 10 conversations to avoid token limits
                    if len(conversation_context) > 10:
                        conversation_context = conversation_context[-10:]
                    
                    # Update the conversation
                    update_current_conversation(chat_history, conversation_context)
                    save_current_user_data()
                    
                else:
                    # Add message with no results
                    chat_history.append({
                        'question': prompt,
                        'answer': "I couldn't find relevant passages in the Hindu scriptures for your thoughts. Could you try rephrasing or exploring a different aspect of Hindu philosophy?",
                        'passages': [],
                        'timestamp': time.time()
                    })
                    
                    # Update the conversation
                    update_current_conversation(chat_history, conversation_context)
                    save_current_user_data()
            
            # Rerun to update the chat display
            st.rerun()

        # Footer
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>🕉️ <strong>Your Personal Guide to Hindu Wisdom</strong> 🕉️</p>
            <p>Logged in as <strong>{name}</strong> • Powered by Google Gemini AI • Built with ❤️ for spiritual conversations</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 