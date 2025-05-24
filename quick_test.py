import streamlit as st

st.title("🔧 Quick User Test")

# Initialize session state manually
if 'persistent_users' not in st.session_state:
    st.session_state.persistent_users = {
        'sksalapur': {
            'email': 'sksalapur@gmail.com',
            'name': 'Administrator',
            'password': 'sksalapur'
        }
    }

if 'persistent_user_data' not in st.session_state:
    st.session_state.persistent_user_data = {}

st.header("Current Users")
st.write("**Users in session state:**")
for username, user_info in st.session_state.persistent_users.items():
    st.write(f"• **{username}**: {user_info['name']} ({user_info['email']})")

st.header("Add Test User")
if st.button("Add Test User"):
    st.session_state.persistent_users['testuser'] = {
        'email': 'test@example.com',
        'name': 'Test User',
        'password': 'testpass'
    }
    st.success("Test user added!")
    st.rerun()

st.header("Stats")
total_users = len(st.session_state.persistent_users)
users_list = list(st.session_state.persistent_users.keys())
st.write(f"• Total users: {total_users}")
st.write(f"• Users list: {users_list}")

# Show admin vs non-admin
admin_users = [u for u in users_list if u == 'sksalapur']
regular_users = [u for u in users_list if u != 'sksalapur']
st.write(f"• Admin users: {admin_users}")
st.write(f"• Regular users: {regular_users}")

if len(regular_users) == 0:
    st.info("No regular users found - this matches what you're seeing!")
else:
    st.success(f"Found {len(regular_users)} regular users")

st.header("Raw Data")
with st.expander("Session State"):
    st.json(dict(st.session_state)) 