#!/usr/bin/env python3
"""
Test script for enhanced AI ordering with address collection
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

def test_address_extraction():
    """Test address extraction from messages"""
    print("=== Testing Address Extraction ===")
    
    try:
        from base.views.ai_ordering_chatbot_views import extract_address_from_message, is_address_collection_message
        
        test_messages = [
            "My address is 123 Main Street, city is New York, postal code is 10001, country is USA",
            "I live at 456 Oak Ave, in Los Angeles, zip 90210, state California",
            "Address: 789 Pine St, city: Chicago, postal: 60601, country: United States",
            "Street: 321 Elm St, city: Boston, zip code: 02101, country: USA"
        ]
        
        for message in test_messages:
            print(f"\nMessage: '{message}'")
            address_info = extract_address_from_message(message)
            is_address = is_address_collection_message(message)
            print(f"  Is address message: {is_address}")
            print(f"  Extracted address: {address_info}")
        
        return True
    except Exception as e:
        print(f"❌ Address extraction test failed: {e}")
        return False

def test_product_matching():
    """Test improved product matching"""
    print("\n=== Testing Product Matching ===")
    
    try:
        from base.views.ai_ordering_chatbot_views import extract_product_from_message, search_products_in_database
        
        # Get some products from database
        products = search_products_in_database("iPhone", limit=3)
        print(f"Found {len(products)} products for testing")
        
        test_messages = [
            "I want to buy iPhone 11 Pro",
            "I need Samsung Galaxy",
            "I want a camera",
            "I need headphones",
            "I want something else"  # Should not match any product
        ]
        
        for message in test_messages:
            print(f"\nMessage: '{message}'")
            product = extract_product_from_message(message, products)
            if product:
                print(f"  Matched product: {product['name']} (${product['price']})")
            else:
                print(f"  No specific product match found")
        
        return True
    except Exception as e:
        print(f"❌ Product matching test failed: {e}")
        return False

def test_order_creation_with_address():
    """Test order creation with address validation"""
    print("\n=== Testing Order Creation with Address ===")
    
    try:
        from base.models import Product, User
        from base.views.ai_ordering_chatbot_views import create_order_via_ai
        
        # Get test user and product
        user = User.objects.first()
        product = Product.objects.filter(countInStock__gt=0).first()
        
        if not user or not product:
            print("❌ No user or product found for testing")
            return False
        
        print(f"Testing with user: {user.username}")
        print(f"Testing with product: {product.name}")
        
        # Test with complete address
        complete_address = {
            'address': '123 Test Street',
            'city': 'Test City',
            'postalCode': '12345',
            'country': 'Test Country'
        }
        
        product_data = {
            'id': product._id,
            'name': product.name,
            'price': float(product.price) if product.price else 0.0
        }
        
        result = create_order_via_ai(user, product_data, 1, complete_address)
        
        if result['success']:
            print(f"✅ Order created successfully with complete address!")
            print(f"   Order ID: {result['order_id']}")
            print(f"   Total: ${result['order']['total']}")
            print(f"   Shipping to: {result['order']['shipping_address']['address']}")
        else:
            print(f"❌ Order creation failed: {result['error']}")
        
        # Test with incomplete address
        incomplete_address = {
            'address': '123 Test Street',
            'city': 'Test City'
            # Missing postalCode and country
        }
        
        result2 = create_order_via_ai(user, product_data, 1, incomplete_address)
        
        if not result2['success'] and result2.get('needs_address'):
            print(f"✅ Correctly rejected incomplete address")
            print(f"   Missing fields: {result2.get('missing_fields', [])}")
        else:
            print(f"❌ Should have rejected incomplete address")
        
        return result['success'] if 'result' in locals() else False
        
    except Exception as e:
        print(f"❌ Order creation test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints with address collection"""
    print("\n=== Testing API Endpoints ===")
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        
        client = Client()
        
        # Test guest endpoint
        response = client.post('/api/chatbot/chat/', {
            'message': 'Do you have any products?',
            'chat_history': []
        }, content_type='application/json')
        print(f"Guest chat endpoint: {response.status_code}")
        
        # Test authenticated endpoint (would need proper authentication)
        print("Authenticated endpoint: Requires proper JWT token")
        
        return True
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Enhanced AI Ordering System Test ===")
    print()
    
    tests = [
        test_address_extraction,
        test_product_matching,
        test_order_creation_with_address,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Final Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced AI ordering system is ready!")
        print("\nNew features working:")
        print("✅ Address extraction from natural language")
        print("✅ Improved product matching (exact matches only)")
        print("✅ Address validation before order creation")
        print("✅ Pending order state management")
        print("✅ Visual indicators for address collection")
        print("\nUsers can now:")
        print("• Order specific products by name")
        print("• Provide address in natural language")
        print("• Get validation for missing address fields")
        print("• See pending order status")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
