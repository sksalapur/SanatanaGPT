import warnings
warnings.filterwarnings('ignore')

# Test database without streamlit context
import os
import sys
import sqlite3

def test_database_direct():
    """Test database directly with SQLite"""
    print("=== Direct SQLite Test ===")
    
    if not os.path.exists('sanatanagpt.db'):
        print("❌ Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect('sanatanagpt.db')
        cursor = conn.cursor()
        
        # Check users table
        cursor.execute("SELECT id, username, email, name, hashed_password FROM users")
        users = cursor.fetchall()
        
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Name: {user[3]}")
            print(f"  Hash: {user[4][:50]}...")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ SQLite error: {e}")
        return False

def test_bcrypt_verification():
    """Test bcrypt directly"""
    print("\n=== Bcrypt Verification Test ===")
    
    try:
        import bcrypt
        
        # Get the actual hash from database
        conn = sqlite3.connect('sanatanagpt.db')
        cursor = conn.cursor()
        cursor.execute("SELECT hashed_password FROM users WHERE username = ?", ('admin',))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            print("❌ Admin user not found")
            return False
        
        stored_hash = result[0].encode('utf-8')
        print(f"Stored hash: {stored_hash[:50]}...")
        
        # Test passwords
        test_passwords = ['admin123', 'admin', 'password', 'Administrator', '123456']
        
        for password in test_passwords:
            is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
            print(f"Password '{password}': {'✅ VALID' if is_valid else '❌ Invalid'}")
            if is_valid:
                return password
        
        return False
        
    except Exception as e:
        print(f"❌ Bcrypt test error: {e}")
        return False

def test_database_functions():
    """Test database functions"""
    print("\n=== Database Functions Test ===")
    
    try:
        # Import without streamlit context issues
        sys.path.append('.')
        
        # Test the actual function
        from database import authenticate_user
        
        correct_password = test_bcrypt_verification()
        if correct_password:
            print(f"\n--- Testing with correct password: {correct_password} ---")
            success, user_info = authenticate_user('admin', correct_password)
            print(f"authenticate_user result: {success}")
            if success:
                print(f"User info: {user_info}")
            else:
                print("❌ Function returned False even with correct password!")
        
    except Exception as e:
        print(f"❌ Database function error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== SanatanaGPT Authentication Deep Debug ===")
    
    if test_database_direct():
        correct_pwd = test_bcrypt_verification()
        test_database_functions()
    
    print("\n=== Debug Complete ===")
