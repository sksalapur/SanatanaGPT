# Authentication Fix for Streamlit-Authenticator 0.4.2

## Issue
The SanatanaGPT application was failing to start on both local and Streamlit Cloud deployments due to API changes in `streamlit-authenticator` version 0.4.2.

### Error Messages
```
TypeError: Hasher.__init__() takes 1 positional argument but 2 were given
AttributeError: 'Hasher' object has no attribute 'generate'
DeprecationError: Please note that the 'pre_authorized' parameter has been removed from the Authenticate class
ValueError: Location must be one of 'main' or 'sidebar' or 'unrendered'
```

## Root Cause
The `streamlit-authenticator` library API changed significantly in version 0.4.2:
- The `Hasher` class no longer accepts arguments in its constructor
- The `generate()` method was removed
- Password hashing is now done via the static method `Hasher.hash_passwords()`
- The `preauthorized` parameter was removed from the `Authenticate` class constructor
- The `login()` and `logout()` methods now use keyword arguments instead of positional arguments

## Solution Applied

### Before (Broken Code)
```python
# Old API - doesn't work in v0.4.2
hashed_passwords = stauth.Hasher(['admin123']).generate()
hashed_password = stauth.Hasher().generate([password])[0]

# Old Authenticate class instantiation
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']  # This parameter was removed
)

# Old login/logout calls
name, authentication_status, username = authenticator.login('Login to SanatanaGPT', 'main')
authenticator.logout('Logout', 'main')
```

### After (Fixed Code)
```python
# New API - works with v0.4.2
config = {
    'credentials': {
        'usernames': {
            'admin': {
                'password': 'admin123'  # Plain text
            }
        }
    }
}
# Hash all passwords in the credentials dictionary
stauth.Hasher.hash_passwords(config['credentials'])

# New Authenticate class instantiation (without preauthorized)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# New login/logout calls with keyword arguments
name, authentication_status, username = authenticator.login(location='main')
authenticator.logout(location='main')
```

## Files Modified
1. **app.py**
   - `create_users_config()` function: Updated to use new hashing API
   - `register_new_user()` function: Updated to use new hashing API
   - `main()` function: Removed deprecated `preauthorized` parameter and fixed login/logout calls

## Changes Made

### create_users_config() Function
- Store plain text password in config dictionary
- Call `stauth.Hasher.hash_passwords(config['credentials'])` to hash all passwords
- This automatically hashes all passwords in the credentials structure

### register_new_user() Function
- Add new user with plain text password
- Call `stauth.Hasher.hash_passwords(config['credentials'])` to hash all passwords
- This ensures new user passwords are properly hashed

### main() Function
- Removed the deprecated `config['preauthorized']` parameter from `stauth.Authenticate()` constructor
- Updated `authenticator.login()` to use `location='main'` keyword argument
- Updated `authenticator.logout()` to use `location='main'` keyword argument
- The preauthorized functionality is now handled directly in the `register_user` widget

## Testing
- ✅ Local development: App starts successfully
- ✅ Password hashing: Verified bcrypt hashes are generated
- ✅ Configuration files: `users_config.yaml` created with hashed passwords
- ✅ Authenticate class: Instantiation works without deprecated parameters
- ✅ Login/logout: Methods work with new keyword argument format
- ✅ Deployment: Changes pushed to GitHub for Streamlit Cloud

## Default Credentials
- **Username:** admin
- **Password:** admin123
- **Email:** admin@sanatanagpt.com

## Next Steps
1. The app should now deploy successfully on Streamlit Cloud
2. Users can log in with the default admin credentials
3. New user registration should work properly
4. All authentication features should function as expected

## References
- [Streamlit-Authenticator v0.4.2 Documentation](https://pypi.org/project/streamlit-authenticator/)
- [GitHub Repository](https://github.com/mkhorasani/Streamlit-Authenticator)