"""
Supermemory service layer for storing and retrieving user memories, 
conversation history, and preferences.
"""

import logging
from django.conf import settings
from .models import User, Conversation, Message, AIRole

logger = logging.getLogger(__name__)

# Initialize Supermemory client (lazy loading)
_supermemory_client = None


def initialize_supermemory_client():
    """
    Initialize the Supermemory client.
    
    Returns:
        Supermemory client instance or None if API key is not configured
        
    Raises:
        ImportError: If supermemory package is not installed
    """
    global _supermemory_client
    
    if _supermemory_client is not None:
        return _supermemory_client
    
    if not settings.SUPERMEMORY_ENABLED:
        logger.info("Supermemory is disabled")
        return None
    
    api_key = settings.SUPERMEMORY_API_KEY
    if not api_key:
        logger.warning("SUPERMEMORY_API_KEY is not configured")
        return None
    
    try:
        from supermemory import Supermemory
        _supermemory_client = Supermemory(api_key=api_key)
        logger.info("Supermemory client initialized successfully")
        return _supermemory_client
    except ImportError:
        logger.error("supermemory package is not installed. Run: pip install supermemory")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Supermemory client: {e}")
        return None


def get_client():
    """Get or initialize the Supermemory client."""
    return initialize_supermemory_client()


def _get_user_container_tag(user_id):
    """Get container tag for user-specific memories."""
    namespace = getattr(settings, 'SUPERMEMORY_NAMESPACE', 'default')
    # Use UUID from profile if available, fallback to ID
    try:
        user_identifier = str(User.objects.get(id=user_id).userprofile.uuid)
    except Exception:
        user_identifier = str(user_id)
        
    return f"{namespace}_user_{user_identifier}"


def _get_conversation_container_tag(user_id, conversation_id):
    """Get container tag for conversation-specific memories."""
    namespace = getattr(settings, 'SUPERMEMORY_NAMESPACE', 'default')
    # Use UUID from profile if available, fallback to ID
    try:
        user_identifier = str(User.objects.get(id=user_id).userprofile.uuid)
    except Exception:
        user_identifier = str(user_id)

    return f"{namespace}_user_{user_identifier}_conv_{conversation_id}"


def _get_preferences_container_tag(user_id):
    """Get container tag for user preferences."""
    namespace = getattr(settings, 'SUPERMEMORY_NAMESPACE', 'default')
    try:
        user_identifier = str(User.objects.get(id=user_id).userprofile.uuid)
    except Exception:
        user_identifier = str(user_id)

    return f"{namespace}_user_{user_identifier}_prefs"


def _get_role_container_tag(role_id):
    """Get container tag for role-specific knowledge."""
    namespace = getattr(settings, 'SUPERMEMORY_NAMESPACE', 'default')
    return f"{namespace}_role_{role_id}"


def store_conversation_memory(user, conversation, message, role='user'):
    """
    Store a conversation message in Supermemory.
    Stores at BOTH user-level (for cross-conversation memory) and conversation-level.
    
    Args:
        user: User instance
        conversation: Conversation instance
        message: Message content string
        role: 'user' or 'assistant'
        
    Returns:
        bool: True if stored successfully, False otherwise
    """
    client = get_client()
    if not client:
        return False
    
    try:
        # Format message with metadata
        content = f"[{role.upper()}] {message}"
        
        # Store at USER level for cross-conversation memory retrieval
        user_container_tag = _get_user_container_tag(user.id)
        try:
            client.add(
                content=content,
                container_tag=user_container_tag
            )
            logger.debug(f"Stored {role} message in Supermemory at user level for user {user.id}")
        except Exception as api_error:
            logger.warning(f"Supermemory API error during user-level memory storage: {api_error}")
        
        # Also store at conversation level for conversation-specific context
        conv_container_tag = _get_conversation_container_tag(user.id, conversation.id)
        try:
            client.add(
                content=content,
                container_tag=conv_container_tag
            )
            logger.debug(f"Stored {role} message in Supermemory for conversation {conversation.id}")
        except Exception as api_error:
            logger.warning(f"Supermemory API error during conversation-level memory storage: {api_error}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to store conversation memory: {e}")
        return False


