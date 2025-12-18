"""
Database models for the chatbot application.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AIRole(models.Model):
    """
    Represents an AI role that can be selected for conversations.
    Stores information from the JSON file.
    """
    role_name = models.CharField(max_length=200, unique=True)
    short_description = models.TextField()
    long_description = models.TextField()
    system_prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['role_name']
        verbose_name = 'AI Role'
        verbose_name_plural = 'AI Roles'

    def __str__(self):
        return self.role_name
    
    def get_category(self):
        """
        Get the category for this AI role based on categorization logic.
        
        Returns:
            str: The category name this role belongs to
        """
        from .utils import categorize_role
        return categorize_role(
            self.role_name,
            self.short_description,
            self.long_description
        )
    
    def get_icon(self):
        """
        Get the Bootstrap Icon class for this AI role.
        
        Returns:
            str: Bootstrap Icon class name (e.g., "bi-heart-pulse")
        """
        from .utils import get_role_icon
        return get_role_icon(self.role_name)


class Conversation(models.Model):
    """
    Represents a conversation between a user and an AI role.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    ai_role = models.ForeignKey(AIRole, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'

    def __str__(self):
        return f"{self.user.username} - {self.ai_role.role_name} - {self.title}"

    def get_last_message(self):
        """Get the last message in this conversation."""
        return self.messages.last()


class Message(models.Model):
    """
    Represents a single message in a conversation.
    Can be from either the user or the AI assistant.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        # Shorter, cleaner string representation
        content_preview = self.content[:30] + '...' if len(self.content) > 30 else self.content
        return f"{self.role.title()}: {content_preview}"
