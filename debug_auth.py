#!/usr/bin/env python3
"""
Debug script to test authentication and database functionality
"""
import os
import sys
import sqlite3

# Try to import database functions without Streamlit context warnings
import warnings
warnings.filterwarnings("ignore")

from database import init_database, authenticate_user, get_user_by_username
from sqlalchemy import text

def test_database():
    """Test database connectivity and data"""
    print("=== Database Connectivity Test ===")
    
    # Check if database file exists
    db_exists = os.path.exists('sanatanagpt.db')
    print(f"Database file exists: {db_exists}")
    
    if db_exists:
        print(f"Database file size: {os.path.getsize('sanatanagpt.db')} bytes")
    
    try:
        # Test SQLAlchemy connection
        engine, SessionLocal = init_database()
        print("✅ SQLAlchemy connection: OK")
        
        # Check tables and data using SQLAlchemy
        with engine.connect() as conn:
            # Check users table
            result = conn.execute(text("SELECT count(*) FROM users"))
            user_count = result.fetchone()[0]
            print(f"Total users in database: {user_count}")
            
            if user_count > 0:
                result = conn.execute(text("SELECT username, email, name FROM users"))
                users = result.fetchall()
                print("Users found:")
                for user in users:
                    print(f"  - Username: {user[0]}, Email: {user[1]}, Name: {user[2]}")
            
            # Check conversations table
            result = conn.execute(text("SELECT count(*) FROM conversations"))
            conv_count = result.fetchone()[0]
            print(f"Total conversations in database: {conv_count}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    return True

def test_authentication():
    """Test authentication with sample data"""
    print("\n=== Authentication Test ===")
    
    try:
        # Test with a known user (you'll need to provide real credentials)
        print("To test authentication, please provide credentials of an existing user:")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        if not username or not password:
            print("Skipping authentication test (no credentials provided)")
            return
        
        # Test authentication
        user = authenticate_user(username, password)
        if user:
            print(f"✅ Authentication successful for user: {user.name} ({user.email})")
            print(f"   User ID: {user.id}")
            print(f"   Created: {user.created_at}")
        else:
            print("❌ Authentication failed")
            
            # Check if user exists but password is wrong
            existing_user = get_user_by_username(username)
            if existing_user:
                print(f"   User '{username}' exists in database but password is incorrect")
                print(f"   Stored hash starts with: {existing_user.hashed_password[:20]}...")
            else:
                print(f"   User '{username}' not found in database")
                
    except Exception as e:
        print(f"❌ Authentication error: {e}")

def test_password_verification():
    """Test bcrypt password verification"""
    print("\n=== Password Hash Test ===")
    
    try:
        import bcrypt
        
        # Test bcrypt functionality
        test_password = "testpass123"
        hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        
        # Verify the password
        is_valid = bcrypt.checkpw(test_password.encode('utf-8'), hashed)
        print(f"✅ Bcrypt test: {is_valid}")
        
    except Exception as e:
        print(f"❌ Bcrypt error: {e}")

if __name__ == "__main__":
    print("SanatanaGPT Authentication Debug Tool")
    print("=" * 50)
    
    # Test database
    db_ok = test_database()
    
    if db_ok:
        # Test password hashing
        test_password_verification()
        
        # Test authentication
        test_authentication()
    else:
        print("Database tests failed. Cannot proceed with authentication tests.")
