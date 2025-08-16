# database.py - SQLite database models and helper functions for SanatanaGPT

import sqlite3
import json
import bcrypt
import time
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import streamlit as st

# Database configuration
DATABASE_URL = "sqlite:///sanatanagpt.db"
Base = declarative_base()

# SQLAlchemy Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationship with conversations
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    conversation_id = Column(String(50), nullable=False)  # e.g., "conv_1", "conv_2"
    title = Column(String(200), nullable=True)  # AI-generated conversation title
    chat_history = Column(Text, nullable=False)  # JSON string of chat messages
    conversation_context = Column(Text, nullable=True)  # JSON string of conversation context
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship with user
    user = relationship("User", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, conversation_id='{self.conversation_id}')>"

# Database initialization
@st.cache_resource
def init_database():
    """Initialize the database and create tables if they don't exist."""
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine, SessionLocal
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        raise

# Database session management
def get_db_session():
    """Get a database session."""
    _, SessionLocal = init_database()
    session = SessionLocal()
    try:
        return session
    except Exception as e:
        session.close()
        raise

# User authentication functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def register_user(username: str, name: str, email: str, password: str) -> tuple[bool, str]:
    """Register a new user in the database."""
    session = get_db_session()
    try:
        # Check if username already exists
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "Username already exists"
        
        # Check if email already exists
        existing_email = session.query(User).filter(User.email == email.lower()).first()
        if existing_email:
            return False, "Email already registered"
        
        # Hash password and create user
        hashed_pw = hash_password(password)
        new_user = User(
            username=username,
            name=name,
            email=email.lower(),
            hashed_password=hashed_pw
        )
        
        session.add(new_user)
        session.commit()
        return True, "User registered successfully!"
        
    except Exception as e:
        session.rollback()
        return False, f"Registration failed: {str(e)}"
    finally:
        session.close()

def authenticate_user(username: str, password: str) -> tuple[bool, dict]:
    """Authenticate a user and return user info if successful."""
    session = get_db_session()
    try:
        # Find user by username
        user = session.query(User).filter(User.username == username).first()
        
        if not user:
            return False, {}
        
        # Verify password
        if verify_password(password, user.hashed_password):
            user_info = {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'created_at': user.created_at
            }
            return True, user_info
        else:
            return False, {}
            
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False, {}
    finally:
        session.close()

def get_user_by_username(username: str) -> dict:
    """Get user information by username."""
    session = get_db_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'created_at': user.created_at
            }
        return {}
    except Exception as e:
        st.error(f"Error getting user: {e}")
        return {}
    finally:
        session.close()

def get_user_by_email(email: str) -> dict:
    """Get user information by email."""
    session = get_db_session()
    try:
        user = session.query(User).filter(User.email == email.lower()).first()
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'created_at': user.created_at
            }
        return {}
    except Exception as e:
        st.error(f"Error getting user by email: {e}")
        return {}
    finally:
        session.close()

# Conversation management functions
def save_conversation(user_id: int, conversation_id: str, chat_history: list, 
                     conversation_context: list, title: str = None) -> bool:
    """Save or update a conversation in the database."""
    session = get_db_session()
    try:
        # Check if conversation already exists
        existing_conv = session.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.conversation_id == conversation_id
        ).first()
        
        if existing_conv:
            # Update existing conversation
            existing_conv.chat_history = json.dumps(chat_history, ensure_ascii=False)
            existing_conv.conversation_context = json.dumps(conversation_context, ensure_ascii=False)
            existing_conv.updated_at = func.now()
            if title:
                existing_conv.title = title
        else:
            # Create new conversation
            new_conv = Conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                title=title,
                chat_history=json.dumps(chat_history, ensure_ascii=False),
                conversation_context=json.dumps(conversation_context, ensure_ascii=False)
            )
            session.add(new_conv)
        
        session.commit()
        return True
        
    except Exception as e:
        session.rollback()
        st.error(f"Error saving conversation: {e}")
        return False
    finally:
        session.close()

def get_user_conversations(user_id: int) -> dict:
    """Get all conversations for a user."""
    session = get_db_session()
    try:
        conversations = session.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).all()
        
        result = {}
        for conv in conversations:
            try:
                chat_history = json.loads(conv.chat_history) if conv.chat_history else []
                conversation_context = json.loads(conv.conversation_context) if conv.conversation_context else []
            except json.JSONDecodeError:
                chat_history = []
                conversation_context = []
            
            result[conv.conversation_id] = {
                'chat_history': chat_history,
                'conversation_context': conversation_context,
                'created_at': conv.created_at.timestamp() if conv.created_at else time.time(),
                'updated_at': conv.updated_at.timestamp() if conv.updated_at else time.time(),
                'title': conv.title
            }
        
        return result
        
    except Exception as e:
        st.error(f"Error getting conversations: {e}")
        return {}
    finally:
        session.close()

