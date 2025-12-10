const { app, BrowserWindow, Menu, Tray, ipcMain, dialog, shell, protocol, session } = require('electron');
const { autoUpdater } = require('electron-updater');
const windowStateKeeper = require('electron-window-state');
const Store = require('electron-store');
const path = require('path');
const os = require('os');
const fs = require('fs');
const express = require('express');
const { spawn } = require('child_process');
const si = require('systeminformation');
const notifier = require('node-notifier');
const AutoLaunch = require('auto-launch');

// Initialize store
const store = new Store();

// Global variables
let mainWindow;
let tray;
let backendProcess;
let expressApp;
let expressServer;
let isQuitting = false;

// Auto-launcher
const autoLauncher = new AutoLaunch({
    name: 'MIA Enterprise AGI',
    path: app.getPath('exe')
});

// App configuration
const APP_CONFIG = {
    name: 'MIA Enterprise AGI',
    version: app.getVersion(),
    backend_port: 8000,
    frontend_port: 12000,
    desktop_port: 12001,
    python_executable: process.platform === 'win32' ? 'python.exe' : 'python3',
    backend_script: 'mia_enterprise_agi.py'
};

// Security configuration
app.commandLine.appendSwitch('--disable-web-security');
app.commandLine.appendSwitch('--disable-features', 'VizDisplayCompositor');

// Protocol handler
protocol.registerSchemesAsPrivileged([
    { scheme: 'mia', privileges: { secure: true, standard: true } }
]);

// App event handlers
app.whenReady().then(async () => {
    await initializeApp();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createMainWindow();
    }
});

app.on('before-quit', (event) => {
    if (!isQuitting) {
        event.preventDefault();
        gracefulShutdown();
    }
});

// Initialize application
async function initializeApp() {
    try {
        console.log('🚀 Initializing MIA Enterprise AGI...');
        
        // Set app user model ID for Windows
        if (process.platform === 'win32') {
            app.setAppUserModelId('com.mia-enterprise.agi');
        }
        
        // Create main window
        await createMainWindow();
        
        // Create system tray
        createSystemTray();
        
        // Start backend services
        await startBackendServices();
        
        // Setup auto-updater
        setupAutoUpdater();
        
        // Setup IPC handlers
        setupIpcHandlers();
        
        // Setup menu
        createApplicationMenu();
        
        // Check for updates
        if (!app.isPackaged) {
            console.log('Development mode - skipping auto-updater');
        } else {
            autoUpdater.checkForUpdatesAndNotify();
        }
        
        console.log('✅ MIA Enterprise AGI initialized successfully');
        
    } catch (error) {
        console.error('❌ Failed to initialize app:', error);
        showErrorDialog('Initialization Error', error.message);
    }
}

// Create main window
async function createMainWindow() {
    try {
        // Load window state
        let mainWindowState = windowStateKeeper({
            defaultWidth: 1400,
            defaultHeight: 900
        });
        
        // Create window
        mainWindow = new BrowserWindow({
            x: mainWindowState.x,
            y: mainWindowState.y,
            width: mainWindowState.width,
            height: mainWindowState.height,
            minWidth: 1000,
            minHeight: 700,
            show: false,
            icon: getIconPath(),
            titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                preload: path.join(__dirname, 'preload.js'),
                webSecurity: false,
                allowRunningInsecureContent: true
            }
        });
        
        // Manage window state
        mainWindowState.manage(mainWindow);
        
        // Window event handlers
        mainWindow.once('ready-to-show', () => {
            mainWindow.show();
            
            if (store.get('startMaximized', false)) {
                mainWindow.maximize();
            }
            
            // Focus window
            if (process.platform === 'darwin') {
                app.dock.show();
            }
        });
        
        mainWindow.on('close', (event) => {
            if (!isQuitting && store.get('minimizeToTray', true)) {
                event.preventDefault();
                mainWindow.hide();
                
                if (process.platform === 'darwin') {
                    app.dock.hide();
                }
                
                showNotification('MIA Enterprise AGI', 'Application minimized to system tray');
            }
        });
        
        mainWindow.on('closed', () => {
            mainWindow = null;
        });
        
        // Load application
        const startUrl = `http://localhost:${APP_CONFIG.frontend_port}`;
        await mainWindow.loadURL(startUrl);
        
        // Development tools
        if (!app.isPackaged) {
            mainWindow.webContents.openDevTools();
        }
        
    } catch (error) {
        console.error('Failed to create main window:', error);
        throw error;
    }
}

