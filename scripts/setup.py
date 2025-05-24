#!/usr/bin/env python3
"""
Setup script for Hindu Scriptures Q&A System
Helps users install dependencies and configure the project.
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_env_file():
    """Create .env file from template."""
    env_file = Path(".env")
    template_file = Path("config/env_example.txt")
    
    if env_file.exists():
        print("⚠️ .env file already exists. Skipping creation.")
        return True
    
    if not template_file.exists():
        print("❌ Template file not found!")
        return False
    
    try:
        # Copy template to .env
        with open(template_file, 'r') as template:
            content = template.read()
        
        with open(env_file, 'w') as env:
            env.write(content)
        
        print("✅ Created .env file from template")
        print("🔑 Please add your Google API key to the .env file")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_hindu_texts():
    """Check if Hindu texts directory exists and has files."""
    texts_dir = Path("hindu_texts")
    
    if not texts_dir.exists():
        print("📚 Creating hindu_texts directory...")
        texts_dir.mkdir()
        print("✅ Created hindu_texts directory")
        print("📝 Please add your Hindu scripture text files (.txt) to the hindu_texts folder")
        return True
    
    txt_files = list(texts_dir.glob("*.txt"))
    if not txt_files:
        print("⚠️ No .txt files found in hindu_texts directory")
        print("📝 Please add some Hindu scripture text files (.txt) to the hindu_texts folder")
    else:
        print(f"✅ Found {len(txt_files)} text files in hindu_texts directory")
    
    return True

def main():
    """Main setup function."""
    print("🕉️ Hindu Scriptures Q&A System Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    success = True
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Create .env file
    if not create_env_file():
        success = False
    
    # Check Hindu texts
    if not check_hindu_texts():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Add your Google API key to the .env file")
        print("2. Add Hindu scripture text files to the hindu_texts/ folder")
        print("3. Run: streamlit run app.py")
    else:
        print("⚠️ Setup completed with some issues. Please check the messages above.")

if __name__ == "__main__":
    main() 