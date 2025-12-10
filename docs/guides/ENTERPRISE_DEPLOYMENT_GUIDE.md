# 🚀 MIA Enterprise AGI - Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying MIA Enterprise AGI in production environments with enterprise-grade features including monitoring, security, scalability, and compliance.

## 📋 Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 4 cores (8 recommended)
- RAM: 8 GB (16 GB recommended)
- Storage: 50 GB SSD (100 GB recommended)
- Network: 1 Gbps connection
- OS: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+

**Recommended for Production:**
- CPU: 8+ cores with AVX2 support
- RAM: 32 GB+
- Storage: 200 GB+ NVMe SSD
- GPU: NVIDIA RTX 4090 / A100 (optional but recommended)
- Network: 10 Gbps connection

### Software Dependencies

```bash
# Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Python 3.11+ (if running without Docker)
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# NVIDIA Docker (for GPU support)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

## 🏗️ Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/Lukifuki1/Mia.git
cd Mia

# Deploy with enterprise configuration
./deploy-enterprise.sh deploy
```

### Option 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/Lukifuki1/Mia.git
cd Mia

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/enterprise.json.example mia_data/config/enterprise.json
# Edit configuration as needed

# Start MIA Enterprise
python mia_enterprise_launcher.py --mode enterprise
```

### Option 3: Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

## ⚙️ Configuration

### Enterprise Configuration

Edit `mia_data/config/enterprise.json`:

```json
{
  "system": {
    "mode": "enterprise",
    "max_workers": 8,
    "memory_limit_gb": 16,
    "gpu_enabled": true,
    "auto_scaling": true
  },
  "services": {
    "core": {"enabled": true, "port": 8000, "workers": 4},
    "web": {"enabled": true, "port": 12000, "workers": 2},
    "voice": {"enabled": true, "port": 8001},
    "multimodal": {"enabled": true, "port": 8002},
    "projects": {"enabled": true, "port": 8003}
  },
  "monitoring": {
    "health_check_interval": 30,
    "performance_logging": true,
    "alerts_enabled": true,
    "metrics_retention_days": 30
  },
  "security": {
    "authentication_required": true,
    "rate_limiting": true,
    "audit_logging": true,
    "encryption_enabled": true
  },
  "enterprise": {
    "backup_enabled": true,
    "backup_interval_hours": 6,
    "disaster_recovery": true,
    "compliance_mode": "SOC2"
  }
}
```

### Security Configuration

Edit `mia_data/config/security.json`:

```json
{
  "authentication": {
    "password_min_length": 12,
    "password_require_special": true,
    "password_require_numbers": true,
    "password_require_uppercase": true,
    "mfa_required": true,
    "session_timeout_minutes": 60,
    "max_failed_attempts": 5,
    "lockout_duration_minutes": 30
  },
  "authorization": {
    "rbac_enabled": true,
    "default_role": "user",
    "admin_approval_required": true
  },
  "audit": {
    "log_all_events": true,
    "retention_days": 2555,
    "real_time_monitoring": true,
    "alert_on_violations": true
  },
  "compliance": {
    "gdpr_enabled": true,
    "soc2_enabled": true,
    "iso27001_enabled": true,
    "data_classification": true
  }
}
```

### Monitoring Configuration

Edit `mia_data/config/monitoring.json`:

```json
{
  "monitoring": {
    "interval_seconds": 30,
    "retention_days": 30,
    "batch_size": 100
  },
  "alerting": {
    "enabled": true,
    "email_enabled": true,
    "webhook_enabled": false,
    "smtp_server": "smtp.company.com",
    "smtp_port": 587,
    "email_from": "mia-monitor@company.com",
    "email_to": ["admin@company.com", "ops@company.com"]
  },
  "thresholds": {
    "cpu_usage": {"warning": 80, "critical": 95},
    "memory_usage": {"warning": 85, "critical": 95},
    "disk_usage": {"warning": 85, "critical": 95},
    "response_time": {"warning": 2000, "critical": 5000}
  }
}
```

## 🔒 Security Setup

### 1. Create Admin User

```bash
# Using the security system
python -c "
from mia_enterprise_security import MIAEnterpriseSecurity, SecurityLevel
security = MIAEnterpriseSecurity()
admin_id = security.create_user(
    username='admin',
    email='admin@company.com',
    password='YourSecurePassword123!',
    security_level=SecurityLevel.SYSTEM_ADMIN
)
print(f'Admin user created: {admin_id}')
"
```

### 2. Configure SSL/TLS

```bash
# Generate SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/mia.key \
  -out nginx/ssl/mia.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=mia.company.com"

# Or use Let's Encrypt
certbot certonly --standalone -d mia.company.com
```

### 3. Configure Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 12000/tcp # MIA Web Interface
sudo ufw enable

# iptables
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 12000 -j ACCEPT
```

## 📊 Monitoring and Alerting

### Health Checks