// Create system tray
function createSystemTray() {
    try {
        const trayIcon = getTrayIconPath();
        tray = new Tray(trayIcon);
        
        const contextMenu = Menu.buildFromTemplate([
            {
                label: 'Show MIA Enterprise AGI',
                click: () => {
                    if (mainWindow) {
                        mainWindow.show();
                        if (process.platform === 'darwin') {
                            app.dock.show();
                        }
                    }
                }
            },
            { type: 'separator' },
            {
                label: 'System Status',
                submenu: [
                    { label: 'Backend: Running', enabled: false },
                    { label: 'Memory: Optimal', enabled: false },
                    { label: 'CPU: Normal', enabled: false }
                ]
            },
            { type: 'separator' },
            {
                label: 'Settings',
                click: () => {
                    if (mainWindow) {
                        mainWindow.show();
                        mainWindow.webContents.send('navigate-to', '/settings');
                    }
                }
            },
            {
                label: 'About',
                click: () => {
                    showAboutDialog();
                }
            },
            { type: 'separator' },
            {
                label: 'Quit MIA Enterprise AGI',
                click: () => {
                    isQuitting = true;
                    app.quit();
                }
            }
        ]);
        
        tray.setContextMenu(contextMenu);
        tray.setToolTip('MIA Enterprise AGI - Ultimate Local AI Platform');
        
        // Tray click handlers
        tray.on('click', () => {
            if (mainWindow) {
                if (mainWindow.isVisible()) {
                    mainWindow.hide();
                } else {
                    mainWindow.show();
                }
            }
        });
        
        tray.on('double-click', () => {
            if (mainWindow) {
                mainWindow.show();
                mainWindow.focus();
            }
        });
        
    } catch (error) {
        console.error('Failed to create system tray:', error);
    }
}

// Start backend services
async function startBackendServices() {
    try {
        console.log('🔧 Starting backend services...');
        
        // Start Python backend
        const pythonPath = getPythonPath();
        const backendScript = getBackendScriptPath();
        
        if (!fs.existsSync(backendScript)) {
            throw new Error(`Backend script not found: ${backendScript}`);
        }
        
        backendProcess = spawn(pythonPath, [
            backendScript,
            '--mode', 'desktop',
            '--desktop-port', APP_CONFIG.desktop_port.toString(),
            '--api-port', APP_CONFIG.backend_port.toString(),
            '--web-port', APP_CONFIG.frontend_port.toString(),
            '--enable-desktop'
        ], {
            cwd: getResourcesPath(),
            stdio: ['pipe', 'pipe', 'pipe'],
            env: {
                ...process.env,
                PYTHONPATH: getResourcesPath(),
                MIA_DESKTOP_MODE: '1',
                MIA_PORT: APP_CONFIG.backend_port.toString()
            }
        });
        
        backendProcess.stdout.on('data', (data) => {
            console.log(`Backend: ${data.toString()}`);
        });
        
        backendProcess.stderr.on('data', (data) => {
            console.error(`Backend Error: ${data.toString()}`);
        });
        
        backendProcess.on('close', (code) => {
            console.log(`Backend process exited with code ${code}`);
            if (code !== 0 && !isQuitting) {
                showErrorDialog('Backend Error', 'MIA backend process crashed. Please restart the application.');
            }
        });
        
        // Wait for backend to start
        await waitForBackend();
        
        // Start Express server for frontend
        await startExpressServer();
        
        console.log('✅ Backend services started successfully');
        
    } catch (error) {
        console.error('Failed to start backend services:', error);
        throw error;
    }
}

// Wait for backend to be ready
function waitForBackend(timeout = 30000) {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        
        const checkBackend = async () => {
            try {
                const response = await fetch(`http://localhost:${APP_CONFIG.backend_port}/health`);
                if (response.ok) {
                    resolve();
                    return;
                }
            } catch (error) {
                // Backend not ready yet
            }
            
            if (Date.now() - startTime > timeout) {
                reject(new Error('Backend startup timeout'));
                return;
            }
            
            setTimeout(checkBackend, 1000);
        };
        
        checkBackend();
    });
}

// Start Express server for frontend
async function startExpressServer() {
    try {
        expressApp = express();
        
        // Serve static files
        const frontendPath = path.join(getResourcesPath(), 'frontend');
        if (fs.existsSync(frontendPath)) {
            expressApp.use(express.static(frontendPath));
        } else {
            // Fallback to basic HTML
            expressApp.get('/', (req, res) => {
                res.send(getDefaultHTML());
            });
        }
        
        // API proxy to backend
        expressApp.use('/api', (req, res) => {
            const backendUrl = `http://localhost:${APP_CONFIG.backend_port}${req.url}`;
            // Implement proxy logic here
            res.json({ message: 'API proxy not implemented yet' });
        });
        
        expressServer = expressApp.listen(APP_CONFIG.frontend_port, () => {
            console.log(`Frontend server running on port ${APP_CONFIG.frontend_port}`);
        });
        
    } catch (error) {
        console.error('Failed to start Express server:', error);
        throw error;
    }
}

