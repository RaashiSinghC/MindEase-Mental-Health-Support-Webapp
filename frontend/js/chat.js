const API_BASE = window.API_BASE || 'https://mindease-backend-s59o.onrender.com/api';
// Enhanced Chat functionality
document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
    
    // Load chat history
    loadChatHistory();
    
    // Focus on input field
    document.getElementById('messageInput').focus();
});

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE}/chat/send`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        if (data.success) {
            addMessageToChat(data.response, 'bot', data.timestamp);
        } else {
            addMessageToChat("I'm having trouble responding right now. Please try again.", 'bot');
        }
        
    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator();
        addMessageToChat("Sorry, I'm having connection issues. Please check your internet.", 'bot');
    }
}

function sendQuickReply(message) {
    document.getElementById('messageInput').value = message;
    sendMessage();
}

function addMessageToChat(message, sender, timestamp = null) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    
    messageDiv.className = `message ${sender}-message`;
    messageDiv.innerHTML = `
        ${message}
        <div class="timestamp">${timestamp ? formatTimestamp(timestamp) : 'Just now'}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'typing-indicator';
    typingDiv.textContent = 'MindEase is typing...';
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function formatTimestamp(timestamp) {
    try {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (error) {
        return 'Just now';
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function loadChatHistory() {
    try {
        const response = await fetch(`http://localhost:5000/api/chat/history`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        
        if (data.success && data.chat_history && data.chat_history.length > 0) {
            // Clear initial message
            document.getElementById('chatMessages').innerHTML = '';
            
            // Load history in chronological order
            data.chat_history.reverse().forEach(chat => {
                addMessageToChat(chat.user_message, 'user', chat.timestamp);
                addMessageToChat(chat.bot_response, 'bot', chat.timestamp);
            });
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

async function clearChat() {
    if (!confirm('Are you sure you want to clear all chat history? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5000/api/chat/clear', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({})
        });

        const data = await response.json();
        
        if (data.success) {
            // Clear chat UI but keep one welcome message
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = '';
            addMessageToChat(
                `Chat history cleared! ${data.message || "I'm here whenever you need to talk!"}`, 
                'bot'
            );
        } else {
            alert(`Error clearing chat: ${data.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error clearing chat:', error);
        alert('Network error. Please check your connection and try again.');
    }
}

function showQuickReplies() {
    const quickReplies = document.getElementById('quickReplies');
    if (quickReplies) {
        quickReplies.style.display = quickReplies.style.display === 'none' ? 'flex' : 'none';
    }

}
