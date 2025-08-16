#!/usr/bin/env python3

# Test if there are any connection or session issues
import warnings
warnings.filterwarnings('ignore')

print("=== Testing Database Session Management ===")

from database import get_db_session, authenticate_user
import time

def test_multiple_sessions():
    """Test if multiple database sessions work correctly"""
    print("\n--- Testing multiple database sessions ---")
    
    for i in range(3):
        print(f"Session {i+1}:")
        try:
            session = get_db_session()
            print(f"  ✅ Session created successfully")
            session.close()
            print(f"  ✅ Session closed successfully")
        except Exception as e:
            print(f"  ❌ Session error: {e}")

def test_concurrent_auth():
    """Test multiple authentication attempts"""
    print("\n--- Testing multiple authentication attempts ---")
    
    for i in range(3):
        print(f"Attempt {i+1}:")
        try:
            success, user_info = authenticate_user('admin', 'admin123')
            print(f"  Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
            if success:
                print(f"  User: {user_info['name']}")
        except Exception as e:
            print(f"  ❌ Auth error: {e}")
        
        time.sleep(0.5)

def test_wrong_credentials():
    """Test with wrong credentials to ensure it properly fails"""
    print("\n--- Testing wrong credentials ---")
    
    test_cases = [
        ('admin', 'wrongpassword'),
        ('wronguser', 'admin123'),
        ('admin', ''),
        ('', 'admin123'),
    ]
    
    for username, password in test_cases:
        try:
            success, user_info = authenticate_user(username, password)
            expected = "FAILED" if not success else "UNEXPECTED SUCCESS"
            print(f"  {username}/{password}: {expected}")
        except Exception as e:
            print(f"  {username}/{password}: ERROR - {e}")

if __name__ == "__main__":
    test_multiple_sessions()
    test_concurrent_auth()
    test_wrong_credentials()
    
    print("\n=== Final Test ===")
    print("Testing the exact credentials you should use:")
    success, user_info = authenticate_user('admin', 'admin123')
    if success:
        print("✅ SUCCESS: Use username='admin' password='admin123'")
    else:
        print("❌ FAILED: Something is wrong with the database")
