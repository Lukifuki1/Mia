
// MIA Enterprise AGI - Unified JavaScript

class MIAInterface {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.messageHistory = [];
        this.currentSessionId = null;
        
        this.init();
    }
    
    init() {
        console.log('🧠 MIA Interface initializing...');
        this.setupEventListeners();
        this.updateSystemStatus();
    }
    
    setupEventListeners() {
        // Send button
        const sendButton = document.getElementById('sendButton');
        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        // Message input
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        // Voice button
        const voiceButton = document.getElementById('voiceButton');
        if (voiceButton) {
            voiceButton.addEventListener('click', () => this.toggleVoiceInput());
        }
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('✅ WebSocket connected');
            this.isConnected = true;
            this.updateConnectionStatus('Connected', 'status-connected');
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onclose = () => {
            console.log('❌ WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected', 'status-error');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connectWebSocket(), 3000);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('Error', 'status-error');
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'assistant':
                this.addMessage(data.content, 'assistant');
                break;
            case 'thought':
                this.addThought(data.content, data.confidence);
                break;
            case 'status':
                this.updateSystemStatus(data.content);
                break;
            case 'error':
                this.addMessage(data.content, 'error');
                break;
        }
    }
    
    sendMessage() {
        const messageInput = document.getElementById('messageInput');
        if (!messageInput) return;
        
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Send via WebSocket if connected
        if (this.isConnected && this.websocket) {
            this.websocket.send(JSON.stringify({
                type: 'user_message',
                content: message,
                timestamp: Date.now()
            }));
        } else {
            // Fallback to API
            this.sendMessageViaAPI(message);
        }
        
        // Clear input
        messageInput.value = '';
    }
    
    async sendMessageViaAPI(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSessionId
                })
            });
            
            const data = await response.json();
            
            if (data.response) {
                this.addMessage(data.response, 'assistant');
            }
            
            if (data.session_id) {
                this.currentSessionId = data.session_id;
            }
            
        } catch (error) {
            console.error('API error:', error);
            this.addMessage('Sorry, I encountered an error processing your message.', 'error');
        }
    }
    
    addMessage(content, type) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        if (type === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">${this.escapeHtml(content)}</div>
                <div class="message-time">${timestamp}</div>
            `;
        } else if (type === 'assistant') {
            messageDiv.innerHTML = `
                <div class="message-content">🧠 ${this.escapeHtml(content)}</div>
                <div class="message-time">${timestamp}</div>
            `;
        } else if (type === 'error') {
            messageDiv.innerHTML = `
                <div class="message-content">❌ ${this.escapeHtml(content)}</div>
                <div class="message-time">${timestamp}</div>
            `;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Store in history
        this.messageHistory.push({
            content: content,
            type: type,
            timestamp: Date.now()
        });
    }
    
    addThought(content, confidence) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        const thoughtDiv = document.createElement('div');
        thoughtDiv.className = 'message thought-message';
        thoughtDiv.innerHTML = `
            <div class="thought-content">
                💭 <em>${this.escapeHtml(content)}</em>
                <span class="confidence">(Confidence: ${(confidence * 100).toFixed(1)}%)</span>
            </div>
        `;
        
        chatMessages.appendChild(thoughtDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    updateConnectionStatus(status, className) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `status-indicator ${className}`;
        }
    }
    
    async updateSystemStatus() {
        try {
            const response = await fetch('/api/interfaces/status');
            const data = await response.json();
            
            const systemStatus = document.getElementById('systemStatus');
            if (systemStatus) {
                systemStatus.innerHTML = `
                    <div>Active Connections: ${data.active_connections}</div>
                    <div>Active Sessions: ${data.active_sessions}</div>
                    <div>Messages: ${data.message_count}</div>
                `;
            }
            
            // Update dashboard if present
            this.updateDashboard(data);
            
        } catch (error) {
            console.error('Failed to update system status:', error);
        }
    }
    
    updateDashboard(data) {
        const agiStatus = document.getElementById('agiStatus');
        if (agiStatus) {
            agiStatus.innerHTML = `
                <div>Status: ✅ Running</div>
                <div>Active Sessions: ${data.active_sessions}</div>
            `;
        }
        
        const chatActivity = document.getElementById('chatActivity');
        if (chatActivity) {
            chatActivity.innerHTML = `
                <div>Active Connections: ${data.active_connections}</div>
                <div>Total Messages: ${data.message_count}</div>
            `;
        }
        
        const securityStatus = document.getElementById('securityStatus');
        if (securityStatus) {
            securityStatus.innerHTML = `
                <div>Security: 🔒 Active</div>
                <div>Encryption: ✅ Enabled</div>
            `;
        }
        
        const systemMetrics = document.getElementById('systemMetrics');
        if (systemMetrics) {
            systemMetrics.innerHTML = `
                <div>Uptime: ${this.formatUptime(Date.now() - (data.timestamp * 1000))}</div>
                <div>Last Update: ${new Date(data.timestamp * 1000).toLocaleTimeString()}</div>
            `;
        }
    }
    
    toggleVoiceInput() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            this.startVoiceRecognition();
        } else {
            alert('Voice recognition is not supported in this browser.');
        }
    }
    
    startVoiceRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        const voiceButton = document.getElementById('voiceButton');
        if (voiceButton) {
            voiceButton.style.background = '#e53e3e';
            voiceButton.textContent = '🔴';
        }
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const messageInput = document.getElementById('messageInput');
            if (messageInput) {
                messageInput.value = transcript;
            }
        };
        
        recognition.onend = () => {
            if (voiceButton) {
                voiceButton.style.background = '#48bb78';
                voiceButton.textContent = '🎤';
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            if (voiceButton) {
                voiceButton.style.background = '#48bb78';
                voiceButton.textContent = '🎤';
            }
        };
        
        recognition.start();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatUptime(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `${days}d ${hours % 24}h`;
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }
}

// Global functions for initialization
function initializeChatInterface() {
    const miaInterface = new MIAInterface();
    miaInterface.connectWebSocket();
    
    // Update status every 30 seconds
    setInterval(() => miaInterface.updateSystemStatus(), 30000);
}

function initializeDashboard() {
    const miaInterface = new MIAInterface();
    
    // Update dashboard every 10 seconds
    setInterval(() => miaInterface.updateSystemStatus(), 10000);
}

// Initialize interface when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌐 MIA Interface loaded');
    
    // Initialize based on current page
    if (window.location.pathname === '/chat') {
        initializeChatInterface();
    } else if (window.location.pathname === '/dashboard') {
        initializeDashboard();
    }
});
