"""
Admin interface configuration for chatbot_app.
"""

from django.contrib import admin
from .models import AIRole, Conversation, Message


@admin.register(AIRole)
class AIRoleAdmin(admin.ModelAdmin):
    """
    Admin interface for AI Role model.
    """
    list_display = ('role_name', 'short_description', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('role_name', 'short_description', 'long_description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Admin interface for Conversation model.
    """
    list_display = ('title', 'user', 'ai_role', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'ai_role')
    search_fields = ('title', 'user__username', 'ai_role__role_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin interface for Message model.
    """
    list_display = ('conversation_title', 'role', 'content_preview', 'timestamp')
    list_filter = ('role', 'timestamp', 'conversation__ai_role')
    search_fields = ('content', 'conversation__title', 'conversation__user__username')
    readonly_fields = ('timestamp', 'conversation', 'role', 'content')
    date_hierarchy = 'timestamp'
    list_per_page = 25
    
    def conversation_title(self, obj):
        """Show conversation title instead of full conversation string."""
        return obj.conversation.title
    conversation_title.short_description = 'Conversation'
    conversation_title.admin_order_field = 'conversation__title'
    
    def content_preview(self, obj):
        """Show a preview of the message content."""
        return obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
    content_preview.short_description = 'Message'
    
    # Make it read-only to prevent accidental edits
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
