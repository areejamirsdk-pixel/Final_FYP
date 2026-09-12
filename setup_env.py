#!/usr/bin/env python3
"""
Simple script to set up environment variables for the chatbot
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def setup_environment():
    """Set up environment variables"""
    print("Setting up environment for Digital Edge Chatbot...")
    
    # Check if .env file exists in the project root
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("# Digital Edge Ecommerce Chatbot Configuration\n")
            f.write("GEMINI_API_KEY=AIzaSyCf-MMEzrCINC9v9-IGuZg4elpd0Yrh1iI\n")
        print("✓ Created .env file")
    else:
        print("✓ .env file already exists")
    
    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'AIzaSyCf-MMEzrCINC9v9-IGuZg4elpd0Yrh1iI':
        print("\n⚠️  Please set your Gemini API key:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Edit the .env file and replace 'your_gemini_api_key_here' with your actual key")
        print("3. Or set it as an environment variable: export GEMINI_API_KEY=your_key")
        return False
    else:
        print("✓ Gemini API key is configured")
        return True

def test_chatbot():
    """Test the chatbot functionality"""
    print("\nTesting chatbot...")
    
    try:
        from base.views.simple_chatbot_views import get_gemini_response
        
        # Test with a simple message
        response = get_gemini_response("Hello, can you help me?")
        if response and "sorry" not in response.lower():
            print("✓ Chatbot is working correctly")
            print(f"Sample response: {response[:100]}...")
            return True
        else:
            print("✗ Chatbot test failed")
            return False
            
    except Exception as e:
        print(f"✗ Error testing chatbot: {e}")
        return False

def main():
    """Main setup function"""
    print("=== Digital Edge Chatbot Setup ===")
    print()
    
    # Setup environment
    env_ok = setup_environment()
    
    if env_ok:
        # Test chatbot
        test_ok = test_chatbot()
        
        if test_ok:
            print("\n🎉 Setup complete! Your chatbot is ready to use.")
            print("\nTo start the application:")
            print("1. python manage.py runserver")
            print("2. cd frontend && npm start")
            print("3. Look for the floating chat button on your site!")
        else:
            print("\n❌ Setup incomplete. Please check the API key configuration.")
    else:
        print("\n❌ Please configure your Gemini API key first.")

if __name__ == "__main__":
    main()
