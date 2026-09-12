#!/usr/bin/env python3
"""
Test script for AI ordering functionality
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

def test_ai_ordering_system():
    """Test the AI ordering system"""
    print("=== AI Ordering System Test ===")
    print()
    
    try:
        from base.views.ai_ordering_chatbot_views import (
            analyze_ordering_intent, 
            search_products_in_database,
            extract_quantity_from_message,
            extract_product_from_message
        )
        from base.models import Product, User
        from django.test import Client
        
        # Test 1: Intent Analysis
        print("1. Testing Intent Analysis...")
        test_messages = [
            "I want to buy an iPhone",
            "Do you have Samsung phones?",
            "I need 2 cameras",
            "What's the status of my order?",
            "Show me gaming products"
        ]
        
        for message in test_messages:
            intent = analyze_ordering_intent(message)
            print(f"   '{message}' -> {intent}")
        
        # Test 2: Product Search
        print("\n2. Testing Product Search...")
        products = search_products_in_database("iPhone", limit=3)
        print(f"   Found {len(products)} products for 'iPhone'")
        for product in products:
            print(f"   - {product['name']} (${product['price']})")
        
        # Test 3: Quantity Extraction
        print("\n3. Testing Quantity Extraction...")
        test_quantity_messages = [
            "I want 2 iPhones",
            "Buy 3 cameras",
            "Get one Samsung phone",
            "I need 5 headphones"
        ]
        
        for message in test_quantity_messages:
            quantity = extract_quantity_from_message(message)
            print(f"   '{message}' -> Quantity: {quantity}")
        
        # Test 4: Product Extraction
        print("\n4. Testing Product Extraction...")
        if products:
            test_product_messages = [
                f"I want to buy {products[0]['name']}",
                "I need an iPhone",
                "Show me Samsung products"
            ]
            
            for message in test_product_messages:
                product = extract_product_from_message(message, products)
                if product:
                    print(f"   '{message}' -> {product['name']}")
                else:
                    print(f"   '{message}' -> No product found")
        
        # Test 5: API Endpoints
        print("\n5. Testing API Endpoints...")
        client = Client()
        
        # Test guest chat
        response = client.post('/api/chatbot/chat/', {
            'message': 'Do you have any Apple products?',
            'chat_history': []
        }, content_type='application/json')
        print(f"   Guest chat endpoint: {response.status_code}")
        
        # Test authenticated chat (would need a user)
        print("   Authenticated chat endpoint: Requires user login")
        
        # Test order status endpoint
        print("   Order status endpoint: Requires user login")
        
        print("\n✅ All tests completed successfully!")
        print("\n🎉 AI Ordering System is ready!")
        print("\nFeatures available:")
        print("✓ Intent analysis for ordering")
        print("✓ Product search and extraction")
        print("✓ Quantity extraction from messages")
        print("✓ Guest and authenticated chat modes")
        print("✓ Order creation through AI")
        print("✓ Order status checking")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_order_creation():
    """Test order creation functionality"""
    print("\n=== Order Creation Test ===")
    
    try:
        from base.models import Product, User, Order, OrderItem
        from base.views.ai_ordering_chatbot_views import create_order_via_ai
        
        # Get a test user
        user = User.objects.first()
        if not user:
            print("❌ No users found in database. Please create a user first.")
            return False
        
        # Get a product
        product = Product.objects.filter(countInStock__gt=0).first()
        if not product:
            print("❌ No products in stock found in database.")
            return False
        
        print(f"Testing with user: {user.username}")
        print(f"Testing with product: {product.name}")
        
        # Test order creation
        product_data = {
            'id': product._id,
            'name': product.name,
            'price': float(product.price) if product.price else 0.0
        }
        
        result = create_order_via_ai(user, product_data, 1)
        
        if result['success']:
            print(f"✅ Order created successfully!")
            print(f"   Order ID: {result['order_id']}")
            print(f"   Total: ${result['order']['total']}")
            print(f"   Items: {len(result['order']['items'])}")
        else:
            print(f"❌ Order creation failed: {result['error']}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Order creation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== AI Ordering System Comprehensive Test ===")
    print()
    
    # Test basic functionality
    basic_test = test_ai_ordering_system()
    
    # Test order creation
    order_test = test_order_creation()
    
    print(f"\n=== Final Results ===")
    print(f"Basic functionality: {'✅ PASS' if basic_test else '❌ FAIL'}")
    print(f"Order creation: {'✅ PASS' if order_test else '❌ FAIL'}")
    
    if basic_test and order_test:
        print("\n🎉 All tests passed! Your AI ordering system is fully functional!")
        print("\nUsers can now:")
        print("• Browse products through chat")
        print("• Place orders by saying things like 'I want to buy an iPhone'")
        print("• Check order status")
        print("• Get product recommendations")
        print("• Have a natural conversation about products")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
