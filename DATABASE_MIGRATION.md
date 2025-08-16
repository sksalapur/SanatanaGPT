# 🚀 SQLite Database Migration Guide

## Overview

SanatanaGPT has been successfully migrated from file-based storage (`.pkl` and `.yaml`) to a persistent SQLite database. This solves the issue of data loss when Streamlit Cloud puts the app to sleep.

## ✨ What's New

### 🗄️ SQLite Database
- **Persistent storage**: Data survives app restarts and Streamlit Cloud sleep cycles
- **Better performance**: Faster queries and data operations
- **Data integrity**: ACID compliance ensures data consistency
- **Scalability**: Can handle thousands of users and conversations

### 🔧 Technical Changes
- **SQLAlchemy ORM**: Clean, maintainable database models
- **Bcrypt encryption**: Enhanced password security
- **Automatic migration**: Seamlessly imports data from old format
- **Database health checks**: Ensures reliability

## 📁 New File Structure

```
SanatanaGPT/
├── app.py                    # Main application (updated)
├── database.py              # NEW: Database models and functions
├── test_database.py         # NEW: Database testing script
├── sanatanagpt.db           # NEW: SQLite database (auto-created)
├── requirements.txt         # Updated with SQLAlchemy & bcrypt
├── .gitignore              # Updated to exclude database files
└── ... (other files unchanged)
```

## 🔄 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Conversations Table
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    conversation_id VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    chat_history TEXT NOT NULL,
    conversation_context TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## 🔑 Key Features

### 🔐 Enhanced Authentication
- **Custom login system**: No longer dependent on streamlit-authenticator YAML format
- **Database-backed**: User credentials stored securely in SQLite
- **Bcrypt hashing**: Industry-standard password encryption
- **Session management**: Persistent login sessions

### 💾 Persistent Conversations
- **Real-time saving**: Conversations saved to database immediately
- **Cross-session persistence**: Chat history survives app restarts
- **User isolation**: Each user's conversations are private
- **Conversation metadata**: Titles, timestamps, and context preserved

### 🔄 Automatic Migration
- **Zero-data-loss**: Automatically imports from old `.pkl` and `.yaml` files
- **One-time process**: Migration runs once when old files are detected
- **Backward compatibility**: Old files are preserved during migration

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test Database (Optional)
```bash
python test_database.py
```

### 3. Run the Application
```bash
streamlit run app.py
```

### 4. Migration (Automatic)
- If you have existing `user_data.pkl` or `users_config.yaml` files:
- The app will automatically detect and migrate your data
- You'll see a migration message on first startup
- Old files are preserved for backup

## 🔧 Database Functions

### User Management
```python
# Register new user
success, message = register_user(username, name, email, password)

# Authenticate user
auth_success, user_info = authenticate_user(username, password)

# Get user info
user_info = get_user_by_username(username)
user_info = get_user_by_email(email)
```

### Conversation Management
```python
# Save conversation
save_conversation(user_id, conversation_id, chat_history, context, title)

# Get user conversations
conversations = get_user_conversations(user_id)

# Delete conversation
delete_conversation(user_id, conversation_id)

# Get conversation count
count = get_conversation_count(user_id)
```

### Database Health
```python
# Check database status
if check_database_health():
    print("Database is healthy!")
```

## 🛡️ Security Improvements

### Password Security
- **Bcrypt hashing**: Replaces weaker hashing methods
- **Salt generation**: Unique salt for each password
- **Verification**: Secure password checking

### Data Protection
- **Local storage**: Database stored locally (not in cloud by default)
- **Git exclusion**: Database files excluded from version control
- **User isolation**: Each user can only access their own data

## 🔄 Migration Details

### From Old Format
The migration process handles:

1. **User Migration**: 
   - Usernames, names, emails from `users_config.yaml`
   - Password hashes converted to new format
   - Missing emails get placeholder values

2. **Conversation Migration**:
   - Chat histories from `user_data.pkl`
   - Conversation contexts preserved
   - Timestamps and metadata maintained

### Manual Migration (if needed)
If automatic migration fails, you can:

1. **Check old files**:
   ```bash
   ls -la user_data.pkl users_config.yaml
   ```

2. **Run migration manually**:
   ```python
   from database import migrate_old_data_if_needed
   migrate_old_data_if_needed()
   ```

3. **Verify migration**:
   ```bash
   python test_database.py
   ```

## 📊 Performance Benefits

### Speed Improvements
- **Faster startup**: No need to load large pickle files
- **Efficient queries**: SQL-based data retrieval
- **Optimized storage**: Normalized database structure

### Memory Usage
- **Lower memory footprint**: Data loaded on-demand
- **Better caching**: SQLAlchemy handles query optimization
- **Scalable**: Handles large datasets efficiently

## 🚨 Troubleshooting

### Common Issues

#### "Database health check failed"
```bash
# Delete and recreate database
rm sanatanagpt.db
python test_database.py
```

#### "Database initialization failed"
```bash
# Check file permissions
ls -la sanatanagpt.db
# Ensure the directory is writable
```

#### "Migration failed"
```bash
# Check old file formats
python -c "import pickle; print(pickle.load(open('user_data.pkl', 'rb')))"
python -c "import yaml; print(yaml.safe_load(open('users_config.yaml')))"
```

### Database Maintenance

#### Backup Database
```bash
cp sanatanagpt.db sanatanagpt_backup_$(date +%Y%m%d).db
```

#### Reset Database
```bash
rm sanatanagpt.db
python test_database.py
```

#### View Database Contents
```bash
sqlite3 sanatanagpt.db
.tables
SELECT * FROM users;
SELECT * FROM conversations;
```

## 🔮 Future Enhancements

### Planned Features
- **Database encryption**: Encrypt database file at rest
- **Cloud storage**: Optional cloud database support
- **Backup system**: Automated backup and restore
- **Analytics**: Usage statistics and insights
- **Import/Export**: Conversation backup and sharing

### Advanced Features
- **Multi-database**: Support for PostgreSQL/MySQL
- **Replication**: Database synchronization across instances
- **Caching**: Redis integration for high-performance queries
- **Search**: Full-text search across conversations

## 📞 Support

### Getting Help
1. **Check logs**: Look for error messages in terminal
2. **Test database**: Run `python test_database.py`
3. **Verify files**: Ensure database file exists and is writable
4. **Check dependencies**: Verify SQLAlchemy and bcrypt are installed

### Reporting Issues
When reporting database issues, include:
- Error messages from terminal
- Output of `python test_database.py`
- Operating system and Python version
- Database file size: `ls -lh sanatanagpt.db`

---

**🕉️ Your spiritual conversations are now securely preserved in the database! 🕉️**

## ✅ Migration Checklist

- [x] SQLAlchemy models created
- [x] Database initialization implemented
- [x] User authentication with bcrypt
- [x] Conversation storage and retrieval
- [x] Automatic migration from old format
- [x] Database health checks
- [x] Updated requirements.txt
- [x] Updated .gitignore
- [x] Comprehensive testing script
- [x] Documentation and guides

**Status: ✅ COMPLETE - Ready for production deployment!**
