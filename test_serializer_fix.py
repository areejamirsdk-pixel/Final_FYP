#!/usr/bin/env python3
"""
Test OrderItemSerializer image URL generation
"""

import os
import sys
import django
from pathlib import Path

project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_order_item_serializer():
    """Test that OrderItemSerializer returns correct image URLs"""
    print("=== Testing OrderItemSerializer Image URLs ===")
    
    try:
        from base.models import OrderItem
        from base.serializers import OrderItemSerializer
        
        # Get the most recent order item
        order_item = OrderItem.objects.last()
        if order_item:
            print(f"Order Item: {order_item.name}")
            print(f"Raw image field: '{order_item.image}'")
            
            # Test serializer
            serializer = OrderItemSerializer(order_item)
            serialized_data = serializer.data
            print(f"Serialized image URL: '{serialized_data['image']}'")
            
            # Check if it's a proper URL
            if serialized_data['image'].startswith('/images/'):
                print("✅ Image URL is correctly formatted")
                return True
            else:
                print("❌ Image URL is not properly formatted")
                return False
        else:
            print("No order items found")
            return False
        
    except Exception as e:
        print(f"❌ Serializer test failed: {e}")
        return False

def test_different_image_formats():
    """Test different image formats"""
    print("\n=== Testing Different Image Formats ===")
    
    try:
        from base.models import OrderItem
        from base.serializers import OrderItemSerializer
        
        # Test with different image formats
        test_cases = [
            ("airpods.jpg", "/images/airpods.jpg"),
            ("phone.jpg", "/images/phone.jpg"),
            ("/images/camera.jpg", "/images/camera.jpg"),
            ("", "/placeholder.png"),
            (None, "/placeholder.png")
        ]
        
        all_passed = True
        for input_image, expected_output in test_cases:
            # Create a mock order item
            order_item = OrderItem()
            order_item.image = input_image
            order_item.name = "Test Product"
            
            serializer = OrderItemSerializer(order_item)
            result = serializer.data['image']
            
            if result == expected_output:
                print(f"✅ '{input_image}' -> '{result}'")
            else:
                print(f"❌ '{input_image}' -> '{result}' (expected: '{expected_output}')")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Image format test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== OrderItemSerializer Image URL Test ===\n")
    
    tests = [
        test_order_item_serializer,
        test_different_image_formats
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Results: {passed}/{total} tests passed ===\n")
    
    if passed == total:
        print("✅ OrderItemSerializer is working correctly!")
        print("\nFixed issues:")
        print("  • Old orders with 'airpods.jpg' now return '/images/airpods.jpg'")
        print("  • New orders with full URLs are preserved")
        print("  • Missing images fallback to '/placeholder.png'")
        print("  • Frontend will now load images correctly")
        print("\nThe order API will now return:")
        print("  image: '/images/airpods.jpg' instead of 'airpods.jpg'")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
