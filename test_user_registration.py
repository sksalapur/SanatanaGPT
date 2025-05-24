import streamlit as st
import sys
import os

# Add the current directory to Python path so we can import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import functions from app.py
from app import init_persistent_storage, register_new_user, get_user_stats

def test_user_registration():
    """Test user registration functionality."""
    st.title("🧪 User Registration Test")
    
    # Initialize storage
    init_persistent_storage()
    
    st.header("Current State")
    
    # Show current users
    if 'persistent_users' in st.session_state:
        st.write("**Users in persistent_users:**")
        for username, user_info in st.session_state.persistent_users.items():
            st.write(f"• {username}: {user_info}")
    else:
        st.error("persistent_users not found in session state")
    
    # Show stats
    try:
        stats = get_user_stats()
        st.write("**Stats:**")
        st.write(f"• Total users: {stats['total_users']}")
        st.write(f"• Users list: {stats['users']}")
    except Exception as e:
        st.error(f"Error getting stats: {e}")
    
    st.header("Test Registration")
    
    # Test registration form
    with st.form("test_registration"):
        test_username = st.text_input("Test Username", value="testuser123")
        test_name = st.text_input("Test Name", value="Test User")
        test_email = st.text_input("Test Email", value="test@example.com")
        test_password = st.text_input("Test Password", value="testpass123")
        
        if st.form_submit_button("Register Test User"):
            try:
                success, message = register_new_user(test_username, test_name, test_email, test_password)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            except Exception as e:
                st.error(f"Registration error: {e}")
    
    st.header("Manual Check")
    
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    # Show raw session state
    with st.expander("Raw Session State"):
        st.write("**All session state keys:**")
        st.write(list(st.session_state.keys()))
        
        if 'persistent_users' in st.session_state:
            st.write("**persistent_users content:**")
            st.json(st.session_state.persistent_users)

if __name__ == "__main__":
    test_user_registration() 