#!/usr/bin/env python3
"""
Minimal CLI for registering and logging in a user to SanatanaGPT (bypassing Streamlit)
"""
import getpass
from database import register_user, authenticate_user, get_user_by_username

def main():
    print("=== SanatanaGPT CLI Registration & Login Test ===\n")
    username = input("Enter new username: ").strip()
    name = input("Enter your name: ").strip()
    email = input("Enter your email: ").strip()
    password = getpass.getpass("Enter password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("❌ Passwords do not match!")
        return

    # Register user
    success, message = register_user(username, name, email, password)
    print(f"Register: {message}")
    if not success:
        return

    # Test login
    print("\nNow testing login...")
    test_password = getpass.getpass("Enter password to login: ")
    success, user_info = authenticate_user(username, test_password)
    if success:
        print(f"✅ Login successful! Welcome, {user_info['name']} ({user_info['email']})")
    else:
        print("❌ Login failed. Check your password or registration logic.")

    # Show user info from DB
    print("\nUser info from DB:")
    print(get_user_by_username(username))

if __name__ == "__main__":
    main()
