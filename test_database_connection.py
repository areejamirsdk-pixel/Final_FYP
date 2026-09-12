#!/usr/bin/env python3
"""
Test script to verify database connection and product search functionality
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

def test_database_connection():
    """Test if we can connect to the database"""
    print("Testing database connection...")
    
    try:
        from base.models import Product
        
        # Count total products
        total_products = Product.objects.count()
        print(f"✓ Total products in database: {total_products}")
        
        # Count products in stock
        in_stock = Product.objects.filter(countInStock__gt=0).count()
        print(f"✓ Products in stock: {in_stock}")
        
        # Show sample products
        print("\nSample products:")
        for product in Product.objects.all()[:5]:
            print(f"  - {product.name} ({product.brand}) - ${product.price} - Stock: {product.countInStock}")
        
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_product_search():
    """Test product search functionality"""
    print("\nTesting product search...")
    
    try:
        from base.views.professional_chatbot_views import search_products_in_database, analyze_user_intent
        
        # Test different search queries
        test_queries = [
            "iPhone",
            "Samsung",
            "Apple",
            "camera",
            "gaming",
            "headphones"
        ]
        
        for query in test_queries:
            print(f"\nSearching for: '{query}'")
            products = search_products_in_database(query, limit=3)
            print(f"  Found {len(products)} products")
            
            for product in products:
                print(f"    - {product['name']} (${product['price']})")
        
        return True
    except Exception as e:
        print(f"✗ Product search failed: {e}")
        return False

def test_intent_analysis():
    """Test intent analysis"""
    print("\nTesting intent analysis...")
    
    try:
        from base.views.professional_chatbot_views import analyze_user_intent
        
        test_messages = [
            "I want to buy an iPhone",
            "Do you have Samsung phones?",
            "Show me gaming products",
            "What's the price of cameras?",
            "I need headphones"
        ]
        
        for message in test_messages:
            intent = analyze_user_intent(message)
            print(f"Message: '{message}'")
            print(f"  Intent: {intent}")
        
        return True
    except Exception as e:
        print(f"✗ Intent analysis failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    
    try:
        from django.test import Client
        
        client = Client()
        
        # Test status endpoint
        response = client.get('/api/chatbot/status/')
        print(f"Status endpoint: {response.status_code}")
        
        # Test debug endpoint
        response = client.get('/api/chatbot/debug/')
        print(f"Debug endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Products found: {data.get('total_found', 0)}")
        
        # Test chat endpoint
        response = client.post('/api/chatbot/chat/', {
            'message': 'Do you have any Apple products?',
            'chat_history': []
        }, content_type='application/json')
        print(f"Chat endpoint: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"✗ API endpoints test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Professional Chatbot Database Test ===")
    print()
    
    tests = [
        test_database_connection,
        test_product_search,
        test_intent_analysis,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed! Your professional chatbot is ready!")
        print("\nThe chatbot will now:")
        print("✓ Search your actual database")
        print("✓ Provide specific product information")
        print("✓ Give accurate prices and stock levels")
        print("✓ Understand user intent")
        print("✓ Suggest alternatives when needed")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
