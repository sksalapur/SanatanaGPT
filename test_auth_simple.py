import warnings
warnings.filterwarnings('ignore')
from database import authenticate_user, get_user_by_username

print('Testing authentication...')
print()

# Test user 'admin'
print('=== Testing admin user ===')
success, user_info = authenticate_user('admin', 'admin')
print(f'Success: {success}')
if success:
    print(f'User info: {user_info}')
else:
    user = get_user_by_username('admin')
    if user:
        print('User exists but password failed')
        print(f'Hash starts with: {user["hashed_password"][:30]}')

print()

# Test user 'testuser'  
print('=== Testing testuser ===')
success, user_info = authenticate_user('testuser', 'testuser123')
print(f'Success: {success}')
if success:
    print(f'User info: {user_info}')
else:
    user = get_user_by_username('testuser')
    if user:
        print('User exists but password failed')
        print(f'Hash starts with: {user["hashed_password"][:30]}')

# Also test some common passwords
common_passwords = ['test', 'testuser', 'password', '123456', 'admin123']
print()
print('=== Testing common passwords for testuser ===')
for pwd in common_passwords:
    success, user_info = authenticate_user('testuser', pwd)
    if success:
        print(f'SUCCESS with password: {pwd}')
        break
    else:
        print(f'Failed with: {pwd}')
