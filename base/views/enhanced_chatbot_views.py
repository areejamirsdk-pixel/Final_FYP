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

# Load environment variables
load_dotenv()

def search_products(query, limit=5):
    """Search products based on query"""
    try:
        # Create search query
        search_terms = query.lower().split()
        
        # Build Q objects for search
        q_objects = Q()
        for term in search_terms:
            q_objects |= (
                Q(name__icontains=term) |
                Q(brand__icontains=term) |
                Q(category__icontains=term) |
                Q(description__icontains=term)
            )
        
        # Search products
        products = Product.objects.filter(q_objects).filter(countInStock__gt=0)[:limit]
        
        # Format results
        results = []
        for product in products:
            results.append({
                'id': product._id,
                'name': product.name,
                'brand': product.brand,
                'category': product.category,
                'price': float(product.price) if product.price else 0,
                'rating': float(product.rating) if product.rating else 0,
                'numReviews': product.numReviews or 0,
                'description': product.description[:200] + '...' if product.description and len(product.description) > 200 else product.description,
                'in_stock': product.countInStock > 0,
                'stock_count': product.countInStock
            })
        
        return results
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

def get_products_by_brand(brand, limit=5):
    """Get products by specific brand"""
    try:
        products = Product.objects.filter(
            brand__icontains=brand,
            countInStock__gt=0
        )[:limit]
        
        results = []
        for product in products:
            results.append({
                'id': product._id,
                'name': product.name,
                'brand': product.brand,
                'category': product.category,
                'price': float(product.price) if product.price else 0,
                'rating': float(product.rating) if product.rating else 0,
                'numReviews': product.numReviews or 0,
                'description': product.description[:200] + '...' if product.description and len(product.description) > 200 else product.description,
                'in_stock': product.countInStock > 0,
                'stock_count': product.countInStock
            })
        
        return results
    except Exception as e:
        print(f"Error getting products by brand: {e}")
        return []

def get_products_by_category(category, limit=5):
    """Get products by category"""
    try:
        products = Product.objects.filter(
            category__icontains=category,
            countInStock__gt=0
        )[:limit]
        
        results = []
        for product in products:
            results.append({
                'id': product._id,
                'name': product.name,
                'brand': product.brand,
                'category': product.category,
                'price': float(product.price) if product.price else 0,
                'rating': float(product.rating) if product.rating else 0,
                'numReviews': product.numReviews or 0,
                'description': product.description[:200] + '...' if product.description and len(product.description) > 200 else product.description,
                'in_stock': product.countInStock > 0,
                'stock_count': product.countInStock
            })
        
        return results
    except Exception as e:
        print(f"Error getting products by category: {e}")
        return []

def get_available_brands():
    """Get list of available brands"""
    try:
        brands = Product.objects.filter(countInStock__gt=0).values_list('brand', flat=True).distinct()
        return [brand for brand in brands if brand]
    except Exception as e:
        print(f"Error getting brands: {e}")
        return []

def get_available_categories():
    """Get list of available categories"""
    try:
        categories = Product.objects.filter(countInStock__gt=0).values_list('category', flat=True).distinct()
        return [category for category in categories if category]
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []

def analyze_query(message):
    """Analyze user query to determine intent"""
    message_lower = message.lower()
    
    # Check for brand queries
    brands = get_available_brands()
    mentioned_brands = [brand for brand in brands if brand.lower() in message_lower]
    
    # Check for category queries
    categories = get_available_categories()
    mentioned_categories = [cat for cat in categories if cat.lower() in message_lower]
    
    # Check for price-related queries
    price_related = any(word in message_lower for word in ['price', 'cost', 'expensive', 'cheap', 'budget', '$', 'dollar'])
    
    # Check for stock queries
    stock_related = any(word in message_lower for word in ['stock', 'available', 'in stock', 'out of stock'])
    
    return {
        'brands': mentioned_brands,
        'categories': mentioned_categories,
        'price_related': price_related,
        'stock_related': stock_related,
        'is_general_query': not (mentioned_brands or mentioned_categories or price_related or stock_related)
    }