def delete_conversation(user_id: int, conversation_id: str) -> bool:
    """Delete a specific conversation."""
    session = get_db_session()
    try:
        conv = session.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.conversation_id == conversation_id
        ).first()
        
        if conv:
            session.delete(conv)
            session.commit()
            return True
        return False
        
    except Exception as e:
        session.rollback()
        st.error(f"Error deleting conversation: {e}")
        return False
    finally:
        session.close()

def get_conversation_count(user_id: int) -> int:
    """Get the total number of conversations for a user."""
    session = get_db_session()
    try:
        count = session.query(Conversation).filter(Conversation.user_id == user_id).count()
        return count
    except Exception as e:
        st.error(f"Error getting conversation count: {e}")
        return 0
    finally:
        session.close()

def update_conversation_title(user_id: int, conversation_id: str, title: str) -> bool:
    """Update the title of a conversation."""
    session = get_db_session()
    try:
        conv = session.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.conversation_id == conversation_id
        ).first()
        
        if conv:
            conv.title = title
            conv.updated_at = func.now()
            session.commit()
            return True
        return False
        
    except Exception as e:
        session.rollback()
        st.error(f"Error updating conversation title: {e}")
        return False
    finally:
        session.close()

# Migration helpers (for transitioning from old system)
def register_user_with_existing_hash(username: str, name: str, email: str, hashed_password: str) -> tuple[bool, str]:
    """Register a user with an already-hashed password (for migration only)."""
    session = get_db_session()
    try:
        # Check if username already exists
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "Username already exists"
        
        # Check if email already exists
        existing_email = session.query(User).filter(User.email == email.lower()).first()
        if existing_email:
            return False, "Email already registered"
        
        # Create user with existing hash (don't hash again)
        new_user = User(
            username=username,
            name=name,
            email=email.lower(),
            hashed_password=hashed_password
        )
        
        session.add(new_user)
        session.commit()
        return True, "User migrated successfully!"
        
    except Exception as e:
        session.rollback()
        return False, f"Migration failed: {str(e)}"
    finally:
        session.close()

def migrate_old_data_if_needed():
    """Migrate data from old .pkl and .yaml files if they exist."""
    try:
        import pickle
        import yaml
        from pathlib import Path
        
        # Check if old files exist
        pkl_file = Path("user_data.pkl")
        yaml_file = Path("users_config.yaml")
        
        if not pkl_file.exists() and not yaml_file.exists():
            return  # No old data to migrate
        
        st.info("📦 Migrating data from old storage format...")
        
        # Migrate users from YAML
        if yaml_file.exists():
            try:
                with open(yaml_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                if config and 'credentials' in config and 'usernames' in config['credentials']:
                    for username, user_data in config['credentials']['usernames'].items():
                        # Check if user already exists in new database
                        if not get_user_by_username(username):
                            password = user_data.get('password', 'migration_placeholder')
                            # Check if password is already a bcrypt hash
                            if password.startswith('$2b$') or password.startswith('$2a$') or password.startswith('$2y$'):
                                # Password is already hashed, use migration function
                                register_user_with_existing_hash(
                                    username=username,
                                    name=user_data.get('name', username),
                                    email=user_data.get('email', f"{username}@migrated.local"),
                                    hashed_password=password
                                )
                            else:
                                # Password is plain text, use normal registration
                                register_user(
                                    username=username,
                                    name=user_data.get('name', username),
                                    email=user_data.get('email', f"{username}@migrated.local"),
                                    password=password
                                )
            except Exception as e:
                st.warning(f"Could not migrate users from YAML: {e}")
        
        # Migrate conversations from PKL
        if pkl_file.exists():
            try:
                with open(pkl_file, 'rb') as f:
                    user_data = pickle.load(f)
                
                for username, data in user_data.items():
                    user_info = get_user_by_username(username)
                    if user_info and 'conversations' in data:
                        for conv_id, conv_data in data['conversations'].items():
                            save_conversation(
                                user_id=user_info['id'],
                                conversation_id=conv_id,
                                chat_history=conv_data.get('chat_history', []),
                                conversation_context=conv_data.get('conversation_context', [])
                            )
            except Exception as e:
                st.warning(f"Could not migrate conversations from PKL: {e}")
        
        st.success("✅ Data migration completed!")
        
    except ImportError:
        pass  # Migration libraries not available
    except Exception as e:
        st.warning(f"Migration warning: {e}")

# Database health check
def check_database_health() -> bool:
    """Check if the database is working properly."""
    try:
        session = get_db_session()
        # Simple query to test database
        session.query(User).count()
        session.close()
        return True
    except Exception as e:
        st.error(f"Database health check failed: {e}")
        return False

# Initialize database on import
try:
    init_database()
    # Run migration if needed (only once)
    if 'migration_attempted' not in st.session_state:
        migrate_old_data_if_needed()
        st.session_state.migration_attempted = True
except Exception as e:
    st.error(f"Failed to initialize database: {e}")
