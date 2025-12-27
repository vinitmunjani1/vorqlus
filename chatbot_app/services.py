"""
Service layer for chatbot functionality.
Extracted and adapted from pilot.py for Django integration.
"""

import json
import logging
import time
from pathlib import Path
from django.conf import settings
from together import Together
from .models import AIRole, Conversation, Message

logger = logging.getLogger(__name__)

# Simple greetings that should get brief responses
SIMPLE_GREETINGS = ["hi", "hello", "hey", "hey there", "hi there", "greetings", "sup", "what's up"]


def load_ai_roles_from_json(json_file_path=None):
    """
    Load AI roles from JSON file.
    
    Args:
        json_file_path (Path, optional): Path to the JSON file. Defaults to settings.ROLES_JSON_FILE
        
    Returns:
        list: List of role dictionaries containing role information
        
    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        json.JSONDecodeError: If the JSON file is invalid
    """
    if json_file_path is None:
        json_file_path = settings.ROLES_JSON_FILE
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            roles = json.load(file)
        return roles
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find the roles file '{json_file_path}'")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in '{json_file_path}': {e}")


def save_roles_to_db():
    """
    Load AI roles from JSON file and save them to the database.
    Updates existing roles if they already exist.
    """
    roles_data = load_ai_roles_from_json()
    
    for role_data in roles_data:
        AIRole.objects.update_or_create(
            role_name=role_data.get('role', ''),
            defaults={
                'short_description': role_data.get('short_description', ''),
                'long_description': role_data.get('long_description', ''),
                'system_prompt': role_data.get('system_prompt', ''),
            }
        )


def initialize_together_client():
    """
    Initialize the Together AI client.
    
    Returns:
        Together: Initialized Together AI client
        
    Raises:
        Exception: If API key is not configured
    """
    api_key = settings.TOGETHER_API_KEY
    if not api_key:
        raise ValueError("TOGETHER_API_KEY is not configured in settings")
    
    return Together(api_key=api_key)


def get_enhanced_system_prompt(base_system_prompt):
    """
    Enhance the system prompt with conciseness instructions.
    
    Args:
        base_system_prompt (str): Original system prompt from AI role
        
    Returns:
        str: Enhanced system prompt
    """
    conciseness_instruction = (
        "\n\nIMPORTANT: Keep your responses concise and match the user's communication style. "
        "For simple greetings or short questions, provide brief, friendly responses. "
        "Only provide detailed explanations when the user asks complex questions or requests more information."
    )
    return base_system_prompt + conciseness_instruction


def is_simple_greeting(message):
    """
    Check if the user message is a simple greeting that should get a brief response.
    
    Args:
        message (str): User's message
        
    Returns:
        bool: True if message is a simple greeting, False otherwise
    """
    message_lower = message.lower().strip()
    # Check if message is just a greeting (short and matches greeting patterns)
    if len(message_lower.split()) <= 3 and message_lower in SIMPLE_GREETINGS:
        return True
    # Also check if message starts with a greeting and is very short
    if len(message_lower.split()) <= 4:
        for greeting in SIMPLE_GREETINGS:
            if message_lower.startswith(greeting):
                return True
    return False


def build_messages_for_api(conversation, user_message, supermemory_context=None):
    """
    Build the messages list for API call from conversation history.
    
    Args:
        conversation (Conversation): The conversation object
        user_message (str): The new user message
        supermemory_context (str, optional): Additional context from Supermemory
        
    Returns:
        list: List of message dictionaries for API call
    """
    # Start with system prompt
    base_system_prompt = conversation.ai_role.system_prompt
    
    # Enhance with Supermemory context if available
    if supermemory_context:
        enhanced_prompt = f"{base_system_prompt}\n\n=== USER CONTEXT ===\n{supermemory_context}\n\nUse this context to provide personalized and context-aware responses. Reference relevant past conversations or user preferences when appropriate."
    else:
        enhanced_prompt = base_system_prompt
    
    system_prompt = get_enhanced_system_prompt(enhanced_prompt)
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    
    # Add conversation history
    previous_messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
    for msg in previous_messages:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Add current user message
    # If it's a simple greeting, add instruction for brevity
    if is_simple_greeting(user_message):
        messages.append({
            "role": "user",
            "content": user_message + " (Please respond briefly and concisely.)"
        })
    else:
        messages.append({
            "role": "user",
            "content": user_message
        })
    
    return messages


def get_ai_response(conversation, user_message, supermemory_context=None):
    """
    Get AI response for a user message in a conversation.
    
    Args:
        conversation (Conversation): The conversation object
        user_message (str): The user's message
        supermemory_context (str, optional): Additional context from Supermemory
        
    Returns:
        str: AI's response
        
    Raises:
        Exception: If API call fails
    """
    try:
        t_init = time.perf_counter()
        client = initialize_together_client()
        messages = build_messages_for_api(conversation, user_message, supermemory_context)
        
        t0 = time.perf_counter()
        response = client.chat.completions.create(
            model=settings.TOGETHER_MODEL_NAME,
            messages=messages
        )
        t_api = time.perf_counter() - t0
        logger.info(f"Together AI API call took {t_api:.4f}s")
        
        ai_response = response.choices[0].message.content
        return ai_response
        
    except Exception as e:
        raise Exception(f"Failed to get AI response: {str(e)}")


def create_conversation_title(first_message):
    """
    Generate a conversation title from the first message.
    
    Args:
        first_message (str): The first message in the conversation
        
    Returns:
        str: Generated title (max 200 chars)
    """
    # Take first 50 words or first 200 characters, whichever is shorter
    words = first_message.split()[:50]
    title = ' '.join(words)
    
    if len(title) > 200:
        title = title[:197] + '...'
    
    return title if title else "New Conversation"