def get_gemini_response_with_context(message, product_data=None, analysis=None):
    """Get response from Gemini API with product context"""
    try:
        api_key = "AIzaSyCf-MMEzrCINC9v9-IGuZg4elpd0Yrh1iI"
        
        if not api_key:
            return "I'm sorry, the chatbot service is not configured. Please add your Gemini API key."
        
        # Prepare context
        context = """You are a helpful ecommerce assistant for Digital Edge, an online electronics store. 
        You have access to real product data from our database. When customers ask about products, provide specific information including:
        - Product names, brands, and prices
        - Stock availability
        - Ratings and reviews
        - Brief descriptions
        
        Be specific and helpful. If you have product data, use it to give detailed answers.
        If you don't have specific product data, be honest about it.
        Always be friendly and professional."""
        
        # Add product data to context if available
        if product_data:
            context += f"\n\nCurrent product data from our database:\n{json.dumps(product_data, indent=2)}"
        
        # Add analysis context
        if analysis:
            context += f"\n\nQuery analysis: {json.dumps(analysis, indent=2)}"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": f"{context}\n\nCustomer question: {message}"}]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                return "I'm sorry, I couldn't generate a response. Please try again."
        else:
            print(f"Gemini API error: {response.status_code} - {response.text}")
            return "I'm sorry, I'm having trouble connecting to the AI service. Please try again later."
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "I'm sorry, I encountered an error. Please try again."

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_with_bot(request):
    """Enhanced chatbot with database integration"""
    print("Enhanced chatbot view is calling")
    
    try:
        data = request.data
        message = data.get('message', '')
        chat_history = data.get('chat_history', [])
        
        if not message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Analyze the query
        analysis = analyze_query(message)
        print(f"Query analysis: {analysis}")
        
        # Get relevant product data based on query
        product_data = []
        
        if analysis['brands']:
            # Search by mentioned brands
            for brand in analysis['brands']:
                products = get_products_by_brand(brand, limit=3)
                product_data.extend(products)
        elif analysis['categories']:
            # Search by mentioned categories
            for category in analysis['categories']:
                products = get_products_by_category(category, limit=3)
                product_data.extend(products)
        else:
            # General search
            products = search_products(message, limit=5)
            product_data.extend(products)
        
        # Remove duplicates based on product ID
        seen_ids = set()
        unique_products = []
        for product in product_data:
            if product['id'] not in seen_ids:
                seen_ids.add(product['id'])
                unique_products.append(product)
        
        product_data = unique_products[:5]  # Limit to 5 products
        
        print(f"Found {len(product_data)} products")
        
        # Get response from Gemini with product context
        response_content = get_gemini_response_with_context(message, product_data, analysis)
        
        # Update chat history
        updated_history = chat_history.copy()
        updated_history.append({"role": "user", "content": message})
        updated_history.append({"role": "assistant", "content": response_content})
        
        return Response({
            'response': response_content,
            'chat_history': updated_history,
            'products_found': len(product_data),
            'query_analysis': analysis
        })
        
    except Exception as e:
        print(f"Error in enhanced chat_with_bot: {str(e)}")
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
def get_products_info(request):
    """Get products information for debugging"""
    try:
        query = request.GET.get('q', '')
        if query:
            products = search_products(query, limit=10)
        else:
            products = []
            for product in Product.objects.filter(countInStock__gt=0)[:10]:
                products.append({
                    'id': product._id,
                    'name': product.name,
                    'brand': product.brand,
                    'category': product.category,
                    'price': float(product.price) if product.price else 0,
                    'rating': float(product.rating) if product.rating else 0,
                    'in_stock': product.countInStock > 0
                })
        
        return Response({
            'products': products,
            'total_found': len(products),
            'brands': get_available_brands(),
            'categories': get_available_categories()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)