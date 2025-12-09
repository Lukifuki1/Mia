const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // MIA operations
    getMIAStatus: () => ipcRenderer.invoke('get-mia-status'),
    sendMIACommand: (command) => ipcRenderer.invoke('send-mia-command', command),
    
    // File operations
    selectFile: () => ipcRenderer.invoke('select-file'),
    selectDirectory: () => ipcRenderer.invoke('select-directory'),
    saveFile: (data) => ipcRenderer.invoke('save-file', data),
    
    // Event listeners
    onMIAOutput: (callback) => {
        ipcRenderer.on('mia-output', callback);
    },
    
    removeMIAOutputListener: (callback) => {
        ipcRenderer.removeListener('mia-output', callback);
    },
    
    // System information
    platform: process.platform,
    versions: process.versions
});

// Expose MIA-specific APIs
contextBridge.exposeInMainWorld('miaAPI', {
    // Project Builder
    createProject: (projectData) => ipcRenderer.invoke('create-project', projectData),
    buildProject: (projectId) => ipcRenderer.invoke('build-project', projectId),
    exportProject: (projectId, format) => ipcRenderer.invoke('export-project', projectId, format),
    
    // Memory Explorer
    getMemories: (filters) => ipcRenderer.invoke('get-memories', filters),
    searchMemories: (query) => ipcRenderer.invoke('search-memories', query),
    
    // System Monitor
    getSystemMetrics: () => ipcRenderer.invoke('get-system-metrics'),
    getComponentStatus: () => ipcRenderer.invoke('get-component-status'),
    
    // LoRA Manager
    getLoRAModels: () => ipcRenderer.invoke('get-lora-models'),
    trainLoRA: (config) => ipcRenderer.invoke('train-lora', config),
    activateLoRA: (modelId) => ipcRenderer.invoke('activate-lora', modelId),
    
    // Voice System
    startListening: () => ipcRenderer.invoke('start-listening'),
    stopListening: () => ipcRenderer.invoke('stop-listening'),
    speak: (text, options) => ipcRenderer.invoke('speak', text, options),
    
    // Avatar System
    setEmotionalState: (state, intensity) => ipcRenderer.invoke('set-emotional-state', state, intensity),
    setAvatarMode: (mode) => ipcRenderer.invoke('set-avatar-mode', mode),
    
    // Adult Mode
    activateAdultMode: (phrase) => ipcRenderer.invoke('activate-adult-mode', phrase),
    startAdultSession: (options) => ipcRenderer.invoke('start-adult-session', options),
    endAdultSession: () => ipcRenderer.invoke('end-adult-session'),
    
    // Configuration
    getConfig: () => ipcRenderer.invoke('get-config'),
    updateConfig: (config) => ipcRenderer.invoke('update-config', config),
    
    // Logs
    getLogs: (level, limit) => ipcRenderer.invoke('get-logs', level, limit),
    
    // Real-time events
    onStatusUpdate: (callback) => {
        ipcRenderer.on('status-update', callback);
    },
    
    onProgressUpdate: (callback) => {
        ipcRenderer.on('progress-update', callback);
    },
    
    onError: (callback) => {
        ipcRenderer.on('error', callback);
    },
    
    // Remove listeners
    removeAllListeners: () => {
        ipcRenderer.removeAllListeners('status-update');
        ipcRenderer.removeAllListeners('progress-update');
        ipcRenderer.removeAllListeners('error');
        ipcRenderer.removeAllListeners('mia-output');
    }
});

// Expose utility functions
contextBridge.exposeInMainWorld('utils', {
    formatBytes: (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    formatDuration: (seconds) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    },
    
    formatTimestamp: (timestamp) => {
        return new Date(timestamp).toLocaleString();
    },
    
    generateId: () => {
        return Math.random().toString(36).substr(2, 9);
    }
});

// Security: Remove Node.js globals from renderer process
delete window.require;
delete window.exports;
delete window.module;