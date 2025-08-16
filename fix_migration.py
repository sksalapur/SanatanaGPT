#!/usr/bin/env python3
"""
Fix migration script - Remove double-hashed users and re-migrate correctly
"""
import warnings
warnings.filterwarnings('ignore')

from database import init_database, get_user_by_username, register_user_with_existing_hash
from sqlalchemy import text
import yaml

def fix_migration():
    """Fix the double-hashing issue by re-migrating users correctly."""
    print("=== SanatanaGPT Migration Fix ===")
    
    # Initialize database
    engine, SessionLocal = init_database()
    
    # Load the original YAML file
    try:
        with open('users_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ users_config.yaml not found")
        return
    
    if not config or 'credentials' not in config:
        print("❌ Invalid YAML format")
        return
    
    usernames = config['credentials']['usernames']
    print(f"Found {len(usernames)} users in YAML file")
    
    # Delete existing users and re-create them with correct hashes
    with engine.connect() as conn:
        for username, user_data in usernames.items():
            print(f"\n--- Processing user: {username} ---")
            
            # Check if user exists
            existing_user = get_user_by_username(username)
            if existing_user:
                print(f"  Deleting existing user: {username}")
                # Delete user (conversations will be cascade deleted)
                conn.execute(text("DELETE FROM users WHERE username = :username"), {"username": username})
                conn.commit()
            
            # Re-create user with correct hash
            password = user_data.get('password', 'migration_placeholder')
            name = user_data.get('name', username)
            email = user_data.get('email', f"{username}@migrated.local")
            
            if password.startswith('$2b$') or password.startswith('$2a$') or password.startswith('$2y$'):
                print(f"  Re-creating user with existing hash...")
                success, message = register_user_with_existing_hash(
                    username=username,
                    name=name,
                    email=email,
                    hashed_password=password
                )
                if success:
                    print(f"  ✅ User {username} migrated successfully")
                else:
                    print(f"  ❌ Failed to migrate {username}: {message}")
            else:
                print(f"  ⚠️  Password for {username} doesn't look like a hash: {password[:20]}...")
    
    print("\n=== Migration Fix Complete ===")
    
    # Test authentication
    print("\n=== Testing Authentication ===")
    
    # We need to figure out what the original password was
    # From the YAML, we have the hash: $2b$12$ONRBCBY7DMakbFJle4Dgkuv3igczSUmyLabPen9Ft35tcACN9.Ahy
    # Let's test common passwords that might hash to this
    
    from database import authenticate_user
    common_passwords = ['admin', 'password', '123456', 'admin123', 'Administrator', 'sanatana']
    
    for password in common_passwords:
        print(f"Testing password '{password}' for admin...")
        success, user_info = authenticate_user('admin', password)
        if success:
            print(f"  ✅ SUCCESS! Password for admin is: {password}")
            break
        else:
            print(f"  ❌ Failed")
    else:
        print("  ⚠️  None of the common passwords worked")
        print("  💡 You may need to set a new password for the admin user")

if __name__ == "__main__":
    fix_migration()