// Setup auto-updater
function setupAutoUpdater() {
    if (!app.isPackaged) return;
    
    autoUpdater.checkForUpdatesAndNotify();
    
    autoUpdater.on('checking-for-update', () => {
        console.log('Checking for update...');
    });
    
    autoUpdater.on('update-available', (info) => {
        console.log('Update available:', info);
        showNotification('Update Available', 'A new version is being downloaded...');
    });
    
    autoUpdater.on('update-not-available', (info) => {
        console.log('Update not available:', info);
    });
    
    autoUpdater.on('error', (err) => {
        console.error('Auto-updater error:', err);
    });
    
    autoUpdater.on('download-progress', (progressObj) => {
        let log_message = "Download speed: " + progressObj.bytesPerSecond;
        log_message = log_message + ' - Downloaded ' + progressObj.percent + '%';
        log_message = log_message + ' (' + progressObj.transferred + "/" + progressObj.total + ')';
        console.log(log_message);
    });
    
    autoUpdater.on('update-downloaded', (info) => {
        console.log('Update downloaded:', info);
        showUpdateDialog();
    });
}

// Setup IPC handlers
function setupIpcHandlers() {
    ipcMain.handle('get-app-info', () => {
        return {
            name: APP_CONFIG.name,
            version: APP_CONFIG.version,
            platform: process.platform,
            arch: process.arch,
            electron: process.versions.electron,
            node: process.versions.node
        };
    });
    
    ipcMain.handle('get-system-info', async () => {
        try {
            const [cpu, mem, osInfo] = await Promise.all([
                si.cpu(),
                si.mem(),
                si.osInfo()
            ]);
            
            return {
                cpu: {
                    manufacturer: cpu.manufacturer,
                    brand: cpu.brand,
                    cores: cpu.cores,
                    physicalCores: cpu.physicalCores,
                    speed: cpu.speed
                },
                memory: {
                    total: mem.total,
                    free: mem.free,
                    used: mem.used
                },
                os: {
                    platform: osInfo.platform,
                    distro: osInfo.distro,
                    release: osInfo.release,
                    arch: osInfo.arch
                }
            };
        } catch (error) {
            console.error('Failed to get system info:', error);
            return null;
        }
    });
    
    ipcMain.handle('show-message-box', async (event, options) => {
        const result = await dialog.showMessageBox(mainWindow, options);
        return result;
    });
    
    ipcMain.handle('show-open-dialog', async (event, options) => {
        const result = await dialog.showOpenDialog(mainWindow, options);
        return result;
    });
    
    ipcMain.handle('show-save-dialog', async (event, options) => {
        const result = await dialog.showSaveDialog(mainWindow, options);
        return result;
    });
    
    ipcMain.handle('open-external', async (event, url) => {
        await shell.openExternal(url);
    });
    
    ipcMain.handle('get-store-value', (event, key, defaultValue) => {
        return store.get(key, defaultValue);
    });
    
    ipcMain.handle('set-store-value', (event, key, value) => {
        store.set(key, value);
    });
    
    ipcMain.handle('restart-app', () => {
        app.relaunch();
        app.exit();
    });
    
    ipcMain.handle('quit-app', () => {
        isQuitting = true;
        app.quit();
    });
}

// Create application menu
function createApplicationMenu() {
    const template = [
        {
            label: 'File',
            submenu: [
                {
                    label: 'New Project',
                    accelerator: 'CmdOrCtrl+N',
                    click: () => {
                        mainWindow.webContents.send('menu-action', 'new-project');
                    }
                },
                {
                    label: 'Open Project',
                    accelerator: 'CmdOrCtrl+O',
                    click: () => {
                        mainWindow.webContents.send('menu-action', 'open-project');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Settings',
                    accelerator: 'CmdOrCtrl+,',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', '/settings');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Quit',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                    click: () => {
                        isQuitting = true;
                        app.quit();
                    }
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
            label: 'MIA',
            submenu: [
                {
                    label: 'Dashboard',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', '/dashboard');
                    }
                },
                {
                    label: 'Chat',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', '/chat');
                    }
                },
                {
                    label: 'Projects',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', '/projects');
                    }
                },
                {
                    label: 'System Monitor',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', '/monitor');
                    }
                }
            ]
        },
        {
            label: 'Window',
            submenu: [
                { role: 'minimize' },
                { role: 'close' }
            ]
        },
        {
            label: 'Help',
            submenu: [
                {
                    label: 'Documentation',
                    click: () => {
                        shell.openExternal('https://docs.mia-enterprise-agi.com');
                    }
                },
                {
                    label: 'Support',
                    click: () => {
                        shell.openExternal('https://support.mia-enterprise-agi.com');
                    }
                },
                { type: 'separator' },
                {
                    label: 'About MIA Enterprise AGI',
                    click: () => {
                        showAboutDialog();
                    }
                }
            ]
        }
    ];
    
    if (process.platform === 'darwin') {
        template.unshift({
            label: app.getName(),
            submenu: [
                { role: 'about' },
                { type: 'separator' },
                { role: 'services' },
                { type: 'separator' },
                { role: 'hide' },
                { role: 'hideothers' },
                { role: 'unhide' },
                { type: 'separator' },
                { role: 'quit' }
            ]
        });
    }
    
    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// Utility functions
