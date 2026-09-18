from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import os
import requests
from django.conf import settings
from dotenv import load_dotenv
from base.models import Product, Order, OrderItem, ShippingAddress
from django.db.models import Q
from django.contrib.auth.models import User
import re
from datetime import datetime
from decimal import Decimal

# Load environment variables
load_dotenv()

def search_products_in_database(query, limit=10):
    """Search products in the actual database with intelligent matching"""
    try:
        print(f"Searching database for: '{query}'")
        
        # Split camelCase boundaries first (e.g. "samsungS23" -> "samsung S23")
        spaced_query = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', query)
        
        # Clean and prepare search terms
        raw_terms = re.findall(r'[a-zA-Z]+\d+|[a-zA-Z]+|\d+', spaced_query.lower())
        
        # Remove common filler/stopwords that cause false matches
        stopwords = {
            'i', 'a', 'an', 'the', 'to', 'of', 'for', 'my', 'me', 'is', 'it',
            'want', 'need', 'buy', 'order', 'get', 'take', 'looking', 'like',
            'please', 'can', 'you', 'would', 'this', 'that', 'one', 'some',
            'and', 'or', 'in', 'on', 'with', 'have', 'has', 'do', 'does'
        }
        search_terms = [t for t in raw_terms if t not in stopwords and len(t) > 1]
        
        print(f"Search terms: {search_terms}")
        
        if not search_terms:
            return []
        
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
        products = all_products.filter(q_objects).filter(countInStock__gt=0).distinct()
        
        # Rank by number of matching terms (best matches first)
        scored_products = []
        for product in products:
            combined_text = f"{product.name} {product.brand} {product.category} {product.description or ''}".lower()
            score = sum(1 for term in search_terms if term in combined_text)
            scored_products.append((score, product))
        
        scored_products.sort(key=lambda x: x[0], reverse=True)
        top_products = [p for score, p in scored_products[:limit]]
        
        print(f"Found {len(top_products)} products matching query")
        
        # Format results
        results = []
        for product in top_products:
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
                'image': product.image.url if product.image else '/placeholder.png'
            }
            results.append(product_data)
            print(f"Added product: {product_data['name']} - ${product_data['price']}")
        
        return results
    except Exception as e:
        print(f"Error searching products: {e}")
        return []
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
                'image': product.image.url if product.image else '/placeholder.png'
            }
            results.append(product_data)
            print(f"Added product: {product_data['name']} - ${product_data['price']}")
        
        return results
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

def extract_quantity_from_message(message):
    """Extract quantity from user message"""
    message_lower = message.lower()
    
    # Convert word numbers to digits
    word_to_number = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
    }
    
    for word, num in word_to_number.items():
        if word in message_lower:
            message_lower = message_lower.replace(word, str(num))
    
    # Don't extract quantity if it's part of a product name (like iPhone 11)
    product_patterns = ['iphone 11', 'iphone 12', 'iphone 13', 'galaxy s23', 'galaxy s24', 'ps4', 'ps5']
    for pattern in product_patterns:
        if pattern in message_lower:
            # Check for explicit quantity mentions
            if 'quantity' in message_lower or 'qty' in message_lower:
                numbers = re.findall(r'(\d+)\s*(?:quantity|qty)', message_lower)
                if numbers:
                    return int(numbers[0])
            # Check for "I want X of them" pattern
            if 'of them' in message_lower or 'of these' in message_lower:
                numbers = re.findall(r'(\d+)\s*(?:of them|of these)', message_lower)
                if numbers:
                    return int(numbers[0])
            # Default to 1 for product names
            return 1
    
    # Look for explicit quantity mentions
    if 'quantity' in message_lower or 'qty' in message_lower:
        numbers = re.findall(r'(\d+)\s*(?:quantity|qty)', message_lower)
        if numbers:
            return int(numbers[0])
    
    # Look for "I want X" or "I need X" pattern
    quantity_patterns = [
        r'(?:want|need|buy|order|get)\s+(\d+)',
        r'(\d+)\s+(?:of them|of these|units|pieces)',
        r'(\d+)\s+(?:iphone|samsung|phone|camera)'
    ]
    
    for pattern in quantity_patterns:
        match = re.search(pattern, message_lower)
        if match:
            return int(match.group(1))
    
    # Default quantity
    return 1

