// chat.js - Embeddable chat functionality
(function() {
    'use strict';
    
    // DOM elements
    let conversationConfig, conversationId, chatLog, messageInput, submitButton, userNameInput, typingIndicator;
    let chatSocket;
    
    // State
    let currentAiMessage = '';
    let currentAiElement = null;
    let isAiResponding = false;
    const agentName = 'Agent';

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeElements();
        initializeWebSocket();
        setupEventListeners();
        updateSubmitButton();
        messageInput.focus();
    });

    function initializeElements() {
        conversationConfig = JSON.parse(document.getElementById('conversation-config').textContent);
        window.conversationConfig = conversationConfig;
        conversationId = conversationConfig.conversation_id;
        chatLog = document.querySelector('#chat-log');
        messageInput = document.querySelector('#chat-message-input');
        submitButton = document.querySelector('#chat-message-submit');
        userNameInput = document.querySelector('#user-name-input');
        typingIndicator = document.querySelector('#typing-indicator');
    }

    function initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        chatSocket = new WebSocket(
            protocol + '//' + window.location.host + '/ws/conversation/' + conversationId + '/'
        );

        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            switch(data.type) {
                case 'user_message':
                    if (data.user_name != 'system') {
                        appendUserMessage(data.message, data.user_name);
                    }
                    break;
                
                case 'message':
                    appendMessage(data.message, data.sender);
                    break;
                
                case 'ai_start':
                    handleAiStart();
                    break;
                    
                case 'chunk':
                    handleAiChunk(data.chunk);
                    break;
                
                case 'revive':
                    reviveChat(data.chat_history);
                    break;
                  
                case 'complete':
                    handleAiComplete();
                    break;
                    
                case 'typing':
                    handleTyping(data.is_typing);
                    break;
                    
                case 'error':
                    appendMessage(`Error: ${data.error}`, 'error');
                    isAiResponding = false;
                    updateSubmitButton();
                    break;
                    
                default:
                    // Fallback for old format
                    appendMessage(data.message, 'user');
            }
        };

        chatSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
            appendMessage('Connection lost. Please refresh the page.', 'error');
        };

        chatSocket.onerror = function(e) {
            console.error('WebSocket error:', e);
            appendMessage('Connection error. Please check your internet connection.', 'error');
        };
    }
    
    function reviveChat(chatHistory) {
        chatHistory.forEach((historyMessage) => {
            if (historyMessage.message.slice(0, 4) != '@@@@') {
                appendMessage(historyMessage.message, historyMessage.sender);
            }
        });
        const reconnectWith = window.sessionStorage.getItem('chatbot_reconnect_with');
        if (reconnectWith) {
            sendSystemMessage(reconnectWith);
            window.sessionStorage.removeItem('chatbot_reconnect_with');
        }
    }

    function setupEventListeners() {
        messageInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter' && !isAiResponding) {
                sendMessage();
            }
        });

        submitButton.addEventListener('click', sendMessage);
        
        // Handle window resize for iframe responsiveness
        window.addEventListener('resize', function() {
            scrollToBottom();
        });
    }

    function appendMessage(message, sender = 'user') {
        const timestamp = new Date().toLocaleTimeString();
        const messageDiv = document.createElement('div');
        
        let className = '';
        switch(sender) {
            case 'ai':
                className = 'ai-message';
                // For AI messages, allow HTML rendering
                const markdownParsedMessage = parseMarkdown(message);
                // messageDiv.innerHTML = `[${timestamp}] AI: ${markdownParsedMessage}`;
                messageDiv.innerHTML = `<span class="agent-name">${agentName}:</span> ${markdownParsedMessage}`;
                break;
            case 'user':
                className = 'user-message';
                // For user messages, escape HTML for security
                // messageDiv.textContent = `[${timestamp}] ${message}`;
                configureUserMessageDiv(messageDiv, 'User', message);
                // messageDiv.textContent = `<span class="agent-name">User:</span> ${message}`;
                break;
            case 'error':
                className = 'error-message';
                messageDiv.textContent = `[${timestamp}] ${message}`;
                break;
        }
        
        messageDiv.className = className;
        chatLog.appendChild(messageDiv);
        
        // Add spacing
        addMessageSpacing();
        scrollToBottom();
    }
    
    function configureUserMessageDiv(messageDiv, userName, message) {
        messageDiv.className = 'user-message';
        const userNameSpan = document.createElement('span');
        userNameSpan.classList.add('agent-name');
        userNameSpan.innerText = userName + ':';
        messageDiv.appendChild(userNameSpan);
        const messageTextNode = document.createTextNode(' ' + message);
        messageDiv.appendChild(messageTextNode);
        return messageDiv;
    }
    
    function appendUserMessage(message, userName) {
        const timestamp = new Date().toLocaleTimeString();
        const messageDiv = document.createElement('div');
        configureUserMessageDiv(messageDiv, userName, message)
        // Escape HTML in user messages for security
        // messageDiv.textContent = `[${timestamp}] ${userName}: ${message}`;
        // messageDiv.textContent = `<span class="agent-name">${userName}:</span> ${message}`;
        chatLog.appendChild(messageDiv);
        
        addMessageSpacing();
        scrollToBottom();
    }

    function handleAiStart() {
        isAiResponding = true;
        currentAiMessage = '';
        const timestamp = new Date().toLocaleTimeString();
        
        // Create a new div for the AI message
        currentAiElement = document.createElement('div');
        currentAiElement.className = 'ai-message';
        // currentAiElement.innerHTML = `[${timestamp}] AI: `;
        currentAiElement.innerHTML = `<span class="agent-name">${agentName}:</span> `;
        chatLog.appendChild(currentAiElement);
        
        updateSubmitButton();
        scrollToBottom();
    }

    function handleAiChunk(chunk) {
        if (currentAiElement) {
            currentAiMessage += chunk;
        
            // For display, we'll process directives but only show content
            const processed = processDirectives(currentAiMessage);
            const markdowned = parseMarkdown(processed.content);
            // console.log(markdowned)
            const timestamp = new Date().toLocaleTimeString();
            // currentAiElement.innerHTML = `[${timestamp}] AI: ${markdowned}`;
            currentAiElement.innerHTML = `<span class="agent-name">${agentName}:</span> ${markdowned}`;
            scrollToBottom();
        }
    }

    function handleAiComplete() {
        if (isAiResponding && currentAiElement) {
            // Process the complete message for directives
            const processed = processDirectives(currentAiMessage);
            const markdowned = parseMarkdown(processed.content);
        
            // Dispatch any directives found
            if (processed.directives.length > 0) {
                dispatchDirectives(processed.directives);
            }
        
            // Update the display with just the content (no directives visible)
            const timestamp = new Date().toLocaleTimeString();
            // currentAiElement.innerHTML = `[${timestamp}] AI: ${markdowned}`;
            currentAiElement.innerHTML = `<span class="agent-name">${agentName}:</span> ${markdowned}`;
        
            addMessageSpacing();
        
            isAiResponding = false;
            currentAiMessage = '';
            currentAiElement = null;
            updateSubmitButton();
            scrollToBottom();
        }
    }
    
    function handleTyping(isTyping) {
        if (isTyping) {
            typingIndicator.classList.remove('hidden');
        } else {
            typingIndicator.classList.add('hidden');
        }
    }

    function updateSubmitButton() {
        submitButton.disabled = isAiResponding;
        submitButton.textContent = isAiResponding ? 'AI is responding...' : 'Send';
    }

    function sendMessage() {
        const message = messageInput.value.trim();
        const userName = userNameInput.value.trim() || 'User';
        
        if (message && !isAiResponding && chatSocket.readyState === WebSocket.OPEN) {
            // Send to server
            chatSocket.send(JSON.stringify({
                'message': message,
                'user_name': userName
            }));
            messageInput.value = '';
        }
    }
    
    function sendSystemMessage(message) {
        if (chatSocket.readyState === WebSocket.OPEN) {
            // Send to server
            chatSocket.send(JSON.stringify({
                'message': message,
                'user_name': 'system'
            }));
        }
    }

    function addMessageSpacing() {
        const spacer = document.createElement('div');
        spacer.innerHTML = '<br>';
        chatLog.appendChild(spacer);
    }

    function scrollToBottom() {
        chatLog.scrollTop = chatLog.scrollHeight;
    }
    
    function processDirectives(message) {
        const lines = message.split('\n');
        const directives = [];
        const contentLines = [];
    
        let processingDirectives = true;
    
        for (const line of lines) {
            // console.log('looking for directives in line:', line)
            if (processingDirectives && line.startsWith('@@@@')) {
                // Parse directive
                const directiveText = line.substring(4).trim();
                const spaceIndex = directiveText.indexOf(' ');
            
                let command, args;
                if (spaceIndex === -1) {
                    command = directiveText;
                    args = null;
                } else {
                    command = directiveText.substring(0, spaceIndex);
                    args = directiveText.substring(spaceIndex + 1).trim();
                }
            
                directives.push({ command, args });
            } else {
                // Once we hit a non-directive line, stop processing directives
                // processingDirectives = false;
                contentLines.push(line);
            }
        }
    
        return {
            directives,
            content: contentLines.join('\n').trim()
        };
    }
    
    function dispatchDirectives(directives) {
        directives.forEach(({ command, args }) => {
            const event = new CustomEvent(`chat-${command.toLowerCase()}`, {
                detail: args,
                bubbles: true
            });
        
            console.log(`Dispatching chat directive: ${command}`, args);
            document.dispatchEvent(event);
        });
    }
    
    

    // Expose some functions globally for debugging/customization
    window.ChatEmbed = {
        sendMessage: sendMessage,
        scrollToBottom: scrollToBottom,
        isConnected: function() {
            return chatSocket && chatSocket.readyState === WebSocket.OPEN;
        }
    };

})();