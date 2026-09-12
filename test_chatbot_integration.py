#!/usr/bin/env python3
"""
Simple test script to verify chatbot integration
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from base.views.chatbot_views import chat_with_bot, chatbot_status
        print("✓ Chatbot views imported successfully")
    except ImportError as e:
        print(f"✗ Error importing chatbot views: {e}")
        return False
    
    try:
        from base.models import Product, Order, OrderItem
        print("✓ Models imported successfully")
    except ImportError as e:
        print(f"✗ Error importing models: {e}")
        return False
    
    return True

def test_urls():
    """Test if URLs are properly configured"""
    print("\nTesting URL configuration...")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test chatbot status endpoint
        response = client.get('/api/chatbot/status/')
        if response.status_code == 200:
            print("✓ Chatbot status endpoint working")
        else:
            print(f"✗ Chatbot status endpoint returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing URLs: {e}")
        return False
    
    return True

def test_models():
    """Test if models are accessible"""
    print("\nTesting models...")
    
    try:
        from base.models import Product
        
        # Count products
        product_count = Product.objects.count()
        print(f"✓ Found {product_count} products in database")
        
        # Test product context function
        from base.views.chatbot_views import get_product_context
        context = get_product_context()
        print(f"✓ Product context function returned {len(context)} products")
        
    except Exception as e:
        print(f"✗ Error testing models: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=== Chatbot Integration Test ===")
    print()
    
    tests = [
        test_imports,
        test_urls,
        test_models
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("✓ All tests passed! Chatbot integration is working correctly.")
        print("\nNext steps:")
        print("1. Add your Gemini API key to chatbot/.env")
        print("2. Start the Django server: python manage.py runserver")
        print("3. Start the React frontend: cd frontend && npm start")
        print("4. Look for the floating chat button on your site!")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()
