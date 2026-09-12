#!/usr/bin/env python3
"""
Setup script for integrating Chainlit chatbot with Django ecommerce site
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Set up the environment for chatbot integration"""
    print("Setting up chatbot integration...")
    
    # Check if .env file exists
    env_file = Path("chatbot/.env")
    if not env_file.exists():
        print("Creating .env file for chatbot...")
        with open(env_file, 'w') as f:
            f.write("# Add your Gemini API key here\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
        print("Please add your Gemini API key to chatbot/.env file")
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Python dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Python dependencies: {e}")
        return False
    
    # Install chatbot dependencies
    print("Installing chatbot dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "../chatbot/pyproject.toml"], check=True)
        print("Chatbot dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing chatbot dependencies: {e}")
        return False
    
    return True

def setup_frontend():
    """Set up frontend dependencies"""
    print("Setting up frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("Frontend directory not found!")
        return False
    
    # Install npm dependencies
    print("Installing npm dependencies...")
    try:
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        print("Frontend dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing frontend dependencies: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("=== Digital Edge Ecommerce Chatbot Integration Setup ===")
    print()
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("Error: Please run this script from the Django project root directory")
        return False
    
    # Setup environment
    if not setup_environment():
        print("Environment setup failed!")
        return False
    
    # Setup frontend
    if not setup_frontend():
        print("Frontend setup failed!")
        return False
    
    print()
    print("=== Setup Complete! ===")
    print()
    print("Next steps:")
    print("1. Add your Gemini API key to chatbot/.env file")
    print("2. Run Django migrations: python manage.py migrate")
    print("3. Start Django server: python manage.py runserver")
    print("4. In another terminal, start the frontend: cd frontend && npm start")
    print("5. The chatbot will be available as a floating button on your site")
    print()
    print("The chatbot is now integrated into your ecommerce site!")
    
    return True

if __name__ == "__main__":
    main()
