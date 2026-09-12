from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json
import os
import requests
from django.conf import settings
from dotenv import load_dotenv
from base.models import Product, Order, OrderItem
from django.db.models import Q
import re

# Load environment variables
load_dotenv()

def search_products_in_database(query, limit=10):
    """Search products in the actual database with intelligent matching"""
    try:
        print(f"Searching database for: '{query}'")
        
        # Clean and prepare search terms
        search_terms = re.findall(r'\b\w+\b', query.lower())
        print(f"Search terms: {search_terms}")
        
        # Get all products from database
        all_products = Product.objects.all()
        print(f"Total products in database: {all_products.count()}")
        
        # Build search query
        q_objects = Q()
        for term in search_terms:
            q_objects |= (
                Q(name__icontains=term) |
                Q(brand__icontains=term) |
                Q(category__icontains=term) |
                Q(description__icontains=term)
            )
        
        # Search with stock filter
        products = all_products.filter(q_objects).filter(countInStock__gt=0)[:limit]
        print(f"Found {products.count()} products matching query")
        
        # Format results
        results = []
        for product in products:
            product_data = {
                'id': product._id,
                'name': product.name or 'Unknown Product',
                'brand': product.brand or 'Unknown Brand',
                'category': product.category or 'Electronics',
                'price': float(product.price) if product.price else 0.0,
                'rating': float(product.rating) if product.rating else 0.0,
                'numReviews': product.numReviews or 0,
                'description': (product.description[:150] + '...') if product.description and len(product.description) > 150 else (product.description or 'No description available'),
                'in_stock': product.countInStock > 0,
                'stock_count': product.countInStock or 0,
                'image': str(product.image) if product.image else '/placeholder.png'
            }
            results.append(product_data)
            print(f"Added product: {product_data['name']} - ${product_data['price']}")
        
        return results
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

def get_all_available_products(limit=20):
    """Get all available products from database"""
    try:
        products = Product.objects.filter(countInStock__gt=0)[:limit]
        results = []
        for product in products:
            results.append({
                'id': product._id,
                'name': product.name or 'Unknown Product',
                'brand': product.brand or 'Unknown Brand',
                'category': product.category or 'Electronics',
                'price': float(product.price) if product.price else 0.0,
                'rating': float(product.rating) if product.rating else 0.0,
                'numReviews': product.numReviews or 0,
                'description': (product.description[:150] + '...') if product.description and len(product.description) > 150 else (product.description or 'No description available'),
                'in_stock': product.countInStock > 0,
                'stock_count': product.countInStock or 0
            })
        return results
    except Exception as e:
        print(f"Error getting all products: {e}")
        return []

def get_products_by_brand_from_db(brand_name, limit=10):
    """Get products by specific brand from database"""
    try:
        products = Product.objects.filter(
            brand__icontains=brand_name,
            countInStock__gt=0
        )[:limit]
        
        results = []
        for product in products:
            results.append({
                'id': product._id,
                'name': product.name or 'Unknown Product',
                'brand': product.brand or 'Unknown Brand',
                'category': product.category or 'Electronics',
                'price': float(product.price) if product.price else 0.0,
                'rating': float(product.rating) if product.rating else 0.0,
                'numReviews': product.numReviews or 0,
                'description': (product.description[:150] + '...') if product.description and len(product.description) > 150 else (product.description or 'No description available'),
                'in_stock': product.countInStock > 0,
                'stock_count': product.countInStock or 0
            })
        return results
    except Exception as e:
        print(f"Error getting products by brand: {e}")
        return []

def analyze_user_intent(message):
    """Analyze user message to understand intent"""
    message_lower = message.lower()
    
    # Common brand names to look for
    brand_keywords = {
        'apple': ['apple', 'iphone', 'ipad', 'macbook', 'airpods', 'mac'],
        'samsung': ['samsung', 'galaxy'],
        'sony': ['sony', 'playstation', 'ps4', 'ps5'],
        'canon': ['canon', 'cannon', 'eos', 'dslr'],
        'logitech': ['logitech', 'g-series', 'gaming mouse'],
        'alexa': ['alexa', 'amazon', 'echo']
    }
    
    # Category keywords
    category_keywords = {
        'phones': ['phone', 'smartphone', 'mobile', 'cell'],
        'headphones': ['headphones', 'earphones', 'airpods', 'bluetooth'],
        'cameras': ['camera', 'dslr', 'photography'],
        'gaming': ['gaming', 'playstation', 'ps4', 'ps5', 'mouse', 'controller'],
        'electronics': ['electronics', 'gadgets', 'devices']
    }
    
    # Price-related keywords
    price_keywords = ['price', 'cost', 'expensive', 'cheap', 'budget', 'affordable', '$', 'dollar']
    
    # Stock-related keywords
    stock_keywords = ['stock', 'available', 'in stock', 'out of stock', 'quantity']
    
    detected_brands = []
    detected_categories = []
    
    # Detect brands
    for brand, keywords in brand_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            detected_brands.append(brand)
    
    # Detect categories
    for category, keywords in category_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            detected_categories.append(category)
    
    return {
        'brands': detected_brands,
        'categories': detected_categories,
        'price_related': any(keyword in message_lower for keyword in price_keywords),
        'stock_related': any(keyword in message_lower for keyword in stock_keywords),
        'is_general_query': not (detected_brands or detected_categories)
    }