def extract_product_from_message(message, products):
    """Extract which product the user wants to order with better matching"""
    message_lower = message.lower()
    
    # Try to match by exact product name first
    for product in products:
        product_name_lower = product['name'].lower()
        if product_name_lower in message_lower:
            return product
    
    # Try to match by brand + model number (like "iPhone 11", "Samsung S23")
    for product in products:
        brand_lower = product['brand'].lower()
        product_name_lower = product['name'].lower()
        
        # Check if brand is mentioned and model number matches
        if brand_lower in message_lower:
            # Extract model numbers from message (like 11, s23, s24, a13, etc.)
            model_patterns = re.findall(r'\b(\d+|[a-z]\d+)\b', message_lower)
            for model in model_patterns:
                if model in product_name_lower:
                    return product
            
            # Check for specific product type keywords
            product_types = ['phone', 'camera', 'headphone', 'mouse', 'console', 'game', 'galaxy', 'iphone', 'airpods']
            for ptype in product_types:
                if ptype in message_lower and ptype in product_name_lower:
                    return product
    
    # Special handling for iPhone 11
    if 'iphone' in message_lower and '11' in message_lower:
        for product in products:
            if 'iphone' in product['name'].lower() and '11' in product['name'].lower():
                return product
    
    # Special handling for Samsung Galaxy models
    if 'samsung' in message_lower and ('galaxy' in message_lower or 's23' in message_lower or 'a13' in message_lower):
        for product in products:
            if 'samsung' in product['name'].lower() and ('galaxy' in product['name'].lower() or 's23' in product['name'].lower() or 'a13' in product['name'].lower()):
                return product
    
    # If multiple products match the brand, return the first one for confirmation
    brand_matches = []
    for product in products:
        brand_lower = product['brand'].lower()
        if brand_lower in message_lower:
            brand_matches.append(product)
    
    if brand_matches:
        return brand_matches[0]  # Return first match for confirmation
    
    return None

def extract_address_from_message(message):
    """Extract shipping address information from user message"""
    address_info = {}
    
    # Common patterns for address extraction
    patterns = {
        'address': [
            r'address[:\s]+([^,\n]+)',
            r'street[:\s]+([^,\n]+)',
            r'location[:\s]+([^,\n]+)',
            r'live at[:\s]+([^,\n]+)',
            r'my address is[:\s]+([^,\n]+)'
        ],
        'city': [
            r'city[:\s]+([^,\n]+)',
            r'in[:\s]+([^,\n]+)',
            r'from[:\s]+([^,\n]+)'
        ],
        'postalCode': [
            r'postal[:\s]+([^,\n]+)',
            r'zip[:\s]+([^,\n]+)',
            r'post code[:\s]+([^,\n]+)',
            r'pincode[:\s]+([^,\n]+)'
        ],
        'country': [
            r'country[:\s]+([^,\n]+)',
            r'state[:\s]+([^,\n]+)',
            r'province[:\s]+([^,\n]+)'
        ]
    }
    
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                address_info[field] = match.group(1).strip()
                break
    
    return address_info

def is_address_collection_message(message):
    """Check if message contains address information"""
    address_keywords = [
        'address', 'street', 'city', 'postal', 'zip', 'country', 'state',
        'location', 'live at', 'my address', 'shipping to', 'deliver to'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in address_keywords)

