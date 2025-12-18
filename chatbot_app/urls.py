"""
URL configuration for chatbot_app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main URLs
    path('', views.dashboard_view, name='dashboard'),
    path('roles/', views.role_selection_view, name='role_selection'),
    path('roles/<int:role_id>/create/', views.create_conversation_view, name='create_conversation'),
    
    # Chat URLs
    path('chat/<int:conversation_id>/', views.chat_view, name='chat'),
    path('chat/<int:conversation_id>/send/', views.send_message_view, name='send_message'),
    path('chat/<int:conversation_id>/delete/', views.delete_conversation_view, name='delete_conversation'),
]


