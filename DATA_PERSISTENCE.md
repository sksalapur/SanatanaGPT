# 📊 Data Persistence Guide for SanatanaGPT

## 🔍 The Problem

When deployed on Streamlit Cloud, the app restarts periodically, causing all user accounts and conversation data to be lost. This happens because:

1. **File-based storage** (pickle files, YAML files) gets reset on app restart
2. **Session state** is temporary and doesn't persist across app restarts
3. **Streamlit Cloud** doesn't provide permanent file storage

## ✅ Current Solution

We've implemented a **hybrid approach** that provides better persistence:

### 🔧 How It Works

1. **Session State Storage**: User data is stored in `st.session_state` instead of files
2. **Admin Account**: Always available with default credentials
3. **Memory-based**: Data persists during the current session
4. **Backup/Export**: Admin can export user data for backup

### 👤 Default Admin Account

- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@sanatanagpt.com`

The admin account is always available and provides access to:
- User statistics
- Data export functionality
- User management

## 🚀 Setting Up Permanent Persistence (Optional)

For true data persistence across app restarts, you can configure external storage:

### Option 1: Streamlit Secrets (Recommended)

Add pre-configured users to your Streamlit secrets:

```toml
# .streamlit/secrets.toml (for local development)
# Or add to Streamlit Cloud App Settings > Secrets

[users]
admin = { email = "admin@sanatanagpt.com", name = "Administrator", password = "$2b$12$..." }
user1 = { email = "user1@example.com", name = "User One", password = "$2b$12$..." }
```

### Option 2: External Database Integration

For production use, consider integrating with:

- **Supabase** (PostgreSQL)
- **Firebase** (NoSQL)
- **MongoDB Atlas**
- **AWS DynamoDB**

## 📋 Current Features

### ✅ What Persists During Session
- User accounts created during the session
- All conversation history
- User preferences and settings
- Authentication state

### ❌ What Resets on App Restart
- User accounts (except admin)
- Conversation history
- Custom settings

### 🔧 Admin Features
- View total users and conversations
- Export user data as JSON backup
- Monitor system statistics
- User management

## 💡 Best Practices

### For Users
1. **Regular Backups**: Ask admin to export data regularly
2. **Important Conversations**: Copy important conversations to external notes
3. **Account Recreation**: Be prepared to recreate accounts after app restarts

### For Admins
1. **Regular Exports**: Export user data weekly or before major updates
2. **User Communication**: Inform users about data persistence limitations
3. **Backup Storage**: Store exported data in secure location

## 🔄 Data Export/Import Process

### Export Process
1. Login as admin
2. Go to Admin Panel in sidebar
3. Click "Export User Data"
4. Download the JSON backup file

### Import Process (Manual)
Currently, import must be done by modifying the code or using Streamlit secrets.

## 🛠️ Technical Implementation

### Data Structure
```python
# User credentials
st.session_state.persistent_users = {
    'username': {
        'email': 'user@example.com',
        'name': 'User Name',
        'password': 'hashed_password'
    }
}

# User conversation data
st.session_state.persistent_user_data = {
    'username': {
        'conversations': {...},
        'current_conversation_id': 'conv_1',
        'conversation_counter': 1
    }
}
```

### Key Functions
- `init_persistent_storage()`: Initialize storage system
- `export_user_data()`: Create backup JSON
- `import_user_data()`: Restore from backup
- `get_user_stats()`: System statistics

## 🔮 Future Improvements

1. **Database Integration**: Connect to external database
2. **Automatic Backups**: Scheduled data exports
3. **User Self-Service**: Allow users to export their own data
4. **Cloud Storage**: Integration with Google Drive, Dropbox, etc.
5. **Data Encryption**: Enhanced security for stored data

## 📞 Support

If you need help with data persistence:

1. **Check Admin Panel**: Login as admin to see current status
2. **Export Data**: Regularly backup important conversations
3. **Contact Support**: Report issues with data loss

## 🔐 Security Notes

- Passwords are hashed using bcrypt
- Session data is temporary and secure
- Admin access is required for system management
- No sensitive data is stored in plain text

---

**Remember**: This solution provides better persistence than file-based storage, but for production use with many users, consider implementing a proper database backend. 