def create_order_via_ai(user, product_data, quantity, shipping_info):
    """Create an order through AI chatbot with required shipping address"""
    try:
        # Validate shipping info
        required_fields = ['address', 'city', 'postalCode', 'country']
        missing_fields = [field for field in required_fields if not shipping_info.get(field)]
        
        if missing_fields:
            return {
                'success': False,
                'error': f'Missing required shipping information: {", ".join(missing_fields)}',
                'needs_address': True,
                'missing_fields': missing_fields
            }
        
        # Get the product from database
        product = Product.objects.get(_id=product_data['id'])
        
        # Check stock availability
        if product.countInStock < quantity:
            return {
                'success': False,
                'error': f'Sorry, we only have {product.countInStock} units of {product.name} in stock.'
            }
        
        # Calculate prices
        item_price = float(product.price) if product.price else 0.0
        subtotal = item_price * quantity
        tax_price = subtotal * 0.1  # 10% tax
        shipping_price = 10.0  # Fixed shipping
        total_price = subtotal + tax_price + shipping_price
        
        # Create order
        order = Order.objects.create(
            user=user,
            paymentMethod='AI Order',  # Special payment method for AI orders
            taxPrice=Decimal(str(tax_price)),
            shippingPrice=Decimal(str(shipping_price)),
            totalPrice=Decimal(str(total_price))
        )
        
        # Create shipping address with provided info
        ShippingAddress.objects.create(
            order=order,
            address=shipping_info['address'],
            city=shipping_info['city'],
            postalCode=shipping_info['postalCode'],
            country=shipping_info['country'],
            shippingPrice=Decimal(str(shipping_price))
        )
        
        # Create order item
        order_item = OrderItem.objects.create(
            product=product,
            order=order,
            name=product.name,
            qty=quantity,
            price=Decimal(str(item_price)),
            image=product.image.url if product.image else '/placeholder.png',
        )
        
        # Update stock
        product.countInStock -= quantity
        product.save()
        
        return {
            'success': True,
            'order_id': order._id,
            'order': {
                'id': order._id,
                'total': float(total_price),
                'items': [{
                    'name': product.name,
                    'quantity': quantity,
                    'price': item_price
                }],
                'status': 'Pending',
                'created_at': order.createdAt.strftime('%Y-%m-%d %H:%M:%S'),
                'shipping_address': {
                    'address': shipping_info['address'],
                    'city': shipping_info['city'],
                    'postalCode': shipping_info['postalCode'],
                    'country': shipping_info['country']
                }
            }
        }
        
    except Exception as e:
        print(f"Error creating order: {e}")
        return {
            'success': False,
            'error': f'Failed to create order: {str(e)}'
        }

