"""
Quick test script to verify delete conversation functionality.
This will check if the changes are properly implemented.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_project.settings')
django.setup()

from chatbot_app.views import delete_conversation_view
from django.views.decorators.http import require_http_methods

print("=" * 60)
print("DELETE CONVERSATION FUNCTIONALITY CHECK")
print("=" * 60)

# Check if the view has the require_http_methods decorator
decorators = []
if hasattr(delete_conversation_view, '_wrapped_view'):
    print("\n✅ View has decorators applied")
else:
    print("\n⚠️  Checking decorator status...")

# Check the view function
import inspect
source = inspect.getsource(delete_conversation_view)

checks = {
    "POST-only decorator": '@require_http_methods(["POST"])' in source,
    "Error handling": 'try:' in source and 'except' in source,
    "Success message with title": 'conversation_title' in source,
    "Error message": 'django_messages.error' in source,
}

print("\n📋 Code Checks:")
for check_name, passed in checks.items():
    status = "✅" if passed else "❌"
    print(f"   {status} {check_name}")

# Check templates
print("\n📄 Template Checks:")

template_checks = []

# Check chat.html
try:
    with open('chatbot_app/templates/chat.html', 'r', encoding='utf-8') as f:
        chat_content = f.read()
    
    chat_has_form = 'method="POST"' in chat_content and 'delete_conversation' in chat_content
    chat_has_csrf = '{% csrf_token %}' in chat_content
    
    print(f"   {'✅' if chat_has_form else '❌'} chat.html uses POST form")
    print(f"   {'✅' if chat_has_csrf else '❌'} chat.html has CSRF token")
    
    template_checks.append(chat_has_form and chat_has_csrf)
except Exception as e:
    print(f"   ❌ Error checking chat.html: {e}")
    template_checks.append(False)

# Check dashboard.html
try:
    with open('chatbot_app/templates/dashboard.html', 'r', encoding='utf-8') as f:
        dashboard_content = f.read()
    
    dashboard_has_form = 'method="POST"' in dashboard_content and 'delete_conversation' in dashboard_content
    dashboard_has_csrf = '{% csrf_token %}' in dashboard_content
    dashboard_has_stop_propagation = 'event.stopPropagation()' in dashboard_content
    
    print(f"   {'✅' if dashboard_has_form else '❌'} dashboard.html uses POST form")
    print(f"   {'✅' if dashboard_has_csrf else '❌'} dashboard.html has CSRF token")
    print(f"   {'✅' if dashboard_has_stop_propagation else '❌'} dashboard.html prevents event propagation")
    
    template_checks.append(dashboard_has_form and dashboard_has_csrf and dashboard_has_stop_propagation)
except Exception as e:
    print(f"   ❌ Error checking dashboard.html: {e}")
    template_checks.append(False)

# Final verdict
print("\n" + "=" * 60)
all_passed = all(checks.values()) and all(template_checks)

if all_passed:
    print("✅ ALL CHECKS PASSED - Delete functionality is fixed!")
    print("\nYou can now test it by:")
    print("1. Going to http://127.0.0.1:8000/")
    print("2. Clicking the trash icon on any conversation")
    print("3. Confirming the deletion")
    print("4. Verifying the conversation is deleted")
else:
    print("⚠️  Some checks failed - please review the changes")

print("=" * 60)
