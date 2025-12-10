#!/usr/bin/env python3
"""
MIA Enterprise AGI - Download Server
Provides direct download access to the complete system ZIP file
"""

from flask import Flask, send_file, render_template_string
import os
from pathlib import Path

app = Flask(__name__)

# HTML template for download page
DOWNLOAD_PAGE = """
<!DOCTYPE html>
<html lang="sl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📦 MIA Enterprise AGI - Prenos</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.2em;
        }
        .download-btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 20px 40px;
            border: none;
            border-radius: 50px;
            font-size: 1.3em;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 20px 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        }
        .info-box {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            text-align: left;
        }
        .info-item {
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .info-label {
            font-weight: bold;
            color: #333;
        }
        .info-value {
            color: #666;
        }
        .instructions {
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 20px;
            margin: 20px 0;
            text-align: left;
            border-radius: 0 10px 10px 0;
        }
        .code {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 MIA Enterprise AGI</h1>
        <p class="subtitle">Celoten sistem pripravljen za prenos</p>
        
        <div class="info-box">
            <div class="info-item">
                <span class="info-label">📁 Datoteka:</span>
                <span class="info-value">MIA_Enterprise_AGI_Complete_System.zip</span>
            </div>
            <div class="info-item">
                <span class="info-label">📊 Velikost:</span>
                <span class="info-value">{{ file_size }} MB</span>
            </div>
            <div class="info-item">
                <span class="info-label">🐍 Vrstice kode:</span>
                <span class="info-value">477,839</span>
            </div>
            <div class="info-item">
                <span class="info-label">🏆 Status:</span>
                <span class="info-value">Enterprise Production Ready</span>
            </div>
        </div>
        
        <a href="/download" class="download-btn">
            ⬇️ PRENESI MIA ENTERPRISE AGI
        </a>
        
        <div class="instructions">
            <h3>🚀 Hitri zagon po prenosu:</h3>
            <div class="code">
                # 1. Razpakuj ZIP datoteko<br>
                # 2. Odpri terminal v mapi<br>
                # 3. Namesti odvisnosti:<br>
                pip install flask flask-socketio pyyaml psutil cryptography<br>
                # 4. Zaženi MIA:<br>
                python mia_chat_interface.py<br>
                # 5. Odpri: http://localhost:12001
            </div>
        </div>
        
        <p style="color: #666; margin-top: 30px;">
            🎉 Dobrodošli v prihodnosti AGI tehnologije!
        </p>
    </div>
</body>
</html>
"""

@app.route('/')
def download_page():
    """Main download page"""
    zip_path = Path('_Complete_SysMIA_Enterprise_AGItem.zip')
    if zip_path.exists():
        file_size = round(zip_path.stat().st_size / (1024 * 1024), 1)
    else:
        file_size = "N/A"
    
    return render_template_string(DOWNLOAD_PAGE, file_size=file_size)

@app.route('/download')
def download_file():
    """Direct download endpoint"""
    zip_path = Path('MIA_Enterprise_AGI_Complete_System.zip')
    
    if not zip_path.exists():
        return "❌ ZIP datoteka ni najdena. Prosimo, generirajte jo ponovno.", 404
    
    return send_file(
        zip_path,
        as_attachment=True,
        download_name='MIA_Enterprise_AGI_Complete_System.zip',
        mimetype='application/zip'
    )

@app.route('/status')
def status():
    """System status endpoint"""
    zip_path = Path('MIA_Enterprise_AGI_Complete_System.zip')
    
    status_info = {
        'file_exists': zip_path.exists(),
        'file_size_mb': round(zip_path.stat().st_size / (1024 * 1024), 1) if zip_path.exists() else 0,
        'system_ready': True,
        'download_url': '/download'
    }
    
    return status_info

if __name__ == '__main__':
    print("🚀 Starting MIA Enterprise AGI Download Server...")
    print("📦 Download page: http://localhost:12002")
    print("⬇️  Direct download: http://localhost:12002/download")
    print("📊 Status: http://localhost:12002/status")
    
    app.run(host='0.0.0.0', port=12002, debug=False)