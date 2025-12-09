// MIA Enterprise AGI Desktop Application
class MIADesktopApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.systemStatus = 'initializing';
        this.init();
    }
    
    async init() {
        console.log('🚀 Initializing MIA Desktop App...');
        
        // Setup navigation
        this.setupNavigation();
        
        // Setup generation tabs
        this.setupGenerationTabs();
        
        // Load app info
        await this.loadAppInfo();
        
        // Start system monitoring
        this.startSystemMonitoring();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize pages
        await this.initializeDashboard();
        
        console.log('✅ MIA Desktop App initialized');
    }
    
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                this.navigateToPage(page);
            });
        });
    }
    
    navigateToPage(page) {
        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('active');
        
        // Show page
        document.querySelectorAll('.page').forEach(p => {
            p.classList.remove('active');
        });
        document.getElementById(page).classList.add('active');
        
        this.currentPage = page;
        
        // Initialize page if needed
        this.initializePage(page);
    }
    
    async initializePage(page) {
        switch(page) {
            case 'dashboard':
                await this.initializeDashboard();
                break;
            case 'projects':
                await this.loadProjects();
                break;
            case 'monitor':
                await this.updateSystemMonitor();
                break;
        }
    }
    
    setupGenerationTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tab = button.dataset.tab;
                
                // Update active tab button
                tabButtons.forEach(b => b.classList.remove('active'));
                button.classList.add('active');
                
                // Show tab content
                document.querySelectorAll('.gen-tab').forEach(t => {
                    t.classList.remove('active');
                });
                document.getElementById(`${tab}-gen`).classList.add('active');
            });
        });
    }
    
    async loadAppInfo() {
        try {
            if (window.electronAPI) {
                const appInfo = await window.electronAPI.getAppInfo();
                document.getElementById('app-info').innerHTML = `
                    <p><strong>Version:</strong> ${appInfo.version}</p>
                    <p><strong>Platform:</strong> ${appInfo.platform}</p>
                    <p><strong>Architecture:</strong> ${appInfo.arch}</p>
                    <p><strong>Electron:</strong> ${appInfo.electron}</p>
                `;
            }
        } catch (error) {
            console.error('Failed to load app info:', error);
        }
    }
    
    async initializeDashboard() {
        try {
            // Update system status
            this.updateSystemStatus('operational');
            
            // Load system info
            if (window.electronAPI) {
                const systemInfo = await window.electronAPI.getSystemInfo();
                if (systemInfo) {
                    document.getElementById('system-info').innerHTML = `
                        <p><strong>CPU:</strong> ${systemInfo.cpu.brand}</p>
                        <p><strong>Cores:</strong> ${systemInfo.cpu.cores}</p>
                        <p><strong>Memory:</strong> ${(systemInfo.memory.total / 1024 / 1024 / 1024).toFixed(1)} GB</p>
                        <p><strong>OS:</strong> ${systemInfo.os.distro}</p>
                    `;
                }
            }
            
            // Load performance metrics
            await this.updatePerformanceMetrics();
            
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
        }
    }
    
    async updatePerformanceMetrics() {
        try {
            if (window.miaAPI) {
                const status = await window.miaAPI.getSystemStatus();
                document.getElementById('performance-metrics').innerHTML = `
                    <p><strong>CPU:</strong> ${status.cpu_usage || 0}%</p>
                    <p><strong>Memory:</strong> ${status.memory_usage || 0}%</p>
                    <p><strong>Uptime:</strong> ${status.uptime || '0s'}</p>
                `;
            }
        } catch (error) {
            console.error('Failed to update performance metrics:', error);
            document.getElementById('performance-metrics').innerHTML = '<p>Performance data unavailable</p>';
        }
    }
    
    updateSystemStatus(status) {
        this.systemStatus = status;
        const indicator = document.getElementById('status-indicator');
        const text = document.getElementById('status-text');
        
        switch(status) {
            case 'operational':
                indicator.style.background = '#4CAF50';
                text.textContent = 'Operational';
                break;
            case 'warning':
                indicator.style.background = '#FF9800';
                text.textContent = 'Warning';
                break;
            case 'error':
                indicator.style.background = '#F44336';
                text.textContent = 'Error';
                break;
            default:
                indicator.style.background = '#2196F3';
                text.textContent = 'Initializing';
        }
    }
    
    startSystemMonitoring() {
        // Update system status every 5 seconds
        setInterval(async () => {
            if (this.currentPage === 'dashboard') {
                await this.updatePerformanceMetrics();
            }
            if (this.currentPage === 'monitor') {
                await this.updateSystemMonitor();
            }
        }, 5000);
    }
    
    async updateSystemMonitor() {
        try {
            if (window.miaAPI) {
                const status = await window.miaAPI.getSystemStatus();
                document.getElementById('cpu-usage').textContent = `${status.cpu_usage || 0}%`;
                document.getElementById('memory-usage').textContent = `${status.memory_usage || 0}%`;
                document.getElementById('gpu-usage').textContent = `${status.gpu_usage || 0}%`;
                document.getElementById('network-usage').textContent = `${status.network_usage || 0} KB/s`;
            }
        } catch (error) {
            console.error('Failed to update system monitor:', error);
        }
    }
    
    setupEventListeners() {
        // Chat input
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }
        
        // Settings
        const startOnBoot = document.getElementById('start-on-boot');
        const minimizeToTray = document.getElementById('minimize-to-tray');
        
        if (startOnBoot && window.electronAPI) {
            startOnBoot.addEventListener('change', async (e) => {
                await window.electronAPI.setStoreValue('startOnBoot', e.target.checked);
            });
        }
        
        if (minimizeToTray && window.electronAPI) {
            minimizeToTray.addEventListener('change', async (e) => {
                await window.electronAPI.setStoreValue('minimizeToTray', e.target.checked);
            });
        }
        
        // Listen for navigation events from main process
        if (window.electronAPI) {
            window.electronAPI.onNavigateTo((event, page) => {
                this.navigateToPage(page.replace('/', ''));
            });
        }
    }
    
    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;
        
        // Add message to chat
        this.addChatMessage('user', message);
        input.value = '';
        
        try {
            if (window.miaAPI) {
                const response = await window.miaAPI.queryConsciousness(message);
                this.addChatMessage('mia', response.response || 'I understand your message.');
            } else {
                this.addChatMessage('mia', 'MIA backend is not available. Please check the connection.');
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.addChatMessage('mia', 'Sorry, I encountered an error processing your message.');
        }
    }
    
    addChatMessage(sender, message) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        messageDiv.innerHTML = `
            <div class="message-header">
                <strong>${sender === 'user' ? 'You' : 'MIA'}</strong>
                <span class="timestamp">${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="message-content">${message}</div>
        `;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    async loadProjects() {
        try {
            if (window.miaAPI) {
                const projects = await window.miaAPI.getProjects();
                const projectsList = document.getElementById('projects-list');
                
                if (projects && projects.length > 0) {
                    projectsList.innerHTML = projects.map(project => `
                        <div class="project-card">
                            <h3>${project.name}</h3>
                            <p>${project.description}</p>
                            <div class="project-actions">
                                <button onclick="openProject('${project.id}')">Open</button>
                                <button onclick="deleteProject('${project.id}')">Delete</button>
                            </div>
                        </div>
                    `).join('');
                } else {
                    projectsList.innerHTML = '<p>No projects yet. Create your first project!</p>';
                }
            }
        } catch (error) {
            console.error('Failed to load projects:', error);
        }
    }
}