def get_user_orders(user):
    """Get user's recent orders"""
    try:
        orders = Order.objects.filter(user=user).order_by('-createdAt')[:5]
        order_data = []
        
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            items = []
            for item in order_items:
                items.append({
                    'name': item.name,
                    'quantity': item.qty,
                    'price': float(item.price)
                })
            
            order_data.append({
                'id': order._id,
                'total': float(order.totalPrice) if order.totalPrice else 0,
                'status': 'Paid' if order.isPaid else 'Pending',
                'delivered': order.isDelivered,
                'items': items,
                'created_at': order.createdAt.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return order_data
    except Exception as e:
        print(f"Error getting user orders: {e}")
        return []

def analyze_ordering_intent(message):
    """Analyze if user wants to place an order"""
    message_lower = message.lower()
    
    # Order-related keywords
    order_keywords = [
        'buy', 'purchase', 'order', 'add to cart', 'get', 'take', 'want',
        'need', 'looking for', 'interested in', 'i want', 'i need',
        'place order', 'checkout', 'pay', 'purchase now'
    ]
    
    # Quantity keywords
    quantity_keywords = ['one', 'two', 'three', 'four', 'five', '1', '2', '3', '4', '5']
    
    # Confirmation keywords
    confirm_keywords = ['yes', 'confirm', 'proceed', 'ok', 'sure', 'go ahead']
    
    return {
        'wants_to_order': any(keyword in message_lower for keyword in order_keywords),
        'has_quantity': any(keyword in message_lower for keyword in quantity_keywords),
        'is_confirmation': any(keyword in message_lower for keyword in confirm_keywords),
        'is_order_status_query': any(keyword in message_lower for keyword in ['status', 'track', 'where is', 'delivery', 'shipped'])
    }

def get_gemini_response_with_ordering(message, products, intent, order_result=None, user_orders=None):
    """Get response from Gemini with ordering context"""
    try:
        api_key = "AIzaSyCf-MMEzrCINC9v9-IGuZg4elpd0Yrh1iI"
        
        if not api_key:
            return "I'm sorry, the chatbot service is not configured."
        
        # Create context based on intent
        context = f"""You are a helpful ecommerce assistant for Digital Edge electronics store. 
        
        Customer query: "{message}"
        
        Intent analysis: {json.dumps(intent, indent=2)}
        
        Available products: {json.dumps(products, indent=2)}
        
        """
        
        if order_result:
            context += f"Order result: {json.dumps(order_result, indent=2)}\n"
        
        if user_orders:
            context += f"User's recent orders: {json.dumps(user_orders, indent=2)}\n"
        
        context += """
        Instructions:
        1. If user wants to order a product, help them place the order
        2. If they ask about order status, provide their recent orders
        3. Be helpful and guide them through the ordering process
        4. Always ask for confirmation before placing orders
        5. Be friendly and professional
        6. If they want to order, ask for quantity and confirm the product
        """
        
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
                return "I'm sorry, I couldn't generate a response. Please try again."
        else:
            print(f"Gemini API error: {response.status_code}")
            return "I'm sorry, I'm having trouble connecting to the AI service. Please try again later."
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "I'm sorry, I encountered an error. Please try again."

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat_with_ordering(request):
    """AI chatbot with ordering functionality and address collection"""
    print(f"AI ordering chatbot called with message: {request.data.get('message', '')}")
    
    try:
        data = request.data
        message = data.get('message', '')
        chat_history = data.get('chat_history', [])
        pending_order = data.get('pending_order', None)  # Store pending order info
        user = request.user
        
        if not message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Analyze user intent
        intent = analyze_ordering_intent(message)
        print(f"Detected intent: {intent}")
        
        # Initialize variables for all paths
        order_result = None
        user_orders = None
        response_content = None
        
        # Check if this is confirmation, product selection, or address collection
        if pending_order:
            if pending_order.get('waiting_for_selection'):
                # User is selecting from multiple products
                available_products = pending_order['available_products']
                message_lower = message.lower()
                
                # Check for selection by number ONLY
                selected_product = None
                if 'first' in message_lower or '1' == message_lower.strip():
                    selected_product = available_products[0]
                elif 'second' in message_lower or '2' == message_lower.strip():
                    selected_product = available_products[1] if len(available_products) > 1 else None
                elif 'third' in message_lower or '3' == message_lower.strip():
                    selected_product = available_products[2] if len(available_products) > 2 else None
                
                if selected_product:
                    quantity = extract_quantity_from_message(message)
                    response_content = f"Perfect! You selected {selected_product['name']} for ${selected_product['price']:.2f}.\n\n"
                    response_content += f"You want {quantity} of them.\n"
                    response_content += f"Total: ${selected_product['price'] * quantity:.2f} (plus tax and shipping)\n\n"
                    response_content += f"Does this look correct? Say 'Yes' to confirm or specify quantity like 'I want 2'."
                    
                    # Update pending order with selected product
                    pending_order = {
                        'product': selected_product,
                        'quantity': quantity,
                        'waiting_for_confirmation': True
                    }
                else:
                    response_content = f"Please select a product by number:\n\n"
                    for i, prod in enumerate(available_products, 1):
                        response_content += f"{i}. {prod['name']} - ${prod['price']:.2f}\n"
                    response_content += f"\nJust say '1' for first one, '2' for second one, etc."
            
            elif pending_order.get('waiting_for_confirmation'):
                # Check if user confirmed the order
                confirmation_keywords = ['yes', 'confirm', 'proceed', 'ok', 'sure', 'go ahead', 'order this', 'want to order', 'i wanna order', 'i want to order', 'quantity']
                message_lower = message.lower()
                
                if any(keyword in message_lower for keyword in confirmation_keywords):
                    # User confirmed, ask for address
                    response_content = f"Excellent! I'll prepare your order for {pending_order['product']['name']} (Qty: {pending_order['quantity']}).\n\nTo complete your order, I need your shipping address. Please provide:\n• Address\n• City\n• Postal Code\n• Country\n\nFor example: 'My address is 123 Main St, city is New York, postal code is 10001, country is USA'"
                    
                    # Update pending order to wait for address
                    pending_order['waiting_for_confirmation'] = False
                else:
                    # Check if user is asking for quantity change
                    quantity = extract_quantity_from_message(message)
                    if quantity != 1:  # User specified a different quantity
                        pending_order['quantity'] = quantity
                        response_content = f"Got it! You want {quantity} of {pending_order['product']['name']}.\n\n"
                        response_content += f"**Updated Total: ${pending_order['product']['price'] * quantity:.2f}** (plus tax and shipping)\n\n"
                        response_content += f"Does this look correct? Please confirm by saying 'Yes' or 'Confirm order'."
                    else:
                        # Check if user is trying to change quantity but didn't specify properly
                        message_lower = message.lower()
                        if any(word in message_lower for word in ['quantity', 'qty', 'change', 'update', 'modify']):
                            response_content = f"Please specify the quantity you want. For example: 'I want 2' or '2 quantity'"
                        else:
                            # User didn't confirm, ask again
                            response_content = f"Please confirm if you want to order {pending_order['product']['name']} for ${pending_order['product']['price']:.2f}.\n\nSay 'Yes' or 'Confirm' to proceed."
            
            elif is_address_collection_message(message):
                # Extract address from message
                address_info = extract_address_from_message(message)
                
                # Try to create order with address
                order_result = create_order_via_ai(
                    user, 
                    pending_order['product'], 
                    pending_order['quantity'], 
                    address_info
                )
                
                if order_result['success']:
                    # Order created successfully
                    response_content = f"🎉 Order created successfully!\n\nOrder ID: #{order_result['order_id']}\nTotal: ${order_result['order']['total']:.2f}\n\nShipping to:\n{address_info.get('address', 'N/A')}\n{address_info.get('city', 'N/A')}, {address_info.get('postalCode', 'N/A')}\n{address_info.get('country', 'N/A')}\n\nThank you for your order! Is there anything else I can help you with?"
                    pending_order = None
                else:
                    if order_result.get('needs_address'):
                        missing_fields = order_result.get('missing_fields', [])
                        response_content = f"I need more shipping information to complete your order. Please provide:\n\n"
                        for field in missing_fields:
                            field_name = field.replace('postalCode', 'Postal Code').title()
                            response_content += f"• {field_name}\n"
                        response_content += f"\nFor example: 'My address is 123 Main St, city is New York, postal code is 10001, country is USA'"
                    else:
                        response_content = f"Sorry, I couldn't create your order: {order_result['error']}"
        else:
            # Normal conversation flow
            products = search_products_in_database(message, limit=5)
            print(f"Found {len(products)} products")
            
            # Handle different intents
            if intent['wants_to_order'] and products:
                # User wants to order something
                product = extract_product_from_message(message, products)
                quantity = extract_quantity_from_message(message)
                
                if product:
                    # Show product details and ask for confirmation
                    response_content = f"Perfect! I found {product['name']} for ${product['price']:.2f}.\n\n"
                    response_content += f"You want {quantity} of them.\n"
                    response_content += f"Total: ${product['price'] * quantity:.2f} (plus tax and shipping)\n\n"
                    response_content += f"Does this look correct? Say 'Yes' to confirm or specify quantity like 'I want 2'."
                    
                    # Store pending order info for confirmation
                    pending_order = {
                        'product': product,
                        'quantity': quantity,
                        'waiting_for_confirmation': True
                    }
                else:
                    # Filter products by category and brand
                    message_lower = message.lower()
                    
                    # Category keywords
                    category_filters = {
                        'phone': ['phone', 'iphone', 'samsung', 'galaxy', 'mobile'],
                        'camera': ['camera', 'dslr', 'canon', 'cannon', 'photography'],
                        'headphone': ['headphone', 'airpods', 'earphone', 'bluetooth', 'audio'],
                        'gaming': ['gaming', 'mouse', 'playstation', 'ps4', 'ps5', 'controller', 'game'],
                        'accessories': ['case', 'cover', 'charger', 'cable', 'adapter']
                    }
                    
                    # Find relevant category
                    relevant_category = None
                    for category, keywords in category_filters.items():
                        if any(keyword in message_lower for keyword in keywords):
                            relevant_category = category
                            break
                    
                    # Filter products by category
                    if relevant_category:
                        filtered_products = []
                        for product in products:
                            product_name_lower = product['name'].lower()
                            # Check if product matches the category
                            if relevant_category == 'phone' and any(k in product_name_lower for k in ['phone', 'iphone', 'samsung', 'galaxy']):
                                filtered_products.append(product)
                            elif relevant_category == 'camera' and any(k in product_name_lower for k in ['camera', 'dslr', 'canon']):
                                filtered_products.append(product)
                            elif relevant_category == 'headphone' and any(k in product_name_lower for k in ['headphone', 'airpods', 'bluetooth', 'audio']):
                                filtered_products.append(product)
                            elif relevant_category == 'gaming' and any(k in product_name_lower for k in ['gaming', 'mouse', 'playstation', 'game']):
                                filtered_products.append(product)
                            elif relevant_category == 'accessories' and any(k in product_name_lower for k in ['case', 'cover', 'charger']):
                                filtered_products.append(product)
                        
                        if filtered_products:
                            products = filtered_products
                    
                    # Check for specific brands mentioned
                    brand_keywords = {
                        'Apple': ['iphone', 'apple', 'airpods'],
                        'Samsung': ['samsung', 'galaxy'],
                        'Sony': ['sony', 'playstation'],
                        'Cannon': ['canon', 'cannon'],
                        'Logitech': ['logitech']
                    }
                    
                    for brand, keywords in brand_keywords.items():
                        if any(keyword in message_lower for keyword in keywords):
                            brand_products = [p for p in products if p['brand'].lower() == brand.lower()]
                            if brand_products:
                                products = brand_products
                                break
                    
                    # Show all matching products for user to choose
                    response_content = f"I found {len(products)} products:\n\n"
                    for i, prod in enumerate(products[:3], 1):  # Show max 3 products
                        response_content += f"{i}. {prod['name']} - ${prod['price']:.2f}\n"
                    
                    response_content += f"\nSelect by number: '1', '2', or '3'"
                    
                    # Store products for selection
                    pending_order = {
                        'available_products': products[:3],
                        'waiting_for_selection': True
                    }
            elif intent['is_order_status_query']:
                # User wants to check order status
                user_orders = get_user_orders(user)
                print(f"User orders: {user_orders}")
                response_content = get_gemini_response_with_ordering(
                    message, products, intent, None, user_orders
                )
            else:
                # General conversation
                response_content = get_gemini_response_with_ordering(
                    message, products, intent, None, None
                )
        
        # Ensure response_content is not None
        if response_content is None:
            response_content = "I'm sorry, I didn't quite understand that. Could you please rephrase your question or tell me what you're looking for?"
        
        # Update chat history
        updated_history = chat_history.copy()
        updated_history.append({"role": "user", "content": message})
        updated_history.append({"role": "assistant", "content": response_content})
        
        return Response({
            'response': response_content,
            'chat_history': updated_history,
            'products_found': len(products) if 'products' in locals() else 0,
            'intent_analysis': intent,
            'order_created': order_result.get('success', False) if order_result else False,
            'order_data': order_result if order_result and order_result.get('success') else None,
            'user_orders': user_orders if user_orders else None,
            'pending_order': pending_order,
            'needs_address': pending_order is not None and not pending_order.get('waiting_for_confirmation') and not pending_order.get('waiting_for_selection')
        })
        
    except Exception as e:
        print(f"Error in AI ordering chatbot: {str(e)}")
        return Response(
            {'error': 'An error occurred while processing your message'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def ai_chat_guest(request):
    """AI chatbot for guests (no ordering)"""
    print(f"AI guest chatbot called with message: {request.data.get('message', '')}")
    
    try:
        data = request.data
        message = data.get('message', '')
        chat_history = data.get('chat_history', [])
        
        if not message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Search for products
        products = search_products_in_database(message, limit=5)
        
        # Get AI response (without ordering functionality)
        response_content = get_gemini_response_with_ordering(message, products, {}, None, None)
        
        # Update chat history
        updated_history = chat_history.copy()
        updated_history.append({"role": "user", "content": message})
        updated_history.append({"role": "assistant", "content": response_content})
        
        return Response({
            'response': response_content,
            'chat_history': updated_history,
            'products_found': len(products),
            'requires_login': True
        })
        
    except Exception as e:
        print(f"Error in AI guest chatbot: {str(e)}")
        return Response(
            {'error': 'An error occurred while processing your message'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_orders_ai(request):
    """Get user's orders for AI chatbot"""
    try:
        user = request.user
        orders = get_user_orders(user)
        
        return Response({
            'orders': orders,
            'total_orders': len(orders)
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
