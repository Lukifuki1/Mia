
class MIAInterface {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.setupEventListeners();
        this.connect();
    }
    
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.isConnected = true;
            this.updateConnectionStatus('Connected', true);
            console.log('Connected to MIA');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected', false);
            console.log('Disconnected from MIA');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connect(), 3000);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    setupEventListeners() {
        // Chat input
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Voice input
        document.getElementById('voice-btn').addEventListener('click', () => {
            this.processVoiceInput();
        });
        
        // Image generation
        document.getElementById('generate-image-btn').addEventListener('click', () => {
            this.generateImage();
        });
        
        // Adult mode
        document.getElementById('activate-adult-btn').addEventListener('click', () => {
            this.activateAdultMode();
        });
        
        // Show adult mode panel on triple click
        let clickCount = 0;
        document.addEventListener('click', () => {
            clickCount++;
            setTimeout(() => { clickCount = 0; }, 1000);
            if (clickCount === 3) {
                document.getElementById('adult-mode-panel').style.display = 'block';
            }
        });
    }
    
    sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (message && this.isConnected) {
            this.addMessage('user', message);
            
            this.ws.send(JSON.stringify({
                type: 'chat',
                message: message
            }));
            
            input.value = '';
        }
    }
    
    processVoiceInput() {
        if (this.isConnected) {
            this.addMessage('system', 'Listening for voice input...');
            
            this.ws.send(JSON.stringify({
                type: 'voice_input'
            }));
        }
    }
    
    generateImage() {
        const prompt = document.getElementById('image-prompt').value.trim();
        const style = document.getElementById('image-style').value;
        
        if (prompt && this.isConnected) {
            this.addMessage('system', `Generating image: "${prompt}" in ${style} style...`);
            
            this.ws.send(JSON.stringify({
                type: 'generate_image',
                prompt: prompt,
                style: style
            }));
        }
    }
    
    activateAdultMode() {
        const phrase = document.getElementById('adult-phrase').value;
        
        if (phrase && this.isConnected) {
            this.ws.send(JSON.stringify({
                type: 'activate_adult_mode',
                phrase: phrase
            }));
            
            document.getElementById('adult-phrase').value = '';
        }
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'chat_response':
                this.addMessage('mia', data.message);
                this.updateStatus(data);
                break;
                
            case 'image_generated':
                this.displayGeneratedImage(data);
                break;
                
            case 'speech_generated':
                this.playGeneratedSpeech(data);
                break;
                
            case 'system_status':
                this.updateSystemInfo(data);
                break;
                
            case 'adult_mode_activated':
                this.addMessage('system', data.message);
                document.getElementById('adult-mode-panel').style.display = 'none';
                break;
                
            case 'error':
                this.addMessage('error', data.message);
                break;
                
            case 'system':
                this.addMessage('system', data.message);
                break;
        }
    }
    
    addMessage(sender, message) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const timestamp = new Date().toLocaleTimeString();
        messageDiv.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-time">${timestamp}</div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    displayGeneratedImage(data) {
        const imageContainer = document.getElementById('generated-image');
        imageContainer.innerHTML = `
            <img src="${data.image_data}" alt="${data.prompt}">
            <p>Style: ${data.style} | Time: ${data.generation_time.toFixed(2)}s</p>
        `;
        
        this.addMessage('mia', `I've generated an image for: "${data.prompt}"`);
    }
    
    playGeneratedSpeech(data) {
        // Create audio element and play
        const audio = new Audio(data.audio_data);
        audio.play().catch(e => console.error('Audio playback failed:', e));
        
        this.addMessage('mia', `🔊 Speaking: "${data.text}"`);
    }
    
    updateStatus(data) {
        if (data.consciousness_state) {
            document.getElementById('consciousness-state').textContent = data.consciousness_state;
        }
        if (data.emotional_tone) {
            document.getElementById('emotional-state').textContent = data.emotional_tone;
        }
    }
    
    updateConnectionStatus(status, connected) {
        const statusElement = document.getElementById('connection-status');
        statusElement.textContent = status;
        statusElement.className = connected ? 'status-connected' : 'status-disconnected';
    }
    
    updateSystemInfo(data) {
        const systemDetails = document.getElementById('system-details');
        systemDetails.innerHTML = `
            <p><strong>Consciousness:</strong> ${data.consciousness.state}</p>
            <p><strong>Emotion:</strong> ${data.consciousness.emotional_state}</p>
            <p><strong>Focus:</strong> ${data.consciousness.attention_focus}</p>
            <p><strong>Energy:</strong> ${(data.consciousness.energy_level * 100).toFixed(0)}%</p>
            <p><strong>Creativity:</strong> ${(data.consciousness.creativity_level * 100).toFixed(0)}%</p>
            <p><strong>Connections:</strong> ${data.connections}</p>
        `;
    }
}

// Initialize MIA interface when page loads
document.addEventListener('DOMContentLoaded', () => {
    new MIAInterface();
});
