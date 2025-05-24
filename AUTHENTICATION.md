# 🔐 SanatanaGPT Authentication System

## Overview

SanatanaGPT now includes a complete user authentication system with persistent conversation history. Each user has their own account with private conversation storage.

## ✨ Features

### 🔑 User Authentication
- **Secure Login/Logout**: Password-based authentication with session management
- **User Registration**: Create new accounts with email validation
- **Password Security**: Bcrypt hashing for secure password storage
- **Session Persistence**: Stay logged in across browser sessions (30 days)

### 💾 Persistent Data Storage
- **User-Specific Conversations**: Each user's conversations are stored separately
- **Cross-Session Persistence**: Conversations saved between app restarts
- **Secure Data Storage**: User data encrypted and stored locally

### 👤 User Management
- **Profile Information**: Display user name and email in sidebar
- **Account Creation**: Simple registration form with validation
- **Multiple Users**: Support for unlimited user accounts

## 🚀 Getting Started

### First Time Setup

1. **Run the App**: Start SanatanaGPT normally
2. **Default Admin Account**: 
   - Username: `admin`
   - Password: `admin123`
   - Email: `admin@sanatanagpt.com`

### Creating a New Account

1. **Access Registration**: Click "Create New Account" on the login page
2. **Fill Details**:
   - Username (unique)
   - Full Name
   - Email address
   - Password (minimum 6 characters)
   - Confirm Password
3. **Submit**: Click "Create New Account"
4. **Login**: Use your new credentials to log in

### Using Your Account

1. **Login**: Enter username and password
2. **Start Chatting**: Create conversations as usual
3. **Persistent History**: Your conversations are automatically saved
4. **Logout**: Click the logout button when done

## 🔧 Technical Details

### File Structure
```
SanatanaGPT/
├── app.py                 # Main application with authentication
├── user_data.pkl          # Encrypted user conversation data
├── users_config.yaml      # User credentials and configuration
├── requirements.txt       # Updated with auth dependencies
└── .gitignore            # Excludes user data files
```

### Dependencies Added
- `streamlit-authenticator`: Authentication framework
- `pyyaml`: Configuration file handling
- `bcrypt`: Password hashing
- `pickle`: Data serialization

### Data Storage

#### User Configuration (`users_config.yaml`)
```yaml
credentials:
  usernames:
    username:
      email: user@example.com
      name: Full Name
      password: hashed_password
cookie:
  expiry_days: 30
  key: sanatana_gpt_auth
  name: sanatana_gpt_cookie
```

#### User Data (`user_data.pkl`)
```python
{
    'username': {
        'conversations': {
            'conv_1': {
                'chat_history': [...],
                'conversation_context': [...],
                'created_at': timestamp
            }
        },
        'current_conversation_id': 'conv_1',
        'conversation_counter': 1
    }
}
```

## 🛡️ Security Features

### Password Security
- **Bcrypt Hashing**: Industry-standard password hashing
- **Salt Generation**: Unique salt for each password
- **Minimum Length**: 6-character minimum requirement

### Session Management
- **Secure Cookies**: HTTP-only session cookies
- **Expiration**: 30-day automatic logout
- **Session Validation**: Server-side session verification

### Data Protection
- **Local Storage**: User data stored locally, not in cloud
- **File Permissions**: Restricted access to data files
- **Git Exclusion**: User data files excluded from version control

## 🔄 Migration from Previous Version

If you were using SanatanaGPT before authentication:

1. **Backup**: Your old conversations are not automatically migrated
2. **Fresh Start**: Create a new account to begin with authentication
3. **Clean Slate**: Enjoy the improved security and persistence

## 🚨 Troubleshooting

### Common Issues

#### "Failed to load authentication configuration"
- **Cause**: Missing or corrupted config files
- **Solution**: Delete `users_config.yaml` and restart the app

#### "Username already exists"
- **Cause**: Trying to register with existing username
- **Solution**: Choose a different username

#### "Password must be at least 6 characters"
- **Cause**: Password too short
- **Solution**: Use a longer password

#### Lost Password
- **Current Solution**: Delete `users_config.yaml` to reset all accounts
- **Future**: Password reset functionality planned

### File Permissions
If you get permission errors:
1. Ensure the app directory is writable
2. Check that `user_data.pkl` and `users_config.yaml` are not read-only

## 🔮 Future Enhancements

### Planned Features
- **Password Reset**: Email-based password recovery
- **Profile Management**: Edit user information
- **Export Conversations**: Download conversation history
- **Admin Panel**: User management interface
- **Cloud Storage**: Optional cloud backup of conversations

### Advanced Authentication
- **Two-Factor Authentication**: SMS/Email verification
- **OAuth Integration**: Google/GitHub login
- **Role-Based Access**: Different user permission levels

## 📞 Support

If you encounter issues with the authentication system:

1. **Check Logs**: Look for error messages in the Streamlit console
2. **File Permissions**: Ensure the app can write to its directory
3. **Dependencies**: Verify all required packages are installed
4. **Fresh Install**: Try deleting data files and starting fresh

## 🎯 Benefits

### For Users
- **Privacy**: Your conversations are private and secure
- **Persistence**: Never lose your conversation history
- **Personalization**: Customized experience for each user
- **Multi-Device**: Access your conversations from any device

### For Administrators
- **User Management**: Track and manage user accounts
- **Data Security**: Secure storage of user information
- **Scalability**: Support for multiple concurrent users
- **Audit Trail**: Track user activity and usage patterns

---

**🕉️ Enjoy your personalized journey through Hindu wisdom with SanatanaGPT! 🕉️**

## 🔧 Recent Updates

### Authentication API Fix (Latest)
- **Issue**: Fixed compatibility with `streamlit-authenticator` v0.4.2
- **Problem**: API changes in the library caused startup failures
- **Solution**: Updated password hashing to use new `Hasher.hash_passwords()` static method
- **Status**: ✅ Resolved - App now works on both local and Streamlit Cloud deployments

For detailed technical information about this fix, see `AUTHENTICATION_FIX.md`. 