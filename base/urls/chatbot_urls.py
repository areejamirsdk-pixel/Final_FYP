from django.urls import path
from base.views import ai_ordering_chatbot_views as views

urlpatterns = [
    path('chat/', views.ai_chat_guest, name='ai_chat_guest'),
    path('chat/authenticated/', views.ai_chat_with_ordering, name='ai_chat_with_ordering'),
    path('chat/status/', views.chatbot_status, name='chatbot_status'),
    path('orders/', views.get_my_orders_ai, name='get_my_orders_ai'),
]
