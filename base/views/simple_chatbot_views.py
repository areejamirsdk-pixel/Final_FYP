from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json
import os
import requests
from django.conf import settings
from dotenv import load_dotenv


# Simple chatbot implementation using direct API calls
def get_gemini_response(message, chat_history=None):
    """Get response from Gemini API directly"""
    try:
        # Get API key from environment
        api_key = "AIzaSyCf-MMEzrCINC9v9-IGuZg4elpd0Yrh1iI"
        print("api_key", api_key)
        if not api_key:
            return "I'm sorry, the chatbot service is not configured. Please add your Gemini API key."
        
        # Prepare the request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        # Build context
        context = "You are a helpful ecommerce assistant for Digital Edge, an online electronics store. "
        context += "Help customers with product questions, orders, and general support. "
        context += "Be friendly, professional, and helpful. "
        context += "If you don't know specific product details, ask them to check the product page. "
        context += "Always end responses by asking if there's anything else you can help with."
        
        # Prepare messages
        messages = [{"role": "user", "parts": [{"text": context}]}]
        
        if chat_history:
            for msg in chat_history:
                if msg.get('role') == 'user':
                    messages.append({"role": "user", "parts": [{"text": msg.get('content', '')}]})
                elif msg.get('role') == 'assistant':
                    messages.append({"role": "model", "parts": [{"text": msg.get('content', '')}]})
        
        # Add current message
        messages.append({"role": "user", "parts": [{"text": message}]})
        
        payload = {
            "contents": messages
        }
        
        headers = {
            'Content-Type': 'application/json',
        }
        
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
    print("view is calling")
    """Handle chatbot messages with simple API approach"""
    try:
        data = request.data
        message = data.get('message', '')
        chat_history = data.get('chat_history', [])
        
        if not message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get response from Gemini
        response_content = get_gemini_response(message, chat_history)
        
        # Update chat history
        updated_history = chat_history.copy()
        updated_history.append({"role": "user", "content": message})
        updated_history.append({"role": "assistant", "content": response_content})
        
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
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            return Response({'status': 'available'})
        else:
            return Response({'status': 'unavailable', 'error': 'API key not configured'})
    except Exception as e:
        return Response({'status': 'unavailable', 'error': str(e)})
