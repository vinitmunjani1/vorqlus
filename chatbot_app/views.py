"""
Views for the chatbot application.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import AIRole, Conversation, Message
from .forms import UserRegistrationForm, MessageForm
from .services import (
    save_roles_to_db,
    get_ai_response,
    create_conversation_title,
)
from .utils import get_all_categories
from .supermemory_service import (
    store_conversation_memory,
    get_enhanced_context,
)


def register_view(request):
    """
    Handle user registration.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            django_messages.success(request, 'Registration successful! Welcome!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """
    Handle user login.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        from django.contrib.auth import authenticate
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            django_messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            django_messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')


@login_required
def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    django_messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Display user's dashboard with conversation list.
    """
    # Ensure AI roles are loaded in database
    if AIRole.objects.count() == 0:
        try:
            save_roles_to_db()
            django_messages.info(request, 'AI roles loaded successfully!')
        except Exception as e:
            django_messages.error(request, f'Error loading AI roles: {str(e)}')
    
    # Get user's conversations
    user_conversations = Conversation.objects.filter(user=request.user)
    
    context = {
        'conversations': user_conversations,
    }
    return render(request, 'dashboard.html', context)


@login_required
def role_selection_view(request):
    """
    Display available AI roles for selection with category filtering.
    """
    # Ensure AI roles are loaded
    if AIRole.objects.count() == 0:
        try:
            save_roles_to_db()
        except Exception as e:
            django_messages.error(request, f'Error loading AI roles: {str(e)}')
            return redirect('dashboard')
    
    ai_roles = AIRole.objects.all()
    
    # Get all available categories
    categories = ['All'] + get_all_categories()
    
    # Categorize each role (for data attributes in template)
    roles_with_categories = []
    for role in ai_roles:
        category = role.get_category()
        roles_with_categories.append({
            'role': role,
            'category': category
        })
    
    context = {
        'ai_roles': ai_roles,
        'roles_with_categories': roles_with_categories,
        'categories': categories,
    }
    return render(request, 'role_selection.html', context)


@login_required
def create_conversation_view(request, role_id):
    """
    Create a new conversation with the selected AI role.
    """
    ai_role = get_object_or_404(AIRole, id=role_id)
    
    # Create new conversation
    conversation = Conversation.objects.create(
        user=request.user,
        ai_role=ai_role,
        title=f"Chat with {ai_role.role_name}"
    )
    
    return redirect('chat', conversation_id=conversation.id)


@login_required
def chat_view(request, conversation_id):
    """
    Display the chat interface for a conversation.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    
    # Get all messages for this conversation
    conversation_messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
    
    # Get all AI roles for switching
    ai_roles = AIRole.objects.all()
    
    context = {
        'conversation': conversation,
        'messages': conversation_messages,
        'ai_roles': ai_roles,
        'form': MessageForm(),
    }
    return render(request, 'chat.html', context)


@login_required
@require_http_methods(["POST"])
def send_message_view(request, conversation_id):
    """
    AJAX endpoint to send a message and get AI response.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Update conversation title if this is the first message (before creating new message)
        is_first_message = conversation.messages.count() == 0
        
        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        # Store user message in Supermemory
        try:
            store_conversation_memory(
                request.user,
                conversation,
                user_message,
                role='user'
            )
        except Exception as e:
            # Log error but continue - Supermemory is optional
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to store user message in Supermemory: {e}")
        
        # Update conversation title if this was the first message
        if is_first_message:
            conversation.title = create_conversation_title(user_message)
            conversation.save()
        
        # Get enhanced context from Supermemory
        supermemory_context = None
        try:
            supermemory_context = get_enhanced_context(
                request.user,
                conversation,
                user_message,
                include_profile=True,
                include_conversation=True
            )
        except Exception as e:
            # Log error but continue - Supermemory is optional
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to retrieve Supermemory context: {e}")
        
        # Get AI response
        try:
            ai_response = get_ai_response(conversation, user_message, supermemory_context)
        except Exception as e:
            return JsonResponse({'error': f'Failed to get AI response: {str(e)}'}, status=500)
        
        # Save AI response
        ai_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response
        )
        
        # Store assistant response in Supermemory
        try:
            store_conversation_memory(
                request.user,
                conversation,
                ai_response,
                role='assistant'
            )
        except Exception as e:
            # Log error but continue - Supermemory is optional
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to store assistant message in Supermemory: {e}")
        
        # Update conversation timestamp
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'user_message': {
                'content': user_msg.content,
                'timestamp': user_msg.timestamp.isoformat(),
            },
            'ai_message': {
                'content': ai_msg.content,
                'timestamp': ai_msg.timestamp.isoformat(),
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def delete_conversation_view(request, conversation_id):
    """
    Delete a conversation.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversation.delete()
    django_messages.success(request, 'Conversation deleted successfully.')
    return redirect('dashboard')
