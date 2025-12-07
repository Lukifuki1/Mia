// Advanced MIA UI JavaScript

class MIAInterface {
    constructor() {
        this.ws = null;
        this.currentTool = 'chat-interface';
        this.adultModeEnabled = false;
        this.isConnected = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadTheme();
        this.startSystemMonitoring();
    }
    
    setupEventListeners() {
        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // Navigation
        document.querySelectorAll('.nav-item[data-tool]').forEach(item => {
            item.addEventListener('click', () => {
                this.switchTool(item.dataset.tool);
            });
        });
        
        // Chat functionality
        document.getElementById('send-message').addEventListener('click', () => {
            this.sendMessage();
        });
        
        document.getElementById('chat-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        document.getElementById('chat-input').addEventListener('input', (e) => {
            this.autoResizeTextarea(e.target);
        });
        
        // Quick actions
        document.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', () => {
                this.handleQuickAction(btn.dataset.action);
            });
        });
        
        // Image generation
        document.getElementById('generate-image').addEventListener('click', () => {
            this.generateImage();
        });
        
        // Code execution
        document.getElementById('run-code').addEventListener('click', () => {
            this.runCode();
        });
        
        // Adult mode toggle
        document.getElementById('adult-mode-toggle').addEventListener('click', () => {
            this.toggleAdultMode();
        });
        
        // File upload
        document.getElementById('attach-file').addEventListener('click', () => {
            this.openFileDialog();
        });
        
        // Clear chat
        document.getElementById('clear-chat').addEventListener('click', () => {
            this.clearChat();
        });
        
        // Export chat
        document.getElementById('export-chat').addEventListener('click', () => {
            this.exportChat();
        });
        
        // Voice toggle
        document.getElementById('voice-toggle').addEventListener('click', () => {
            this.toggleVoice();
        });
        
        // Modal close
        document.getElementById('modal-close').addEventListener('click', () => {
            this.closeModal();
        });
        
        // Modal overlay click
        document.getElementById('modal-overlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                this.closeModal();
            }
        });
        
        // Memory search
        document.getElementById('memory-search').addEventListener('input', (e) => {
            this.searchMemories(e.target.value);
        });
        
        // Memory filter
        document.getElementById('memory-filter').addEventListener('change', (e) => {
            this.filterMemories(e.target.value);
        });
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.updateConnectionStatus('Connected');
            this.showNotification('Connected to MIA', 'success');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected');
            this.showNotification('Disconnected from MIA', 'error');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
                this.connectWebSocket();
            }, 3000);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showNotification('Connection error', 'error');
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'chat_response':
                this.addMessage(data.content, 'system');
                break;
            case 'image_generated':
                this.addGeneratedImage(data.image_path, data.prompt);
                break;
            case 'code_result':
                this.displayCodeResult(data.result, data.error);
                break;
            case 'system_status':
                this.updateSystemStatus(data.status);
                break;
            case 'memory_data':
                this.displayMemoryData(data.memories);
                break;
            case 'notification':
                this.showNotification(data.message, data.level);
                break;
            case 'voice_response':
                this.handleVoiceResponse(data.audio_data);
                break;
        }
    }
    
    sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message || !this.isConnected) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Send to MIA
        this.ws.send(JSON.stringify({
            type: 'chat_message',
            content: message,
            adult_mode: this.adultModeEnabled
        }));
        
        // Clear input
        input.value = '';
        this.autoResizeTextarea(input);
        
        // Show loading indicator
        this.showLoading();
    }
    
    addMessage(content, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-brain"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const header = document.createElement('div');
        header.className = 'message-header';
        header.innerHTML = `
            <span class="sender">${sender === 'user' ? 'You' : 'MIA'}</span>
            <span class="timestamp">${new Date().toLocaleTimeString()}</span>
        `;
        
        const text = document.createElement('div');
        text.className = 'message-text';
        text.innerHTML = this.formatMessage(content);
        
        messageContent.appendChild(header);
        messageContent.appendChild(text);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        this.hideLoading();
    }
    
    formatMessage(content) {
        // Basic markdown-like formatting
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
        content = content.replace(/`(.*?)`/g, '<code>$1</code>');
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }
    
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    handleQuickAction(action) {
        const input = document.getElementById('chat-input');
        const prompts = {
            explain: 'Please explain ',
            code: 'Write code to ',
            create: 'Create a ',
            analyze: 'Analyze '
        };
        
        input.value = prompts[action] || '';
        input.focus();
        this.autoResizeTextarea(input);
    }
    
    switchTool(toolName) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-tool="${toolName}"]`).classList.add('active');
        
        // Switch panels
        document.querySelectorAll('.tool-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(toolName).classList.add('active');
        
        this.currentTool = toolName;
        
        // Load tool-specific data
        this.loadToolData(toolName);
    }
    
    loadToolData(toolName) {
        switch (toolName) {
            case 'system-monitor':
                this.loadSystemMonitor();
                break;
            case 'memory-explorer':
                this.loadMemoryExplorer();
                break;
            case 'evolution-status':
                this.loadEvolutionStatus();
                break;
            case 'learning-dashboard':
                this.loadLearningDashboard();
                break;
        }
    }
    
    generateImage() {
        const prompt = document.getElementById('image-prompt').value.trim();
        const style = document.getElementById('image-style').value;
        const size = document.getElementById('image-size').value;
        
        if (!prompt) {
            this.showNotification('Please enter a prompt', 'warning');
            return;
        }
        
        this.showLoading('Generating image...');
        
        this.ws.send(JSON.stringify({
            type: 'generate_image',
            prompt: prompt,
            style: style,
            size: size,
            adult_mode: this.adultModeEnabled
        }));
    }
    
    addGeneratedImage(imagePath, prompt) {
        const gallery = document.getElementById('image-gallery');
        const imageItem = document.createElement('div');
        imageItem.className = 'image-item';
        
        imageItem.innerHTML = `
            <img src="${imagePath}" alt="Generated image" loading="lazy">
            <div class="image-info">
                <div class="image-prompt">${prompt}</div>
                <div class="image-actions">
                    <button class="image-action" onclick="this.downloadImage('${imagePath}')">
                        <i class="fas fa-download"></i> Download
                    </button>
                    <button class="image-action" onclick="this.shareImage('${imagePath}')">
                        <i class="fas fa-share"></i> Share
                    </button>
                </div>
            </div>
        `;
        
        gallery.insertBefore(imageItem, gallery.firstChild);
        this.hideLoading();
    }
    
    runCode() {
        const code = document.getElementById('code-editor').value.trim();
        const language = document.getElementById('code-language').value;
        
        if (!code) {
            this.showNotification('Please enter code to execute', 'warning');
            return;
        }
        
        this.showLoading('Executing code...');
        
        this.ws.send(JSON.stringify({
            type: 'execute_code',
            code: code,
            language: language
        }));
    }
    
    displayCodeResult(result, error) {
        const resultElement = document.getElementById('code-result');
        
        if (error) {
            resultElement.textContent = `Error: ${error}`;
            resultElement.style.color = 'var(--error)';
        } else {
            resultElement.textContent = result;
            resultElement.style.color = 'var(--text-primary)';
        }
        
        this.hideLoading();
    }
    
    toggleAdultMode() {
        if (!this.adultModeEnabled) {
            this.showModal('Adult Mode Confirmation', `
                <p>You are about to enable Adult Mode. This will allow MIA to:</p>
                <ul>
                    <li>Generate adult content</li>
                    <li>Engage in mature conversations</li>
                    <li>Access 18+ capabilities</li>
                </ul>
                <p>Are you sure you want to continue?</p>
                <div style="margin-top: 1rem; display: flex; gap: 1rem; justify-content: flex-end;">
                    <button onclick="miaInterface.closeModal()" class="control-btn">Cancel</button>
                    <button onclick="miaInterface.enableAdultMode()" class="control-btn" style="background-color: var(--warning); color: white;">Enable Adult Mode</button>
                </div>
            `);
        } else {
            this.disableAdultMode();
        }
    }
    
    enableAdultMode() {
        this.adultModeEnabled = true;
        document.body.classList.add('adult-mode');
        document.getElementById('adult-mode-toggle').innerHTML = '<i class="fas fa-unlock"></i><span>Adult Mode</span>';
        this.switchTool('adult-mode-panel');
        this.closeModal();
        this.showNotification('Adult Mode enabled', 'warning');
    }
    
    disableAdultMode() {
        this.adultModeEnabled = false;
        document.body.classList.remove('adult-mode');
        document.getElementById('adult-mode-toggle').innerHTML = '<i class="fas fa-lock"></i><span>Adult Mode</span>';
        this.showNotification('Adult Mode disabled', 'info');
    }
    
    toggleTheme() {
        const body = document.body;
        const isDark = body.classList.contains('dark-theme');
        
        if (isDark) {
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
            document.getElementById('theme-toggle').innerHTML = '<i class="fas fa-sun"></i>';
            localStorage.setItem('theme', 'light');
        } else {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            document.getElementById('theme-toggle').innerHTML = '<i class="fas fa-moon"></i>';
            localStorage.setItem('theme', 'dark');
        }
    }
    
    loadTheme() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        const body = document.body;
        
        if (savedTheme === 'light') {
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
            document.getElementById('theme-toggle').innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            document.getElementById('theme-toggle').innerHTML = '<i class="fas fa-moon"></i>';
        }
    }
    
    showModal(title, content) {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-content').innerHTML = content;
        document.getElementById('modal-overlay').classList.add('active');
    }
    
    closeModal() {
        document.getElementById('modal-overlay').classList.remove('active');
    }
    
    showLoading(message = 'MIA is thinking...') {
        const indicator = document.getElementById('loading-indicator');
        indicator.querySelector('span').textContent = message;
        indicator.classList.add('active');
    }
    
    hideLoading() {
        document.getElementById('loading-indicator').classList.remove('active');
    }
    
    showNotification(message, type = 'info') {
        const notifications = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        notifications.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    updateConnectionStatus(status) {
        const statusElement = document.querySelector('#connection-status');
        if (statusElement) {
            statusElement.textContent = status;
        }
    }
    
    startSystemMonitoring() {
        setInterval(() => {
            if (this.isConnected) {
                this.ws.send(JSON.stringify({ type: 'get_system_status' }));
            }
        }, 5000); // Update every 5 seconds
    }
    
    updateSystemStatus(status) {
        // Update CPU usage
        const cpuElement = document.getElementById('cpu-usage');
        if (cpuElement && status.cpu_usage) {
            cpuElement.style.width = `${status.cpu_usage}%`;
        }
        
        // Update RAM usage
        const ramElement = document.getElementById('ram-usage');
        if (ramElement && status.ram_usage) {
            ramElement.style.width = `${status.ram_usage}%`;
        }
        
        // Update status indicators
        if (status.consciousness) {
            document.getElementById('consciousness-status').textContent = status.consciousness.state;
        }
        
        if (status.memory) {
            document.getElementById('memory-status').textContent = 'Operational';
        }
    }
    
    loadSystemMonitor() {
        // Request system status
        if (this.isConnected) {
            this.ws.send(JSON.stringify({ type: 'get_detailed_status' }));
        }
    }
    
    loadMemoryExplorer() {
        // Request memory data
        if (this.isConnected) {
            this.ws.send(JSON.stringify({ type: 'get_memories' }));
        }
    }
    
    displayMemoryData(memories) {
        const memoryList = document.getElementById('memory-list');
        memoryList.innerHTML = '';
        
        memories.forEach(memory => {
            const memoryItem = document.createElement('div');
            memoryItem.className = 'memory-item';
            memoryItem.innerHTML = `
                <div class="memory-header">
                    <span class="memory-type">${memory.type}</span>
                    <span class="memory-timestamp">${new Date(memory.timestamp * 1000).toLocaleString()}</span>
                </div>
                <div class="memory-content">${memory.content}</div>
                <div class="memory-tags">
                    ${memory.tags.map(tag => `<span class="memory-tag">${tag}</span>`).join('')}
                </div>
            `;
            memoryList.appendChild(memoryItem);
        });
    }
    
    searchMemories(query) {
        if (this.isConnected) {
            this.ws.send(JSON.stringify({
                type: 'search_memories',
                query: query
            }));
        }
    }
    
    filterMemories(filter) {
        if (this.isConnected) {
            this.ws.send(JSON.stringify({
                type: 'filter_memories',
                filter: filter
            }));
        }
    }
    
    clearChat() {
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.innerHTML = `
            <div class="message system-message">
                <div class="message-avatar">
                    <i class="fas fa-brain"></i>
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="sender">MIA</span>
                        <span class="timestamp">Just now</span>
                    </div>
                    <div class="message-text">
                        Chat cleared. How can I help you today?
                    </div>
                </div>
            </div>
        `;
    }
    
    exportChat() {
        const messages = document.querySelectorAll('.message');
        let chatText = 'MIA Chat Export\n';
        chatText += '='.repeat(50) + '\n\n';
        
        messages.forEach(message => {
            const sender = message.querySelector('.sender').textContent;
            const timestamp = message.querySelector('.timestamp').textContent;
            const content = message.querySelector('.message-text').textContent;
            
            chatText += `[${timestamp}] ${sender}: ${content}\n\n`;
        });
        
        const blob = new Blob([chatText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `mia-chat-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    toggleVoice() {
        // Voice functionality would be implemented here
        this.showNotification('Voice feature coming soon', 'info');
    }
    
    openFileDialog() {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = '*/*';
        
        input.onchange = (e) => {
            const files = Array.from(e.target.files);
            this.handleFileUpload(files);
        };
        
        input.click();
    }
    
    handleFileUpload(files) {
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                this.ws.send(JSON.stringify({
                    type: 'file_upload',
                    filename: file.name,
                    content: e.target.result,
                    type: file.type
                }));
            };
            reader.readAsDataURL(file);
        });
        
        this.showNotification(`Uploading ${files.length} file(s)`, 'info');
    }
    
    downloadImage(imagePath) {
        const a = document.createElement('a');
        a.href = imagePath;
        a.download = imagePath.split('/').pop();
        a.click();
    }
    
    shareImage(imagePath) {
        if (navigator.share) {
            navigator.share({
                title: 'MIA Generated Image',
                url: imagePath
            });
        } else {
            navigator.clipboard.writeText(window.location.origin + imagePath);
            this.showNotification('Image URL copied to clipboard', 'success');
        }
    }
    
    loadEvolutionStatus() {
        if (this.isConnected) {
            this.ws.send(JSON.stringify({ type: 'get_evolution_status' }));
        }
    }
    
    loadLearningDashboard() {
        if (this.isConnected) {
            this.ws.send(JSON.stringify({ type: 'get_learning_status' }));
        }
    }
}

// Initialize the interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.miaInterface = new MIAInterface();
});

// Handle keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus chat input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('chat-input').focus();
    }
    
    // Ctrl/Cmd + / to toggle theme
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        window.miaInterface.toggleTheme();
    }
    
    // Escape to close modal
    if (e.key === 'Escape') {
        window.miaInterface.closeModal();
    }
});