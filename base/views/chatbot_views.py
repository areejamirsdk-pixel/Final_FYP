from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import os
import sys
from django.conf import settings
from base.models import Product, Order, OrderItem
from base.serializers import ProductSerializer

# Chatbot configuration imports
try:
    from base.setup_config import google_gemini_config, get_gemini_config
except ImportError:
    chatbot_path = os.path.join(settings.BASE_DIR.parent, 'chatbot')
    if chatbot_path not in sys.path:
        sys.path.append(chatbot_path)
    try:
        from setup_config import google_gemini_config
        get_gemini_config = lambda: google_gemini_config
    except ImportError:
        google_gemini_config = None
        get_gemini_config = lambda: None

try:
    from agents import Agent, Runner, RunConfig
except ImportError as e:
    print(f"Error importing chatbot agent modules: {e}")
    Agent, Runner, RunConfig = None, None, None

# Global agent instance
chatbot_agent = None

def get_chatbot_agent():
    """Initialize and return the chatbot agent"""
    global chatbot_agent
    config = google_gemini_config or (get_gemini_config() if callable(get_gemini_config) else None)
    if chatbot_agent is None and config and Agent:
        try:
            chatbot_agent = Agent(
                name="Digital Edge Ecommerce Assistant",
                instructions="""
You are a helpful ecommerce assistant for Digital Edge, an online electronics store. Your role is to:

1. Help customers find products they're looking for
2. Provide product information, specifications, and recommendations
3. Assist with order inquiries, shipping, and returns
4. Answer questions about our store policies and services
5. Help with account and payment issues
6. Provide general customer support

Guidelines:
- Be friendly, professional, and helpful
- If you don't know specific product details, ask the customer to check the product page
- For order-specific questions, direct them to check their order history or contact support
- Always be encouraging about our products and services
- If asked about products not in our catalog, politely explain we focus on electronics
- Keep responses concise but informative
- Use a conversational, helpful tone

Our store specializes in:
- Electronics and gadgets
- Mobile phones and accessories
- Gaming equipment
- Audio devices
- Computer peripherals

Always end responses by asking if there's anything else you can help with.
""",
            )
        except Exception as e:
            print(f"Error creating chatbot agent: {e}")
            return None
    return chatbot_agent

def get_product_context():
    """Get product data for chatbot context"""
    try:
        products = Product.objects.all()[:10]  # Get first 10 products
        product_data = []
        for product in products:
            product_data.append({
                'name': product.name,
                'brand': product.brand,
                'category': product.category,
                'price': float(product.price) if product.price else 0,
                'rating': float(product.rating) if product.rating else 0,
                'description': product.description[:200] + '...' if product.description and len(product.description) > 200 else product.description,
                'in_stock': product.countInStock > 0
            })
        return product_data
    except Exception as e:
        print(f"Error getting product context: {e}")
        return []

def get_user_context(user):
    """Get user-specific context for chatbot"""
    if not user or not user.is_authenticated:
        return {}
    
    try:
        recent_orders = Order.objects.filter(user=user).order_by('-createdAt')[:3]
        order_data = []
        for order in recent_orders:
            order_items = OrderItem.objects.filter(order=order)
            items = [{'name': item.name, 'qty': item.qty, 'price': float(item.price)} for item in order_items]
            order_data.append({
                'id': order._id,
                'total': float(order.totalPrice) if order.totalPrice else 0,
                'status': 'Paid' if order.isPaid else 'Pending',
                'items': items,
                'date': order.createdAt.strftime('%Y-%m-%d')
            })
        
        return {
            'user_name': user.first_name or user.username,
            'recent_orders': order_data
        }
    except Exception as e:
        print(f"Error getting user context: {e}")
        return {}

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_with_bot(request):
    """Handle chatbot messages"""
    try:
        data = request.data
        message = data.get('message', '')
        chat_history = data.get('chat_history', [])
        
        if not message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the chatbot agent
        agent = get_chatbot_agent()
        if not agent or not google_gemini_config:
            return Response(
                {'error': 'Chatbot service is currently unavailable'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Get context data
        product_context = get_product_context()
        user_context = get_user_context(request.user) if hasattr(request, 'user') else {}
        
        # Create context message
        context_message = ""
        if product_context:
            context_message += f"Current products in store: {json.dumps(product_context, indent=2)}\n\n"
        if user_context:
            context_message += f"User information: {json.dumps(user_context, indent=2)}\n\n"
        
        # Add context and user message to history
        if context_message and len(chat_history) == 0:
            chat_history.append({"role": "system", "content": context_message})
        
        chat_history.append({"role": "user", "content": message})
        
        # Get response from agent using async runner
        import asyncio
        
        async def get_agent_response():
            return await Runner.run(
                starting_agent=agent,
                input=chat_history,
                run_config=google_gemini_config
            )
        
        # Run the async function in a new event loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(get_agent_response())
            loop.close()
        except Exception as e:
            print(f"Error running agent: {e}")
            return Response(
                {'error': 'Failed to get response from chatbot'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response_content = result.final_output
        updated_history = result.to_input_list()
        
        return Response({
            'response': response_content,
            'chat_history': updated_history
        })
        
    except Exception as e:
        print(f"Error in chat_with_bot: {str(e)}")
        return Response(
            {'error': 'An error occurred while processing your message'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def chatbot_status(request):
    """Check if chatbot service is available"""
    try:
        agent = get_chatbot_agent()
        if agent and google_gemini_config:
            return Response({'status': 'available'})
        else:
            return Response({'status': 'unavailable'})
    except Exception as e:
        return Response({'status': 'unavailable', 'error': str(e)})
