from django.urls import path
from base.views import user_views as views

urlpatterns = [
    path('login/', views.requestLoginOtp, name='request-login-otp'),
    path('verify-otp/', views.verifyLoginOtp, name='verify-login-otp'),
    path('register/', views.registerUser, name='register'),

    path('profile/update/', views.updateUserProfile, name='user-profile-update'),
    path('profile/', views.getUserProfile, name='user-profile'),

    path('delete/<str:pk>/', views.deleteUser, name='user-delete'),
    path('update/<str:pk>/', views.updateUser, name='user-update'),

    path('<str:pk>/', views.getUserById, name='user'),
    path('', views.getUsers, name='users'),
]