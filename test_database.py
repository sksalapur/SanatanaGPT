#!/usr/bin/env python3
"""
Test script for SanatanaGPT database functionality
"""

import sys
import time
from database import (
    init_database, register_user, authenticate_user, 
    save_conversation, get_user_conversations, 
    check_database_health
)

def test_database():
    """Test all database functions."""
    print("🔍 Testing SanatanaGPT Database...")
    
    try:
        # Test 1: Initialize database
        print("\n1. Testing database initialization...")
        init_database()
        
        if check_database_health():
            print("✅ Database initialized successfully!")
        else:
            print("❌ Database health check failed!")
            return False
        
        # Test 2: Register a test user
        print("\n2. Testing user registration...")
        success, message = register_user(
            username="testuser",
            name="Test User",
            email="test@example.com",
            password="testpass123"
        )
        
        if success:
            print(f"✅ User registration: {message}")
        else:
            if "already exists" in message.lower():
                print(f"⚠️ User already exists (expected): {message}")
            else:
                print(f"❌ User registration failed: {message}")
                return False
        
        # Test 3: Authenticate user
        print("\n3. Testing user authentication...")
        auth_success, user_info = authenticate_user("testuser", "testpass123")
        
        if auth_success:
            print(f"✅ Authentication successful for: {user_info['name']}")
            user_id = user_info['id']
        else:
            print("❌ Authentication failed!")
            return False
        
        # Test 4: Test wrong password
        print("\n4. Testing wrong password...")
        wrong_auth, _ = authenticate_user("testuser", "wrongpassword")
        
        if not wrong_auth:
            print("✅ Wrong password correctly rejected!")
        else:
            print("❌ Wrong password was accepted!")
            return False
        
        # Test 5: Save a conversation
        print("\n5. Testing conversation saving...")
        test_chat = [
            {
                'question': 'What is dharma?',
                'answer': 'Dharma refers to righteousness and moral law...',
                'timestamp': time.time()
            }
        ]
        test_context = [{'question': 'What is dharma?', 'answer': 'Dharma refers to righteousness...'}]
        
        conv_success = save_conversation(
            user_id=user_id,
            conversation_id="test_conv_1",
            chat_history=test_chat,
            conversation_context=test_context,
            title="Dharma Discussion"
        )
        
        if conv_success:
            print("✅ Conversation saved successfully!")
        else:
            print("❌ Failed to save conversation!")
            return False
        
        # Test 6: Retrieve conversations
        print("\n6. Testing conversation retrieval...")
        conversations = get_user_conversations(user_id)
        
        if conversations and "test_conv_1" in conversations:
            conv = conversations["test_conv_1"]
            print(f"✅ Retrieved conversation: {conv.get('title', 'Untitled')}")
            print(f"   - Messages: {len(conv.get('chat_history', []))}")
            print(f"   - Context items: {len(conv.get('conversation_context', []))}")
        else:
            print("❌ Failed to retrieve conversations!")
            return False
        
        # Test 7: Update conversation
        print("\n7. Testing conversation update...")
        updated_chat = test_chat + [
            {
                'question': 'What about karma?',
                'answer': 'Karma is the law of cause and effect...',
                'timestamp': time.time()
            }
        ]
        
        update_success = save_conversation(
            user_id=user_id,
            conversation_id="test_conv_1",
            chat_history=updated_chat,
            conversation_context=test_context,
            title="Dharma & Karma Discussion"
        )
        
        if update_success:
            print("✅ Conversation updated successfully!")
            
            # Verify update
            updated_conversations = get_user_conversations(user_id)
            updated_conv = updated_conversations.get("test_conv_1", {})
            if len(updated_conv.get('chat_history', [])) == 2:
                print("✅ Update verified - chat history contains 2 messages")
            else:
                print("❌ Update verification failed!")
                return False
        else:
            print("❌ Failed to update conversation!")
            return False
        
        print("\n🎉 All database tests passed!")
        print("\n📊 Database Summary:")
        print(f"   - Test user ID: {user_id}")
        print(f"   - Test conversations: {len(conversations)}")
        print(f"   - Database file: sanatanagpt.db")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database()
    if not success:
        sys.exit(1)
    
    print("\n✅ Database is ready for SanatanaGPT!")
