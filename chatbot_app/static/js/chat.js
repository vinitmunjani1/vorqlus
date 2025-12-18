/**
 * JavaScript for chat interface functionality
 */

let conversationId = null;

function initializeChat(convId) {
    conversationId = convId;
    const chatMessages = document.getElementById('chat-messages');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const loadingIndicator = document.getElementById('loading-indicator');

    // Check if elements exist
    if (!chatMessages || !messageForm || !messageInput) {
        console.error('Chat elements not found');
        return;
    }

    // Auto-scroll to bottom on load
    scrollToBottom();

    // Handle form submission
    messageForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Form submitted'); // Debug log
        
        const message = messageInput.value.trim();
        if (!message) {
            console.log('Empty message, returning');
            return;
        }

        console.log('Sending message:', message); // Debug log

        // Disable input and button
        messageInput.disabled = true;
        sendButton.disabled = true;

        // Add user message to chat immediately (optimistic update)
        addMessageToChat('user', message);
        const userMessageText = message; // Store for potential rollback
        messageInput.value = '';

        // Show loading indicator
        loadingIndicator.classList.add('active');
        scrollToBottom();

        try {
            // Send message to server
            const csrfToken = getCookie('csrftoken');
            if (!csrfToken) {
                throw new Error('CSRF token not found');
            }

            const response = await fetch(`/chat/${conversationId}/send/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    message: message
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                // Add AI response to chat
                addMessageToChat('assistant', data.ai_message.content);
            } else {
                // Show error message
                addMessageToChat('assistant', 'Error: ' + (data.error || 'Failed to get response'));
            }
        } catch (error) {
            console.error('Error:', error);
            addMessageToChat('assistant', 'Error: Failed to send message. Please check the console for details.');
        } finally {
            // Hide loading indicator
            loadingIndicator.classList.remove('active');
            
            // Re-enable input and button
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
            
            scrollToBottom();
        }
    });

    // Auto-focus input
    messageInput.focus();

    // Handle Enter key to send message, Shift+Enter for new line
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); // Prevent default new line
            if (!sendButton.disabled && messageInput.value.trim()) {
                messageForm.dispatchEvent(new Event('submit'));
            }
        }
        // Shift+Enter will allow default behavior (new line)
    });
}

function addMessageToChat(role, content) {
    console.log('Adding message:', role, content); // Debug log
    const chatMessages = document.getElementById('chat-messages');
    
    if (!chatMessages) {
        console.error('chat-messages element not found');
        return;
    }
    
    // Remove empty state message if it exists
    const emptyState = chatMessages.querySelector('#empty-state') || chatMessages.querySelector('.text-center.text-muted');
    if (emptyState) {
        console.log('Removing empty state');
        emptyState.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });

    // Escape HTML and convert line breaks to <br> tags
    const escapedContent = content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    const formattedContent = escapedContent.replace(/\n/g, '<br>');

    messageDiv.innerHTML = `
        <div>
            <div class="message-bubble">
                ${formattedContent}
            </div>
            <div class="message-time">
                ${timeString}
            </div>
        </div>
    `;

    // Insert before loading indicator
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        chatMessages.insertBefore(messageDiv, loadingIndicator);
    } else {
        chatMessages.appendChild(messageDiv);
    }
    
    console.log('Message added to DOM'); // Debug log
    scrollToBottom();
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

