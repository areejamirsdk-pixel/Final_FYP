# Digital Edge Ecommerce Chatbot Integration

This document explains how the Chainlit chatbot has been integrated into your Django ecommerce site.

## Overview

The chatbot integration includes:
- **Backend**: Django API endpoints for chatbot functionality
- **Frontend**: React component with floating chat widget
- **AI Agent**: Google Gemini-powered ecommerce assistant
- **Context Integration**: Product data and user information

## Files Added/Modified

### Backend (Django)
- `base/views/chatbot_views.py` - Chatbot API endpoints
- `base/urls/chatbot_urls.py` - URL routing for chatbot
- `backend/urls.py` - Updated to include chatbot routes
- `requirements.txt` - Added chatbot dependencies

### Frontend (React)
- `frontend/src/components/Chatbot.js` - Floating chat widget component
- `frontend/src/App.js` - Added chatbot to main app

### Setup
- `setup_chatbot.py` - Automated setup script
- `CHATBOT_INTEGRATION.md` - This documentation

## Features

### Chatbot Capabilities
- **Product Recommendations**: Suggests products based on user queries
- **Order Support**: Helps with order inquiries and status
- **General Support**: Answers questions about store policies
- **User Context**: Personalized responses based on user history
- **Product Context**: Access to current product catalog

### UI Features
- **Floating Button**: Always-visible chat button
- **Modal Interface**: Clean, modern chat interface
- **Real-time Typing**: Shows typing indicators
- **Message History**: Maintains conversation context
- **Responsive Design**: Works on all screen sizes

## Setup Instructions

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure API Key
Create a `.env` file in the `chatbot` directory:
```bash
# chatbot/.env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run Database Migrations
```bash
python manage.py migrate
```

### 4. Start the Application
```bash
# Terminal 1: Start Django backend
python manage.py runserver

# Terminal 2: Start React frontend
cd frontend
npm start
```

### 5. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Chatbot: Available as floating button on the site

## API Endpoints

### Chat with Bot
- **URL**: `/api/chatbot/chat/`
- **Method**: POST
- **Body**: 
  ```json
  {
    "message": "What products do you have?",
    "chat_history": []
  }
  ```

### Check Status
- **URL**: `/api/chatbot/status/`
- **Method**: GET
- **Response**: `{"status": "available"}`

## Customization

### Modify Chatbot Instructions
Edit the instructions in `base/views/chatbot_views.py`:
```python
instructions="""
Your custom instructions here...
"""
```

### Add More Context
Extend the `get_product_context()` and `get_user_context()` functions to include more data.

### Styling
Modify the styles in `frontend/src/components/Chatbot.js` to match your brand.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **API Key Issues**: Verify your Gemini API key is correct
3. **CORS Errors**: Check Django CORS settings
4. **Module Not Found**: Ensure the chatbot directory is in the Python path

### Debug Mode
Enable debug logging by adding to Django settings:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

## Security Considerations

- The chatbot API is currently set to `AllowAny` for testing
- Consider adding authentication for production use
- Validate and sanitize all user inputs
- Implement rate limiting for API calls

## Performance Optimization

- Cache product data to reduce database queries
- Implement message history limits
- Use async processing for heavy operations
- Consider using Redis for session storage

## Future Enhancements

- **Voice Support**: Add voice input/output
- **File Uploads**: Support image sharing
- **Multi-language**: Add internationalization
- **Analytics**: Track chatbot interactions
- **A/B Testing**: Test different response strategies

## Support

For issues or questions:
1. Check the Django logs for backend errors
2. Check the browser console for frontend errors
3. Verify API key configuration
4. Test API endpoints directly using curl or Postman

## License

This integration follows the same license as your main project.