def store_user_preference(user, key, value):
    """
    Store a user preference in Supermemory.
    
    Args:
        user: User instance
        key: Preference key (e.g., 'communication_style')
        value: Preference value
        
    Returns:
        bool: True if stored successfully, False otherwise
    """
    client = get_client()
    if not client:
        return False
    
    try:
        container_tag = _get_preferences_container_tag(user.id)
        content = f"{key}: {value}"
        
        client.add(
            content=content,
            container_tag=container_tag
        )
        
        logger.debug(f"Stored user preference {key} for user {user.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to store user preference: {e}")
        return False


def store_role_knowledge(role, knowledge):
    """
    Store AI role-specific knowledge in Supermemory.
    
    Args:
        role: AIRole instance
        knowledge: Knowledge content string
        
    Returns:
        bool: True if stored successfully, False otherwise
    """
    client = get_client()
    if not client:
        return False
    
    try:
        container_tag = _get_role_container_tag(role.id)
        
        client.add(
            content=knowledge,
            container_tag=container_tag
        )
        
        logger.debug(f"Stored knowledge for role {role.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to store role knowledge: {e}")
        return False


def search_memories(user, query, limit=5, container_tag=None):
    """
    Search user's memories in Supermemory.
    
    Args:
        user: User instance
        query: Search query string
        limit: Maximum number of results to return
        container_tag: Optional specific container tag to search
        
    Returns:
        list: List of memory results (empty list if error or no results)
    """
    client = get_client()
    if not client:
        return []
    
    try:
        # Handle API errors gracefully
        try:
            if container_tag is not None:
                # Search in specific container
                response = client.search.memories(q=query, container_tag=container_tag, limit=limit)
            else:
                # Search at user level for cross-conversation memories
                user_container_tag = _get_user_container_tag(user.id)
                response = client.search.memories(q=query, container_tag=user_container_tag, limit=limit)
        except Exception as api_error:
            logger.warning(f"Supermemory API error during search: {api_error}")
            return []
        
        # Extract results from the response object
        results = []
        if response:
            if hasattr(response, 'results'):
                results = response.results or []
            elif isinstance(response, dict) and 'results' in response:
                results = response.get('results', [])
        
        if results:
            logger.debug(f"Found {len(results)} memories for query: {query}")
        return results
    except Exception as e:
        logger.error(f"Failed to search memories: {e}")
        return []


def get_user_context(user, query, limit=5):
    """
    Get relevant user context from Supermemory for a query.
    
    Args:
        user: User instance
        query: Query string to find relevant context
        limit: Maximum number of context items to return
        
    Returns:
        str: Formatted context string (empty if no context found)
    """
    memories = search_memories(user, query, limit=limit)
    
    if not memories:
        return ""
    
    context_parts = []
    for memory in memories:
        if hasattr(memory, 'content'):
            context_parts.append(memory.content)
        elif isinstance(memory, dict) and 'content' in memory:
            context_parts.append(memory['content'])
    
    if context_parts:
        context = "\n".join(context_parts)
        logger.debug(f"Retrieved {len(context_parts)} context items for user {user.id}")
        return context
    return ""


def get_conversation_context(conversation, query, limit=10):
    """
    Get relevant context from a specific conversation.
    
    Args:
        conversation: Conversation instance
        query: Query string to find relevant context
        limit: Maximum number of context items to return
        
    Returns:
        str: Formatted context string (empty if no context found)
    """
    client = get_client()
    if not client:
        return ""
    
    try:
        container_tag = _get_conversation_container_tag(conversation.user.id, conversation.id)
        memories = search_memories(conversation.user, query, limit=limit, container_tag=container_tag)
        
        if not memories:
            return ""
        
        context_parts = []
        for memory in memories:
            if hasattr(memory, 'content'):
                context_parts.append(memory.content)
            elif isinstance(memory, dict) and 'content' in memory:
                context_parts.append(memory['content'])
        
        if context_parts:
            context = "\n".join(context_parts)
            logger.debug(f"Retrieved {len(context_parts)} context items from conversation {conversation.id}")
            return context
        return ""
    except Exception as e:
        logger.error(f"Failed to get conversation context: {e}")
        return ""


