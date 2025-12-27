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
import time
import logging
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)
logger = logging.getLogger(__name__)

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


def health_check(request):
    """
    Health check endpoint for Railway.
    Returns a simple 200 OK response.
    """
    return JsonResponse({'status': 'ok', 'message': 'Vorqlus is running!'})


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


def landing_page_view(request):
    """
    Display the landing page for unauthenticated users.
    Redirects to dashboard if user is logged in.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


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
        'chat_history': conversation_messages,
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
    start_total = time.perf_counter()
    logger.info(f"--- Starting message processing for conversation {conversation_id} ---")
    
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    
    try:
        t0 = time.perf_counter()
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        logger.info(f"Step: JSON parsing took {time.perf_counter() - t0:.4f}s")
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Update conversation title if this is the first message (before creating new message)
        is_first_message = conversation.messages.count() == 0
        
        # Save user message
        t0 = time.perf_counter()
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        logger.info(f"Step: DB save user message took {time.perf_counter() - t0:.4f}s")
        
        # Store user message in Supermemory (BACKGROUND)
        sm_time = 0
        try:
            # We don't wait for this to finish
            executor.submit(
                store_conversation_memory,
                request.user,
                conversation,
                user_message,
                'user'
            )
            logger.info("Step: Supermemory store user message (queued to background)")
        except Exception as e:
            logger.warning(f"Failed to queue user message storage: {e}")
        
        # Update conversation title if this was the first message
        if is_first_message:
            t0 = time.perf_counter()
            conversation.title = create_conversation_title(user_message)
            conversation.save()
            logger.info(f"Step: Update conversation title took {time.perf_counter() - t0:.4f}s")
        
        # Get enhanced context from Supermemory
        supermemory_context = None
        t0 = time.perf_counter()
        try:
            supermemory_context = get_enhanced_context(
                request.user,
                conversation,
                user_message,
                include_profile=True,
                include_conversation=True
            )
            dur = time.perf_counter() - t0
            sm_time += dur
            logger.info(f"Step: Supermemory retrieve context took {dur:.4f}s")
        except Exception as e:
            # Log error but continue - Supermemory is optional
            logger.warning(f"Failed to retrieve Supermemory context: {e}")
        
        # Get AI response
        ai_time = 0
        t0 = time.perf_counter()
        try:
            ai_response = get_ai_response(conversation, user_message, supermemory_context)
            ai_time = time.perf_counter() - t0
            logger.info(f"Step: AI response generation (Together AI API) took {ai_time:.4f}s")
        except Exception as e:
            return JsonResponse({'error': f'Failed to get AI response: {str(e)}'}, status=500)
        
        # Save AI response
        t0 = time.perf_counter()
        ai_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response
        )
        logger.info(f"Step: DB save AI response took {time.perf_counter() - t0:.4f}s")
        
        # Store assistant response in Supermemory (BACKGROUND)
        try:
            # We don't wait for this to finish
            executor.submit(
                store_conversation_memory,
                request.user,
                conversation,
                ai_response,
                'assistant'
            )
            logger.info("Step: Supermemory store assistant response (queued to background)")
        except Exception as e:
            logger.warning(f"Failed to queue assistant message storage: {e}")
        
        # Update conversation timestamp
        conversation.save()
        
        total_time = time.perf_counter() - start_total
        logger.info(f"--- TOTAL PROCESSING TIME: {total_time:.4f}s ---")
        
        return JsonResponse({
            'success': True,
            'user_message': {
                'content': user_msg.content,
                'timestamp': user_msg.timestamp.isoformat(),
            },
            'ai_message': {
                'content': ai_msg.content,
                'timestamp': ai_msg.timestamp.isoformat(),
            },
            'timings': {
                'total': total_time,
                'supermemory': sm_time,
                'ai': ai_time
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.exception("Unexpected error in send_message_view")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def delete_conversation_view(request, conversation_id):
    """
    Delete a conversation (POST only for security).
    """
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        conversation_title = conversation.title
        conversation.delete()
        django_messages.success(request, f'Conversation "{conversation_title}" deleted successfully.')
        return redirect('dashboard')
    except Exception as e:
        django_messages.error(request, f'Failed to delete conversation: {str(e)}')
        return redirect('dashboard')
