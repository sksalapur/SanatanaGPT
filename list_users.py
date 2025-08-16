#!/usr/bin/env python3
"""
List all registered users in the SanatanaGPT database (excluding passwords)
"""
from database import init_database
from sqlalchemy import text

def list_users():
    engine, SessionLocal = init_database()
    with engine.connect() as conn:
        result = conn.execute(text('SELECT id, username, email, name, created_at FROM users'))
        users = result.fetchall()
        print(f"Total users: {len(users)}\n")
        for user in users:
            print(f"ID: {user[0]} | Username: {user[1]} | Email: {user[2]} | Name: {user[3]} | Created: {user[4]}")

if __name__ == "__main__":
    list_users()