def get_user_profile(user, query):
    """
    Get user profile (static + dynamic context) from Supermemory.
    
    Args:
        user: User instance
        query: Query string to get relevant profile information
        
    Returns:
        dict: Profile dictionary with 'static' and 'dynamic' keys, or empty dict if error
    """
    client = get_client()
    if not client:
        return {"static": "", "dynamic": ""}
    
    try:
        container_tag = _get_user_container_tag(user.id)
        
        # Handle API errors gracefully
        try:
            profile = client.profile(container_tag=container_tag, q=query)
        except Exception as api_error:
            logger.warning(f"Supermemory API error during profile retrieval: {api_error}")
            return {"static": "", "dynamic": ""}
        
        if profile and hasattr(profile, 'profile'):
            return {
                "static": getattr(profile.profile, 'static', ''),
                "dynamic": getattr(profile.profile, 'dynamic', '')
            }
        elif profile and isinstance(profile, dict):
            profile_data = profile.get('profile', {})
            return {
                "static": profile_data.get('static', ''),
                "dynamic": profile_data.get('dynamic', '')
            }
        return {"static": "", "dynamic": ""}
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        return {"static": "", "dynamic": ""}


def get_user_preferences(user):
    """
    Retrieve all user preferences from Supermemory.
    
    Args:
        user: User instance
        
    Returns:
        dict: Dictionary of preference key-value pairs
    """
    client = get_client()
    if not client:
        return {}
    
    try:
        container_tag = _get_preferences_container_tag(user.id)
        memories = search_memories(user, "preferences", limit=50, container_tag=container_tag)
        
        preferences = {}
        for memory in memories:
            content = memory.content if hasattr(memory, 'content') else memory.get('content', '')
            if ':' in content:
                key, value = content.split(':', 1)
                preferences[key.strip()] = value.strip()
        
        return preferences
    except Exception as e:
        logger.error(f"Failed to get user preferences: {e}")
        return {}


def get_user_preference(user, key, default=None):
    """
    Get a specific user preference.
    
    Args:
        user: User instance
        key: Preference key
        default: Default value if preference not found
        
    Returns:
        str: Preference value or default
    """
    preferences = get_user_preferences(user)
    return preferences.get(key, default)


def update_user_preference(user, key, value):
    """
    Update a user preference (stores as new memory in Supermemory).
    
    Args:
        user: User instance
        key: Preference key
        value: Preference value
        
    Returns:
        bool: True if stored successfully, False otherwise
    """
    return store_user_preference(user, key, value)


def store_conversation_summary(conversation, summary):
    """
    Store a summary of a conversation for quick context retrieval.
    
    Args:
        conversation: Conversation instance
        summary: Summary text
        
    Returns:
        bool: True if stored successfully, False otherwise
    """
    client = get_client()
    if not client:
        return False
    
    try:
        container_tag = _get_conversation_container_tag(conversation.user.id, conversation.id)
        content = f"[CONVERSATION_SUMMARY] {summary}"
        
        client.add(
            content=content,
            container_tag=container_tag
        )
        
        logger.debug(f"Stored conversation summary for conversation {conversation.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to store conversation summary: {e}")
        return False


def get_enhanced_context(user, conversation, query, include_profile=True, include_conversation=True):
    """
    Get comprehensive context for AI response generation.
    Combines user profile, conversation history, and relevant memories.
    
    Args:
        user: User instance
        conversation: Conversation instance
        query: Current user query
        include_profile: Whether to include user profile
        include_conversation: Whether to include conversation context
        
    Returns:
        str: Formatted context string to enhance system prompt
    """
    context_parts = []
    
    # Get user profile
    if include_profile:
        profile = get_user_profile(user, query)
        if profile.get('static'):
            context_parts.append(f"User Profile (Static): {profile['static']}")
        if profile.get('dynamic'):
            context_parts.append(f"User Profile (Dynamic): {profile['dynamic']}")
    
    # Get conversation context
    if include_conversation:
        conv_context = get_conversation_context(conversation, query, limit=10)
        if conv_context:
            context_parts.append(f"Previous Conversation Context:\n{conv_context}")
    
    # Get general user context
    user_context = get_user_context(user, query, limit=5)
    if user_context:
        context_parts.append(f"Relevant User History:\n{user_context}")
    
    if context_parts:
        return "\n\n".join(context_parts)
    return ""

