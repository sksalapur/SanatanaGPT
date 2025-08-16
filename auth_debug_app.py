import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# Simple test app to debug authentication
from database import authenticate_user, init_database

st.title("🔍 Authentication Debug Test")

# Initialize database
try:
    init_database()
    st.success("✅ Database initialized successfully")
except Exception as e:
    st.error(f"❌ Database error: {e}")
    st.stop()

st.markdown("---")
st.subheader("Test Authentication")

# Simple login form
with st.form("debug_login"):
    username = st.text_input("Username", value="admin")
    password = st.text_input("Password", type="password", value="admin123")
    test_button = st.form_submit_button("Test Authentication")

if test_button:
    st.write(f"Testing credentials: {username} / {password}")
    
    try:
        success, user_info = authenticate_user(username, password)
        
        st.write(f"**Result:** {success}")
        
        if success:
            st.success("✅ Authentication SUCCESS!")
            st.json(user_info)
        else:
            st.error("❌ Authentication FAILED!")
            
    except Exception as e:
        st.error(f"❌ Error during authentication: {e}")
        import traceback
        st.code(traceback.format_exc())

# Show current session state
st.markdown("---")
st.subheader("Session State Debug")
st.json(dict(st.session_state))
