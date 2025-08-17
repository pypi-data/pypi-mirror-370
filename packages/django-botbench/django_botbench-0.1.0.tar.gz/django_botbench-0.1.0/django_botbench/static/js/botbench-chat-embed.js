window.addEventListener('message', (event) => {
    // console.log('Window received message:', event.data);
    const evd = event.data;
    if (evd.type === 'agentConfiguration') {
        if (evd.variant === 'setConversationId') {
            window.sessionStorage.setItem('chatbot_conversation_id', evd.conversationId);
        }
    }
    else if (evd.type === 'agentRequest') {
        if (evd.variant === 'navigation') {
            window.sessionStorage.setItem('chatbot_conversation_id', evd.conversationId);
            window.sessionStorage.setItem('chatbot_reconnect_with', '@@@@RECONNECT');
            window.location.href = evd.detail;
        }
    }
})

window.addEventListener('DOMContentLoaded', (event) => {
    const chatEmbedFrame = document.createElement('iframe');
    chatEmbedFrame.classList.add('botbench-chat-embed');
    const conversationId = window.sessionStorage.getItem('chatbot_conversation_id');
    if (conversationId === null) {
        chatEmbedFrame.src = '/chat/embed/conversation/';
    }
    else {
        chatEmbedFrame.src = '/chat/embed/conversation/' + conversationId + '/';
    }
    document.querySelector('div#botbench-chat-embed').appendChild(chatEmbedFrame);
})

