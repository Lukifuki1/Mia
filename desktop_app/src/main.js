const { app, BrowserWindow, Menu, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const WebSocket = require('ws');

class MIADesktopApp {
    constructor() {
        this.mainWindow = null;
        this.miaProcess = null;
        this.expressApp = null;
        this.httpServer = null;
        this.socketServer = null;
        this.wsServer = null;
        this.serverPort = 12000;
        this.wsPort = 12001;
        
        this.isDev = process.argv.includes('--dev');
        this.resourcesPath = this.isDev ? path.join(__dirname, '../../..') : process.resourcesPath;
        this.miaPath = path.join(this.resourcesPath, 'mia');
        
        this.setupApp();
    }
    
    setupApp() {
        // App event handlers
        app.whenReady().then(() => {
            this.createMainWindow();
            this.setupMenu();
            this.startMIABackend();
            this.setupIPC();
            
            app.on('activate', () => {
                if (BrowserWindow.getAllWindows().length === 0) {
                    this.createMainWindow();
                }
            });
        });
        
        app.on('window-all-closed', () => {
            this.cleanup();
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });
        
        app.on('before-quit', () => {
            this.cleanup();
        });
    }
    
    createMainWindow() {
        this.mainWindow = new BrowserWindow({
            width: 1400,
            height: 900,
            minWidth: 1200,
            minHeight: 800,
            icon: path.join(__dirname, '../assets/icon.png'),
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                preload: path.join(__dirname, 'preload.js'),
                webSecurity: !this.isDev
            },
            titleBarStyle: 'default',
            show: false
        });
        
        // Load the app
        if (this.isDev) {
            this.mainWindow.loadURL('http://localhost:12002');
            this.mainWindow.webContents.openDevTools();
        } else {
            this.mainWindow.loadURL('http://localhost:12002');
        }
        
        // Show window when ready
        this.mainWindow.once('ready-to-show', () => {
            this.mainWindow.show();
            this.showSplashScreen();
        });
        
        // Handle window closed
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });
        
        // Handle external links
        this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
            shell.openExternal(url);
            return { action: 'deny' };
        });
    }
    
    setupMenu() {
        const template = [
            {
                label: 'MIA',
                submenu: [
                    {
                        label: 'About MIA Enterprise AGI',
                        click: () => this.showAboutDialog()
                    },
                    { type: 'separator' },
                    {
                        label: 'Preferences',
                        accelerator: 'CmdOrCtrl+,',
                        click: () => this.showPreferences()
                    },
                    { type: 'separator' },
                    {
                        label: 'Restart MIA',
                        click: () => this.restartMIA()
                    },
                    {
                        label: 'Stop MIA',
                        click: () => this.stopMIA()
                    },
                    { type: 'separator' },
                    {
                        label: 'Quit',
                        accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                        click: () => app.quit()
                    }
                ]
            },
            {
                label: 'Edit',
                submenu: [
                    { role: 'undo' },
                    { role: 'redo' },
                    { type: 'separator' },
                    { role: 'cut' },
                    { role: 'copy' },
                    { role: 'paste' },
                    { role: 'selectall' }
                ]
            },
            {
                label: 'View',
                submenu: [
                    { role: 'reload' },
                    { role: 'forceReload' },
                    { role: 'toggleDevTools' },
                    { type: 'separator' },
                    { role: 'resetZoom' },
                    { role: 'zoomIn' },
                    { role: 'zoomOut' },
                    { type: 'separator' },
                    { role: 'togglefullscreen' }
                ]
            },
            {
                label: 'Tools',
                submenu: [
                    {
                        label: 'Project Builder',
                        click: () => this.openProjectBuilder()
                    },
                    {
                        label: 'Memory Explorer',
                        click: () => this.openMemoryExplorer()
                    },
                    {
                        label: 'System Monitor',
                        click: () => this.openSystemMonitor()
                    },
                    {
                        label: 'LoRA Manager',
                        click: () => this.openLoRAManager()
                    },
                    { type: 'separator' },
                    {
                        label: 'Developer Mode',
                        type: 'checkbox',
                        checked: this.isDev,
                        click: () => this.toggleDeveloperMode()
                    }
                ]
            },
            {
                label: 'Help',
                submenu: [
                    {
                        label: 'Documentation',
                        click: () => shell.openExternal('https://github.com/mia-enterprise-agi/docs')
                    },
                    {
                        label: 'Report Issue',
                        click: () => shell.openExternal('https://github.com/mia-enterprise-agi/issues')
                    },
                    { type: 'separator' },
                    {
                        label: 'System Information',
                        click: () => this.showSystemInfo()
                    }
                ]
            }
        ];
        
        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }
    
    setupIPC() {
        // Handle MIA status requests
        ipcMain.handle('get-mia-status', async () => {
            return this.getMIAStatus();
        });
        
        // Handle MIA commands
        ipcMain.handle('send-mia-command', async (event, command) => {
            return this.sendMIACommand(command);
        });
        
        // Handle file operations
        ipcMain.handle('select-file', async () => {
            const result = await dialog.showOpenDialog(this.mainWindow, {
                properties: ['openFile'],
                filters: [
                    { name: 'All Files', extensions: ['*'] }
                ]
            });
            return result;
        });
        
        // Handle directory operations
        ipcMain.handle('select-directory', async () => {
            const result = await dialog.showOpenDialog(this.mainWindow, {
                properties: ['openDirectory']
            });
            return result;
        });
        
        // Handle save operations
        ipcMain.handle('save-file', async (event, data) => {
            const result = await dialog.showSaveDialog(this.mainWindow, {
                filters: [
                    { name: 'JSON Files', extensions: ['json'] },
                    { name: 'Text Files', extensions: ['txt'] },
                    { name: 'All Files', extensions: ['*'] }
                ]
            });
            
            if (!result.canceled) {
                fs.writeFileSync(result.filePath, data);
                return { success: true, path: result.filePath };
            }
            
            return { success: false };
        });
    }
    
    async startMIABackend() {
        try {
            console.log('Starting MIA backend...');
            
            // Setup Express server for UI
            this.setupExpressServer();
            
            // Setup WebSocket server for real-time communication
            this.setupWebSocketServer();
            
            // Start MIA Python backend
            await this.startMIAPythonProcess();
            
            console.log('MIA backend started successfully');
            
        } catch (error) {
            console.error('Failed to start MIA backend:', error);
            this.showErrorDialog('Failed to start MIA backend', error.message);
        }
    }
    
    setupExpressServer() {
        this.expressApp = express();
        this.httpServer = http.createServer(this.expressApp);
        
        // Serve static files
        this.expressApp.use(express.static(path.join(__dirname, 'ui')));
        this.expressApp.use(express.json());
        
        // API routes
        this.expressApp.get('/api/status', (req, res) => {
            res.json(this.getMIAStatus());
        });
        
        this.expressApp.post('/api/command', (req, res) => {
            const result = this.sendMIACommand(req.body.command);
            res.json(result);
        });
        
        // Serve main UI
        this.expressApp.get('/', (req, res) => {
            res.sendFile(path.join(__dirname, 'ui', 'index.html'));
        });
        
        // Setup Socket.IO
        this.socketServer = socketIo(this.httpServer, {
            cors: {
                origin: "*",
                methods: ["GET", "POST"]
            }
        });
        
        this.socketServer.on('connection', (socket) => {
            console.log('Client connected to Socket.IO');
            
            socket.on('mia-command', (command) => {
                const result = this.sendMIACommand(command);
                socket.emit('mia-response', result);
            });
            
            socket.on('disconnect', () => {
                console.log('Client disconnected from Socket.IO');
            });
        });
        
        // Start server
        this.httpServer.listen(this.serverPort, () => {
            console.log(`Express server running on port ${this.serverPort}`);
        });
    }
    
    setupWebSocketServer() {
        this.wsServer = new WebSocket.Server({ port: this.wsPort });
        
        this.wsServer.on('connection', (ws) => {
            console.log('WebSocket client connected');
            
            ws.on('message', (message) => {
                try {
                    const data = JSON.parse(message);
                    const result = this.sendMIACommand(data.command);
                    ws.send(JSON.stringify(result));
                } catch (error) {
                    ws.send(JSON.stringify({ error: error.message }));
                }
            });
            
            ws.on('close', () => {
                console.log('WebSocket client disconnected');
            });
        });
        
        console.log(`WebSocket server running on port ${this.wsPort}`);
    }
    
    async startMIAPythonProcess() {
        return new Promise((resolve, reject) => {
            const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';
            const miaLauncher = path.join(this.resourcesPath, 'mia_real_agi_chat.py');
            
            console.log(`Starting MIA Real AGI process: ${pythonExecutable} ${miaLauncher}`);
            
            this.miaProcess = spawn(pythonExecutable, [miaLauncher], {
                cwd: this.resourcesPath,
                stdio: ['pipe', 'pipe', 'pipe'],
                env: {
                    ...process.env,
                    PYTHONPATH: this.resourcesPath,
                    MIA_DESKTOP_MODE: 'true'
                }
            });
            
            this.miaProcess.stdout.on('data', (data) => {
                console.log(`MIA stdout: ${data}`);
                this.broadcastMIAOutput(data.toString());
            });
            
            this.miaProcess.stderr.on('data', (data) => {
                console.error(`MIA stderr: ${data}`);
                this.broadcastMIAOutput(data.toString(), 'error');
            });
            
            this.miaProcess.on('close', (code) => {
                console.log(`MIA process exited with code ${code}`);
                if (code !== 0) {
                    reject(new Error(`MIA process exited with code ${code}`));
                }
            });
            
            this.miaProcess.on('error', (error) => {
                console.error('MIA process error:', error);
                reject(error);
            });
            
            // Wait for MIA to start
            setTimeout(() => {
                if (this.miaProcess && !this.miaProcess.killed) {
                    resolve();
                } else {
                    reject(new Error('MIA process failed to start'));
                }
            }, 5000);
        });
    }
    
    broadcastMIAOutput(output, type = 'info') {
        // Broadcast to Socket.IO clients
        if (this.socketServer) {
            this.socketServer.emit('mia-output', { output, type, timestamp: Date.now() });
        }
        
        // Broadcast to WebSocket clients
        if (this.wsServer) {
            this.wsServer.clients.forEach((client) => {
                if (client.readyState === WebSocket.OPEN) {
                    client.send(JSON.stringify({ 
                        type: 'output', 
                        data: { output, type, timestamp: Date.now() }
                    }));
                }
            });
        }
    }
    
    getMIAStatus() {
        return {
            running: this.miaProcess && !this.miaProcess.killed,
            pid: this.miaProcess ? this.miaProcess.pid : null,
            uptime: this.miaProcess ? Date.now() - this.miaProcess.spawnTime : 0,
            version: '2.0.0',
            mode: 'desktop'
        };
    }
    
    sendMIACommand(command) {
        try {
            if (!this.miaProcess || this.miaProcess.killed) {
                return { success: false, error: 'MIA process not running' };
            }
            
            this.miaProcess.stdin.write(JSON.stringify(command) + '\n');
            return { success: true };
            
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    showSplashScreen() {
        // Show splash screen with MIA logo and loading animation
        if (this.mainWindow) {
            this.mainWindow.webContents.executeJavaScript(`
                if (window.showSplashScreen) {
                    window.showSplashScreen();
                }
            `);
        }
    }
    
    showAboutDialog() {
        dialog.showMessageBox(this.mainWindow, {
            type: 'info',
            title: 'About MIA Enterprise AGI',
            message: 'MIA Enterprise AGI v2.0.0',
            detail: 'Local Digital Intelligence Entity\\n\\nMIA is a fully autonomous, local AGI system with consciousness, memory, and enterprise capabilities.\\n\\nCopyright © 2024 MIA Enterprise AGI Team',
            buttons: ['OK']
        });
    }
    
    showPreferences() {
        // Open preferences window
        if (this.mainWindow) {
            this.mainWindow.webContents.executeJavaScript(`
                if (window.openPreferences) {
                    window.openPreferences();
                }
            `);
        }
    }
    
    showSystemInfo() {
        const systemInfo = {
            platform: process.platform,
            arch: process.arch,
            nodeVersion: process.version,
            electronVersion: process.versions.electron,
            chromeVersion: process.versions.chrome,
            miaVersion: '2.0.0'
        };
        
        dialog.showMessageBox(this.mainWindow, {
            type: 'info',
            title: 'System Information',
            message: 'MIA Enterprise AGI System Information',
            detail: Object.entries(systemInfo)
                .map(([key, value]) => `${key}: ${value}`)
                .join('\\n'),
            buttons: ['OK']
        });
    }
    
    showErrorDialog(title, message) {
        dialog.showErrorBox(title, message);
    }
    
    restartMIA() {
        this.stopMIA();
        setTimeout(() => {
            this.startMIABackend();
        }, 2000);
    }
    
    stopMIA() {
        if (this.miaProcess && !this.miaProcess.killed) {
            this.miaProcess.kill('SIGTERM');
            this.miaProcess = null;
        }
    }
    
    openProjectBuilder() {
        if (this.mainWindow) {
            this.mainWindow.webContents.executeJavaScript(`
                if (window.openProjectBuilder) {
                    window.openProjectBuilder();
                }
            `);
        }
    }
    
    openMemoryExplorer() {
        if (this.mainWindow) {
            this.mainWindow.webContents.executeJavaScript(`
                if (window.openMemoryExplorer) {
                    window.openMemoryExplorer();
                }
            `);
        }
    }
    
    openSystemMonitor() {
        if (this.mainWindow) {
            this.mainWindow.webContents.executeJavaScript(`
                if (window.openSystemMonitor) {
                    window.openSystemMonitor();
                }
            `);
        }
    }
    
    openLoRAManager() {
        if (this.mainWindow) {
            this.mainWindow.webContents.executeJavaScript(`
                if (window.openLoRAManager) {
                    window.openLoRAManager();
                }
            `);
        }
    }
    
    toggleDeveloperMode() {
        this.isDev = !this.isDev;
        if (this.isDev) {
            this.mainWindow.webContents.openDevTools();
        } else {
            this.mainWindow.webContents.closeDevTools();
        }
    }
    
    cleanup() {
        console.log('Cleaning up MIA Desktop App...');
        
        // Stop MIA process
        this.stopMIA();
        
        // Close servers
        if (this.httpServer) {
            this.httpServer.close();
        }
        
        if (this.wsServer) {
            this.wsServer.close();
        }
        
        console.log('Cleanup completed');
    }
}

// Create and start the app
new MIADesktopApp();