// Global functions
async function startNewChat() {
    app.navigateToPage('chat');
}

async function createProject() {
    app.navigateToPage('projects');
}

async function generateContent() {
    app.navigateToPage('generate');
}

async function createNewProject() {
    const name = prompt('Project name:');
    if (name && window.miaAPI) {
        try {
            await window.miaAPI.createProject({ name, description: 'New project' });
            await app.loadProjects();
        } catch (error) {
            console.error('Failed to create project:', error);
        }
    }
}

async function generateImage() {
    const prompt = document.getElementById('image-prompt').value;
    if (!prompt) return;
    
    const resultDiv = document.getElementById('image-result');
    resultDiv.innerHTML = '<p>Generating image...</p>';
    
    try {
        if (window.miaAPI) {
            const result = await window.miaAPI.generateImage(prompt);
            resultDiv.innerHTML = `<img src="${result.image_url}" alt="Generated image" style="max-width: 100%; border-radius: 8px;">`;
        }
    } catch (error) {
        console.error('Image generation error:', error);
        resultDiv.innerHTML = '<p>Failed to generate image.</p>';
    }
}

async function generateVideo() {
    const prompt = document.getElementById('video-prompt').value;
    if (!prompt) return;
    
    const resultDiv = document.getElementById('video-result');
    resultDiv.innerHTML = '<p>Generating video...</p>';
    
    try {
        if (window.miaAPI) {
            const result = await window.miaAPI.generateVideo(prompt);
            resultDiv.innerHTML = `<video controls style="max-width: 100%; border-radius: 8px;"><source src="${result.video_url}" type="video/mp4"></video>`;
        }
    } catch (error) {
        console.error('Video generation error:', error);
        resultDiv.innerHTML = '<p>Failed to generate video.</p>';
    }
}

async function generateAudio() {
    const prompt = document.getElementById('audio-prompt').value;
    if (!prompt) return;
    
    const resultDiv = document.getElementById('audio-result');
    resultDiv.innerHTML = '<p>Generating audio...</p>';
    
    try {
        if (window.miaAPI) {
            const result = await window.miaAPI.generateAudio(prompt);
            resultDiv.innerHTML = `<audio controls style="width: 100%;"><source src="${result.audio_url}" type="audio/wav"></audio>`;
        }
    } catch (error) {
        console.error('Audio generation error:', error);
        resultDiv.innerHTML = '<p>Failed to generate audio.</p>';
    }
}

async function searchMemories() {
    const query = document.getElementById('memory-search').value;
    if (!query) return;
    
    const resultsDiv = document.getElementById('memory-results');
    resultsDiv.innerHTML = '<p>Searching memories...</p>';
    
    try {
        if (window.miaAPI) {
            const results = await window.miaAPI.queryMemory(query);
            if (results && results.length > 0) {
                resultsDiv.innerHTML = results.map(memory => `
                    <div class="memory-item">
                        <div class="memory-content">${memory.content}</div>
                        <div class="memory-meta">
                            <span>Type: ${memory.type}</span>
                            <span>Score: ${memory.score}</span>
                            <span>Date: ${new Date(memory.timestamp).toLocaleDateString()}</span>
                        </div>
                    </div>
                `).join('');
            } else {
                resultsDiv.innerHTML = '<p>No memories found for this query.</p>';
            }
        }
    } catch (error) {
        console.error('Memory search error:', error);
        resultsDiv.innerHTML = '<p>Failed to search memories.</p>';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MIADesktopApp();
});

console.log('🖥️ MIA Desktop App script loaded');
