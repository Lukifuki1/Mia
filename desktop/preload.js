const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // App info
    getAppInfo: () => ipcRenderer.invoke('get-app-info'),
    getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
    
    // Dialog methods
    showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
    showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
    showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
    openExternal: (url) => ipcRenderer.invoke('open-external', url),
    
    // Store methods
    getStoreValue: (key, defaultValue) => ipcRenderer.invoke('get-store-value', key, defaultValue),
    setStoreValue: (key, value) => ipcRenderer.invoke('set-store-value', key, value),
    
    // App control
    restartApp: () => ipcRenderer.invoke('restart-app'),
    quitApp: () => ipcRenderer.invoke('quit-app'),
    
    // Navigation
    onNavigateTo: (callback) => ipcRenderer.on('navigate-to', callback),
    onMenuAction: (callback) => ipcRenderer.on('menu-action', callback),
    
    // Remove listeners
    removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});

// MIA API Bridge
contextBridge.exposeInMainWorld('miaAPI', {
    // Backend communication
    sendCommand: async (command, data) => {
        try {
            const response = await fetch(`http://localhost:8000/api/command`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command, data })
            });
            return await response.json();
        } catch (error) {
            console.error('MIA API Error:', error);
            throw error;
        }
    },
    
    // Real-time updates
    onSystemUpdate: (callback) => {
        // WebSocket connection for real-time updates
        const ws = new WebSocket('ws://localhost:8000/ws');
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            callback(data);
        };
        return ws;
    },
    
    // File operations
    readFile: async (filePath) => {
        const response = await fetch(`http://localhost:8000/api/file/read`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: filePath })
        });
        return await response.json();
    },
    
    writeFile: async (filePath, content) => {
        const response = await fetch(`http://localhost:8000/api/file/write`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: filePath, content })
        });
        return await response.json();
    },
    
    // System monitoring
    getSystemStatus: async () => {
        const response = await fetch('http://localhost:8000/api/system/status');
        return await response.json();
    },
    
    // MIA consciousness
    queryConsciousness: async (query) => {
        const response = await fetch('http://localhost:8000/api/consciousness/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        return await response.json();
    },
    
    // Memory operations
    storeMemory: async (content, type = 'short_term') => {
        const response = await fetch('http://localhost:8000/api/memory/store', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content, type })
        });
        return await response.json();
    },
    
    queryMemory: async (query, limit = 10) => {
        const response = await fetch('http://localhost:8000/api/memory/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, limit })
        });
        return await response.json();
    },
    
    // Project management
    createProject: async (projectData) => {
        const response = await fetch('http://localhost:8000/api/project/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(projectData)
        });
        return await response.json();
    },
    
    getProjects: async () => {
        const response = await fetch('http://localhost:8000/api/project/list');
        return await response.json();
    },
    
    // Multimodal generation
    generateImage: async (prompt, options = {}) => {
        const response = await fetch('http://localhost:8000/api/generate/image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, ...options })
        });
        return await response.json();
    },
    
    generateVideo: async (prompt, options = {}) => {
        const response = await fetch('http://localhost:8000/api/generate/video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, ...options })
        });
        return await response.json();
    },
    
    generateAudio: async (prompt, options = {}) => {
        const response = await fetch('http://localhost:8000/api/generate/audio', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, ...options })
        });
        return await response.json();
    }
});

// Platform detection
contextBridge.exposeInMainWorld('platform', {
    isWindows: process.platform === 'win32',
    isMacOS: process.platform === 'darwin',
    isLinux: process.platform === 'linux',
    arch: process.arch,
    version: process.version
});

// Security utilities
contextBridge.exposeInMainWorld('security', {
    sanitizeHTML: (html) => {
        // Basic HTML sanitization
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    },
    
    validateURL: (url) => {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }
});

console.log('🔗 Preload script loaded successfully');
