# 🖥️ MIA Enterprise AGI - Desktop Quick Start

## 🚀 One-Click Desktop Launch

MIA Enterprise AGI is now a complete desktop application with automatic model discovery and self-learning capabilities!

### Windows 🪟
1. **Double-click** `start_mia_windows.bat`
2. The application will automatically:
   - Check and install Python dependencies
   - Create necessary data directories
   - Start model discovery on all drives
   - Launch web interface at http://localhost:12000

### Linux 🐧
1. **Double-click** `start_mia_linux.sh` or run in terminal:
   ```bash
   ./start_mia_linux.sh
   ```
2. The application will automatically:
   - Verify Python 3.8+ installation
   - Install required packages
   - Set up data directories with proper permissions
   - Begin scanning for AI models

### macOS 🍎
1. **Double-click** `start_mia_macos.command`
2. The application will automatically:
   - Check Python and Xcode Command Line Tools
   - Install dependencies via pip3
   - Scan common macOS model locations
   - Start the complete MIA system

## 🧠 What MIA Does Automatically

### 🔍 Model Discovery
- **Scans all drives** including external USB drives
- **Finds AI models** in formats: GGUF, Safetensors, PyTorch, ONNX, HuggingFace
- **Common locations checked**:
  - `~/Downloads`
  - `~/Documents/AI_Models`
  - `~/.cache/huggingface`
  - `~/.ollama/models`
  - External drives and USB storage
  - Custom model directories

### 📚 Self-Learning
- **Extracts knowledge** from discovered LLM models
- **Analyzes behavior patterns** and capabilities
- **Learns continuously** from local AI models
- **Improves responses** based on learned knowledge

### 🌐 Web Interface
- **Modern dashboard** at http://localhost:12000
- **Real-time monitoring** of discovery and learning
- **Model management** and statistics
- **Learning progress** tracking

### 🔌 API Gateway
- **REST API** at http://localhost:8000
- **Enterprise security** with authentication
- **Rate limiting** and monitoring
- **Real-time analytics**

## 📊 System Requirements

### Minimum Requirements
- **Python 3.8+** (automatically checked)
- **4GB RAM** (8GB+ recommended)
- **10GB free disk space**
- **Internet connection** (for initial setup only)

### Supported Platforms
- ✅ **Windows 10/11** (x64)
- ✅ **Linux** (Ubuntu, CentOS, Arch, etc.)
- ✅ **macOS 10.15+** (Intel & Apple Silicon)

## 🎯 Quick Access URLs

Once MIA is running:

| Service | URL | Description |
|---------|-----|-------------|
| **Web Interface** | http://localhost:12000 | Main dashboard and controls |
| **API Gateway** | http://localhost:8000 | REST API endpoints |
| **Health Check** | http://localhost:8000/health | System status |
| **Metrics** | http://localhost:8000/metrics | Real-time analytics |

## 🔧 Advanced Configuration

### Custom Model Paths
Edit `mia/data/models/discovery_config.json`:
```json
{
  "scan_paths": [
    "/custom/model/path",
    "D:\\MyModels",
    "/external/drive/models"
  ],
  "file_extensions": [".gguf", ".bin", ".safetensors", ".pt", ".onnx"]
}
```

### Learning Configuration
Edit `mia/data/learning/config.json`:
```json
{
  "max_concurrent_tasks": 2,
  "learning_methods": ["knowledge_extraction", "behavior_modeling"],
  "max_model_size": 53687091200,
  "timeout_minutes": 60
}
```

## 🛠️ Troubleshooting

### Python Not Found
- **Windows**: Install from https://python.org
- **Linux**: `sudo apt install python3 python3-pip`
- **macOS**: `brew install python3` or from python.org

### Permission Errors (Linux/macOS)
```bash
chmod +x start_mia_linux.sh
chmod +x start_mia_macos.command
```

### Port Already in Use
If ports 8000 or 12000 are busy, edit `mia_main.py`:
```python
# Change these lines
await self._start_web_interface()  # Uses port 12000
await self._start_api_gateway()    # Uses port 8000
```

### No Models Found
- Check if models are in supported formats
- Verify file permissions
- Add custom paths to discovery config
- Models will be found automatically as you add them

## 📈 Monitoring & Logs

### Log Files
- **Application logs**: `mia_desktop.log`
- **Discovery logs**: `mia/logs/discovery.log`
- **Learning logs**: `mia/logs/learning.log`
- **Security logs**: `mia/data/security/audit.log`

### Real-time Status
```bash
# Check system status
curl http://localhost:8000/health

# Get discovered models
curl http://localhost:8000/api/models

# View learning progress
curl http://localhost:8000/api/learning
```

## 🎉 Success Indicators

When MIA is running successfully, you'll see:

1. ✅ **Console output** showing system initialization
2. 🌐 **Web interface** accessible at localhost:12000
3. 🔍 **Model discovery** finding AI models automatically
4. 📚 **Learning tasks** processing discovered models
5. 📊 **Real-time metrics** in the dashboard

## 🆘 Support

If you encounter issues:

1. **Check logs** in `mia_desktop.log`
2. **Verify Python version** is 3.8+
3. **Ensure ports** 8000 and 12000 are available
4. **Check permissions** on data directories
5. **Review GitHub issues** at https://github.com/Lukifuki1/Mia/issues

---

**🤖 MIA Enterprise AGI - Your Local Digital Intelligence System**

*Automatically discovers, learns from, and improves using local AI models while maintaining complete privacy and security.*