function getIconPath() {
    const iconName = process.platform === 'win32' ? 'icon.ico' : 
                     process.platform === 'darwin' ? 'icon.icns' : 'icon.png';
    return path.join(__dirname, 'assets', iconName);
}

function getTrayIconPath() {
    const iconName = process.platform === 'win32' ? 'tray-icon.ico' : 
                     process.platform === 'darwin' ? 'tray-icon.png' : 'tray-icon.png';
    return path.join(__dirname, 'assets', iconName);
}

function getPythonPath() {
    if (app.isPackaged) {
        // In production, use bundled Python
        const pythonPath = process.platform === 'win32' ? 
            path.join(process.resourcesPath, 'python', 'python.exe') :
            path.join(process.resourcesPath, 'python', 'bin', 'python3');
        
        if (fs.existsSync(pythonPath)) {
            return pythonPath;
        }
    }
    
    // Fallback to system Python
    return APP_CONFIG.python_executable;
}

function getBackendScriptPath() {
    return path.join(getResourcesPath(), APP_CONFIG.backend_script);
}

function getResourcesPath() {
    return app.isPackaged ? 
        path.join(process.resourcesPath) : 
        path.join(__dirname, '..');
}

function getDefaultHTML() {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <title>MIA Enterprise AGI</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0; padding: 40px; background: #1a1a1a; color: #fff;
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                min-height: 100vh;
            }
            .logo { font-size: 48px; margin-bottom: 20px; }
            .status { font-size: 18px; margin-bottom: 10px; }
            .loading { animation: pulse 2s infinite; }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        </style>
    </head>
    <body>
        <div class="logo">🤖 MIA Enterprise AGI</div>
        <div class="status loading">Initializing Ultimate Local AI Platform...</div>
        <div class="status">Please wait while MIA starts up...</div>
    </body>
    </html>
    `;
}

function showNotification(title, body) {
    notifier.notify({
        title: title,
        message: body,
        icon: getIconPath(),
        sound: false,
        wait: false
    });
}

function showErrorDialog(title, content) {
    dialog.showErrorBox(title, content);
}

function showAboutDialog() {
    dialog.showMessageBox(mainWindow, {
        type: 'info',
        title: 'About MIA Enterprise AGI',
        message: 'MIA Enterprise AGI',
        detail: `Version: ${APP_CONFIG.version}\nUltimate Local AI Platform\n\nCopyright © 2024 MIA Enterprise Team`,
        buttons: ['OK']
    });
}

function showUpdateDialog() {
    dialog.showMessageBox(mainWindow, {
        type: 'info',
        title: 'Update Ready',
        message: 'Update downloaded',
        detail: 'A new version has been downloaded. Restart the application to apply the update.',
        buttons: ['Restart Now', 'Later'],
        defaultId: 0
    }).then((result) => {
        if (result.response === 0) {
            autoUpdater.quitAndInstall();
        }
    });
}

async function gracefulShutdown() {
    try {
        console.log('🔄 Graceful shutdown initiated...');
        
        // Close Express server
        if (expressServer) {
            expressServer.close();
        }
        
        // Terminate backend process
        if (backendProcess && !backendProcess.killed) {
            backendProcess.kill('SIGTERM');
            
            // Wait for graceful shutdown or force kill after timeout
            setTimeout(() => {
                if (!backendProcess.killed) {
                    backendProcess.kill('SIGKILL');
                }
            }, 5000);
        }
        
        // Save window state
        if (mainWindow) {
            store.set('startMaximized', mainWindow.isMaximized());
        }
        
        isQuitting = true;
        app.quit();
        
    } catch (error) {
        console.error('Error during graceful shutdown:', error);
        app.quit();
    }
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
    showErrorDialog('Application Error', error.message);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