```bash
# Check system health
curl http://localhost:12000/health

# Check individual services
curl http://localhost:8000/health  # Core API
curl http://localhost:8001/health  # Voice service
curl http://localhost:8002/health  # Multimodal service
```

### Monitoring Dashboard

Access monitoring dashboards:
- **Grafana**: http://localhost:3000 (admin/admin_change_me)
- **Prometheus**: http://localhost:9090
- **MIA Web Interface**: http://localhost:12000

### Log Monitoring

```bash
# View system logs
docker-compose -f docker-compose.enterprise.yml logs -f

# View specific service logs
docker-compose -f docker-compose.enterprise.yml logs -f mia-enterprise

# View security logs
tail -f mia_data/logs/security/security.log
tail -f mia_data/logs/security/audit.log
```

## 🔄 Backup and Recovery

### Automated Backups

Backups are automatically created every 6 hours (configurable). Manual backup:

```bash
# Create manual backup
./deploy-enterprise.sh backup

# List backups
ls -la backups/

# Restore from backup
cp -r backups/mia_backup_YYYYMMDD_HHMMSS/mia_data ./
```

### Database Backup

```bash
# Backup SQLite databases
cp mia_data/memory/consciousness.db backups/
cp mia_data/memory/memory.db backups/
cp mia_data/security/security.db backups/
cp mia_data/monitoring/metrics.db backups/
```

## 🚀 Performance Optimization

### CPU Optimization

```bash
# Set CPU governor to performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Disable CPU frequency scaling
sudo systemctl disable ondemand
```

### Memory Optimization

```bash
# Increase shared memory
echo 'kernel.shmmax = 68719476736' >> /etc/sysctl.conf
echo 'kernel.shmall = 4294967296' >> /etc/sysctl.conf
sudo sysctl -p
```

### GPU Optimization (NVIDIA)

```bash
# Set GPU to performance mode
nvidia-smi -pm 1
nvidia-smi -ac 877,1215  # Adjust for your GPU
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale web interface
docker-compose -f docker-compose.enterprise.yml up -d --scale mia-enterprise=3

# Load balancer configuration (nginx)
upstream mia_backend {
    server mia-enterprise-1:12000;
    server mia-enterprise-2:12000;
    server mia-enterprise-3:12000;
}
```

### Vertical Scaling

Edit `docker-compose.enterprise.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '8.0'      # Increase CPU limit
      memory: 32G      # Increase memory limit
    reservations:
      cpus: '4.0'
      memory: 16G
```

## 🛡️ Compliance

### SOC 2 Compliance

- ✅ Access controls implemented
- ✅ Audit logging enabled
- ✅ Data encryption at rest and in transit
- ✅ Incident response procedures
- ✅ Monitoring and alerting

### GDPR Compliance

- ✅ Data classification and inventory
- ✅ Privacy by design
- ✅ Data subject rights implementation
- ✅ Breach notification procedures
- ✅ Data retention policies

### ISO 27001 Compliance

- ✅ Information security management system
- ✅ Risk assessment and treatment
- ✅ Security controls implementation
- ✅ Continuous monitoring
- ✅ Regular security reviews

## 🔧 Troubleshooting

### Common Issues

**Issue: High CPU Usage**
```bash
# Check processes
docker exec mia-enterprise-agi top
# Reduce workers in configuration
# Enable CPU throttling
```

**Issue: Memory Leaks**
```bash
# Monitor memory usage
docker stats mia-enterprise-agi
# Restart service
docker-compose -f docker-compose.enterprise.yml restart mia-enterprise
```

**Issue: Database Corruption**
```bash
# Check database integrity
sqlite3 mia_data/memory/consciousness.db "PRAGMA integrity_check;"
# Restore from backup if needed
```

### Log Analysis

```bash
# Search for errors
grep -i error mia_data/logs/enterprise/mia_enterprise.log

# Search for security events
grep -i "security" mia_data/logs/security/security.log

# Monitor real-time logs
tail -f mia_data/logs/enterprise/mia_enterprise.log | grep -i "error\|warning\|critical"
```

## 📞 Support

### Enterprise Support Channels

- **Email**: enterprise-support@mia-agi.com
- **Phone**: +1-800-MIA-SUPPORT
- **Portal**: https://support.mia-agi.com
- **Emergency**: +1-800-MIA-EMERGENCY (24/7)

### Documentation

- **API Documentation**: http://localhost:12000/docs
- **Admin Guide**: `/docs/admin-guide.md`
- **Security Guide**: `/docs/security-guide.md`
- **Compliance Guide**: `/docs/compliance-guide.md`

### Community

- **GitHub**: https://github.com/Lukifuki1/Mia
- **Discord**: https://discord.gg/mia-agi
- **Forum**: https://forum.mia-agi.com

---

## 📄 License

MIA Enterprise AGI is licensed under the Enterprise License Agreement.
For licensing inquiries, contact: licensing@mia-agi.com

---

**© 2024 MIA Enterprise AGI. All rights reserved.**