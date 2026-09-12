from django.urls import path
from base.views import user_views as views


urlpatterns = [
       path('login/', views.requestLoginOtp, name='request_login_otp'),
    path('verify-otp/', views.verifyLoginOtp, name='verify_login_otp'),

    path('register/', views.registerUser, name='register'),

    path('profile/', views.getUserProfile, name="users-profile"),
    path('profile/update/', views.updateUserProfile, name="user-profile-update"),
    path('', views.getUsers, name="users"),

    path('<str:pk>/', views.getUserById, name='user'),

    path('update/<str:pk>/', views.updateUser, name='user-update'),

    path('delete/<str:pk>/', views.deleteUser, name='user-delete'),
]
