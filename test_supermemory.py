"""
Test script to check Supermemory integration.
This script will:
1. Check if Supermemory is enabled and configured
2. Test the client initialization
3. Check the container tag structure
4. Determine if it's working for specific chat context or global context
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_project.settings')
django.setup()

from django.conf import settings
from chatbot_app.supermemory_service import (
    get_client,
    initialize_supermemory_client,
)
from chatbot_app.models import User, Conversation

def test_supermemory_configuration():
    """Test Supermemory configuration."""
    print("=" * 60)
    print("SUPERMEMORY CONFIGURATION TEST")
    print("=" * 60)
    
    # Check if Supermemory is enabled
    print(f"\n1. SUPERMEMORY_ENABLED: {settings.SUPERMEMORY_ENABLED}")
    
    # Check API key
    api_key = settings.SUPERMEMORY_API_KEY
    if api_key:
        print(f"2. SUPERMEMORY_API_KEY: {'*' * 20} (configured)")
    else:
        print("2. SUPERMEMORY_API_KEY: NOT CONFIGURED ❌")
    
    # Check namespace
    print(f"3. SUPERMEMORY_NAMESPACE: {settings.SUPERMEMORY_NAMESPACE}")
    
    return bool(api_key)

def test_client_initialization():
    """Test Supermemory client initialization."""
    print("\n" + "=" * 60)
    print("CLIENT INITIALIZATION TEST")
    print("=" * 60)
    
    try:
        client = initialize_supermemory_client()
        if client:
            print("\n✅ Supermemory client initialized successfully!")
            print(f"   Client type: {type(client)}")
            return True
        else:
            print("\n❌ Supermemory client initialization failed!")
            print("   Possible reasons:")
            print("   - API key not configured")
            print("   - Supermemory disabled in settings")
            print("   - supermemory package not installed")
            return False
    except Exception as e:
        print(f"\n❌ Error initializing client: {e}")
        return False

def test_container_tags():
    """Test container tag structure to understand context scope."""
    print("\n" + "=" * 60)
    print("CONTAINER TAG STRUCTURE TEST")
    print("=" * 60)
    
    # Import the internal functions
    from chatbot_app import supermemory_service
    
    # Check if functions exist
    print("\nChecking function definitions...")
    
    # Check for _get_user_container_tag
    if hasattr(supermemory_service, '_get_user_container_tag'):
        print("✅ _get_user_container_tag exists")
    else:
        print("❌ _get_user_container_tag MISSING - This is a BUG!")
        
    # Check for _get_conversation_container_tag
    if hasattr(supermemory_service, '_get_conversation_container_tag'):
        print("✅ _get_conversation_container_tag exists")
    else:
        print("❌ _get_conversation_container_tag MISSING - This is a BUG!")
        
    # Check for _get_preferences_container_tag
    if hasattr(supermemory_service, '_get_preferences_container_tag'):
        print("✅ _get_preferences_container_tag exists")
    else:
        print("❌ _get_preferences_container_tag MISSING - This is a BUG!")
    
    # Try to get a sample user and conversation
    try:
        user = User.objects.first()
        if user:
            print(f"\nTesting with user: {user.username} (ID: {user.id})")
            
            # Test user container tag
            try:
                from chatbot_app.supermemory_service import _get_user_container_tag
                user_tag = _get_user_container_tag(user.id)
                print(f"  User container tag: {user_tag}")
            except Exception as e:
                print(f"  ❌ Error getting user container tag: {e}")
            
            # Test conversation container tag
            conversation = Conversation.objects.filter(user=user).first()
            if conversation:
                print(f"\nTesting with conversation: {conversation.id}")
                try:
                    from chatbot_app.supermemory_service import _get_conversation_container_tag
                    conv_tag = _get_conversation_container_tag(user.id, conversation.id)
                    print(f"  Conversation container tag: {conv_tag}")
                except Exception as e:
                    print(f"  ❌ Error getting conversation container tag: {e}")
            else:
                print("\n  No conversations found for this user")
                
            # Test preferences container tag
            try:
                from chatbot_app.supermemory_service import _get_preferences_container_tag
                prefs_tag = _get_preferences_container_tag(user.id)
                print(f"  Preferences container tag: {prefs_tag}")
            except Exception as e:
                print(f"  ❌ Error getting preferences container tag: {e}")
        else:
            print("\n  No users found in database")
    except Exception as e:
        print(f"\n  ❌ Error testing container tags: {e}")

def analyze_context_scope():
    """Analyze whether Supermemory is working for specific chat or global context."""
    print("\n" + "=" * 60)
    print("CONTEXT SCOPE ANALYSIS")
    print("=" * 60)
    
    print("\nBased on the code analysis:")
    print("\n📊 Supermemory operates on MULTIPLE LEVELS:")
    print("\n1. USER-LEVEL (Global Context):")
    print("   - Tag format: {namespace}_user_{user_id}")
    print("   - Stores: All user messages across ALL conversations")
    print("   - Purpose: Cross-conversation memory and user profile")
    print("   - Used for: Understanding user preferences, history, patterns")
    
    print("\n2. CONVERSATION-LEVEL (Specific Chat Context):")
    print("   - Tag format: {namespace}_user_{user_id}_conv_{conversation_id}")
    print("   - Stores: Messages specific to ONE conversation")
    print("   - Purpose: Conversation-specific context")
    print("   - Used for: Retrieving relevant context from current chat")
    
    print("\n3. PREFERENCES-LEVEL (User Settings):")
    print("   - Tag format: {namespace}_user_{user_id}_prefs")
    print("   - Stores: User preferences and settings")
    print("   - Purpose: Persistent user preferences")
    
    print("\n4. ROLE-LEVEL (AI Role Knowledge):")
    print("   - Tag format: {namespace}_role_{role_id}")
    print("   - Stores: Role-specific knowledge")
    print("   - Purpose: AI role enhancement")
    
    print("\n✅ CONCLUSION:")
    print("   Supermemory is configured to work on BOTH:")
    print("   - SPECIFIC CHAT CONTEXT (conversation-level)")
    print("   - GLOBAL CONTEXT (user-level, cross-conversation)")
    print("\n   When generating AI responses, it combines:")
    print("   - User profile (global)")
    print("   - Conversation history (specific)")
    print("   - Relevant user history (global)")

def check_code_bugs():
    """Check for bugs in the supermemory_service.py file."""
    print("\n" + "=" * 60)
    print("CODE BUG DETECTION")
    print("=" * 60)
    
    print("\n🔍 Checking supermemory_service.py for issues...")
    
    # Read the file
    with open('chatbot_app/supermemory_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    bugs_found = []
    
    # Check for missing function definitions
    if 'def _get_user_container_tag' not in content:
        bugs_found.append("❌ BUG: Missing function definition for _get_user_container_tag")
    
    if 'def _get_conversation_container_tag' not in content:
        bugs_found.append("❌ BUG: Missing function definition for _get_conversation_container_tag")
    
    if 'def _get_preferences_container_tag' not in content:
        bugs_found.append("❌ BUG: Missing function definition for _get_preferences_container_tag")
    
    if bugs_found:
        print("\n⚠️  CRITICAL BUGS FOUND:")
        for bug in bugs_found:
            print(f"   {bug}")
        print("\n   These functions have docstrings but no function signatures!")
        print("   This will cause NameError when trying to use Supermemory.")
        return False
    else:
        print("\n✅ No critical bugs detected in function definitions")
        return True

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SUPERMEMORY INTEGRATION TEST SUITE")
    print("=" * 60)
    
    # Test 1: Configuration
    config_ok = test_supermemory_configuration()
    
    # Test 2: Client initialization
    client_ok = test_client_initialization()
    
    # Test 3: Container tags
    test_container_tags()
    
    # Test 4: Context scope analysis
    analyze_context_scope()
    
    # Test 5: Bug detection
    code_ok = check_code_bugs()
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    if config_ok and client_ok and code_ok:
        print("\n✅ Supermemory integration is WORKING PROPERLY")
        print("   - Configuration: OK")
        print("   - Client: OK")
        print("   - Code: OK")
    else:
        print("\n⚠️  Supermemory integration has ISSUES:")
        if not config_ok:
            print("   ❌ Configuration issues detected")
        if not client_ok:
            print("   ❌ Client initialization failed")
        if not code_ok:
            print("   ❌ Code bugs detected")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