def format_product_response(products, intent):
    """Format product data into a readable response"""
    if not products:
        return "I'm sorry, I couldn't find any products matching your request in our current inventory."
    
    response_parts = []
    
    if intent['brands']:
        response_parts.append(f"Here are the {intent['brands'][0].title()} products we have available:")
    elif intent['categories']:
        response_parts.append(f"Here are the {intent['categories'][0].title()} products we have available:")
    else:
        response_parts.append("Here are the products I found for you:")
    
    for i, product in enumerate(products[:5], 1):  # Limit to 5 products
        price_str = f"${product['price']:.2f}" if product['price'] > 0 else "Price not available"
        rating_str = f"⭐ {product['rating']:.1f}" if product['rating'] > 0 else "No ratings yet"
        stock_str = f"({product['stock_count']} in stock)" if product['stock_count'] > 0 else "(Out of stock)"
        
        product_info = f"{i}. **{product['name']}** by {product['brand']}\n"
        product_info += f"   💰 {price_str} | {rating_str} | {stock_str}\n"
        product_info += f"   📝 {product['description']}\n"
        
        response_parts.append(product_info)
    
    if len(products) > 5:
        response_parts.append(f"\n*And {len(products) - 5} more products available!*")
    
    response_parts.append("\nWould you like more details about any specific product, or can I help you with anything else?")
    
    return "\n".join(response_parts)

def get_gemini_response_with_products(message, products, intent):
    """Get response from Gemini with product context"""
    try:
        api_key = "AIzaSyCf-MMEzrCINC9v9-IGuZg4elpd0Yrh1iI"
        
        if not api_key:
            return format_product_response(products, intent)
        
        # Create context with product data
        context = f"""You are a helpful ecommerce assistant for Digital Edge electronics store. 
        
        You have access to real product data from our database. Here are the products that match the customer's query:

        {json.dumps(products, indent=2)}

        Customer query: "{message}"

        Instructions:
        1. Use the actual product data provided above
        2. Be specific about product names, prices, and availability
        3. If products are found, mention them by name and price
        4. If no products match, be honest about it
        5. Be helpful and suggest alternatives if possible
        6. Keep responses conversational and friendly
        7. Always ask if they need more help

        Respond naturally as if you're a knowledgeable sales assistant."""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": context}]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                return format_product_response(products, intent)
        else:
            print(f"Gemini API error: {response.status_code}")
            return format_product_response(products, intent)
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return format_product_response(products, intent)

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_with_bot(request):
    """Professional chatbot with real database integration"""
    print(f"Professional chatbot called with message: {request.data.get('message', '')}")
    
    try:
        data = request.data
        message = data.get('message', '')
        chat_history = data.get('chat_history', [])
        
        if not message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Analyze user intent
        intent = analyze_user_intent(message)
        print(f"Detected intent: {intent}")
        
        # Search for products based on intent
        products = []
        
        if intent['brands']:
            # Search by brand
            for brand in intent['brands']:
                brand_products = get_products_by_brand_from_db(brand, limit=5)
                products.extend(brand_products)
        else:
            # General search
            products = search_products_in_database(message, limit=10)
        
        # Remove duplicates
        seen_ids = set()
        unique_products = []
        for product in products:
            if product['id'] not in seen_ids:
                seen_ids.add(product['id'])
                unique_products.append(product)
        
        products = unique_products[:8]  # Limit to 8 products
        print(f"Found {len(products)} unique products")
        
        # Get response
        if products:
            response_content = get_gemini_response_with_products(message, products, intent)
        else:
            # If no products found, get all available products to suggest alternatives
            all_products = get_all_available_products(limit=5)
            if all_products:
                response_content = f"I couldn't find any products matching '{message}' in our current inventory. However, here are some popular items we have available:\n\n"
                response_content += format_product_response(all_products, intent)
            else:
                response_content = "I'm sorry, I couldn't find any products matching your request. Our inventory might be empty at the moment. Please check back later or contact our support team."
        
        # Update chat history
        updated_history = chat_history.copy()
        updated_history.append({"role": "user", "content": message})
        updated_history.append({"role": "assistant", "content": response_content})
        
        return Response({
            'response': response_content,
            'chat_history': updated_history,
            'products_found': len(products),
            'intent_analysis': intent
        })
        
    except Exception as e:
        print(f"Error in professional chat_with_bot: {str(e)}")
        return Response(
            {'error': 'An error occurred while processing your message'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def chatbot_status(request):
    """Check if chatbot service is available"""
    try:
        api_key = "AIzaSyCf-MMEzrCINC9v9-IGuZg4elpd0Yrh1iI"
        if api_key:
            return Response({'status': 'available'})
        else:
            return Response({'status': 'unavailable', 'error': 'API key not configured'})
    except Exception as e:
        return Response({'status': 'unavailable', 'error': str(e)})

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_products(request):
    """Debug endpoint to see what's in the database"""
    try:
        query = request.GET.get('q', '')
        
        if query:
            products = search_products_in_database(query, limit=10)
        else:
            products = get_all_available_products(limit=20)
        
        return Response({
            'query': query,
            'products': products,
            'total_found': len(products),
            'database_connection': 'OK'
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
