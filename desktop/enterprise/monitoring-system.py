#!/usr/bin/env python3
"""
Enterprise Monitoring System for MIA Enterprise AGI
"""

import json
import time
import logging
import psutil
import threading
from datetime import datetime
from pathlib import Path
import socket
import requests

class EnterpriseMonitor:

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    def __init__(self, config_file="monitoring-config.json"):
        self.config = self.load_config(config_file)
        self.logger = self.setup_logging()
        self.monitoring_active = False
        self.monitoring_thread = None
        
    def load_config(self, config_file):
        """Load monitoring configuration"""
        default_config = {
            "monitoring": {
                "enabled": True,
                "interval": 60,
                "metrics": ["cpu", "memory", "disk", "network", "processes"],
                "thresholds": {
                    "cpu_warning": 80,
                    "cpu_critical": 95,
                    "memory_warning": 80,
                    "memory_critical": 95,
                    "disk_warning": 85,
                    "disk_critical": 95
                }
            },
            "logging": {
                "level": "INFO",
                "file": "/var/log/mia-enterprise-agi/monitor.log",
                "max_size": "100MB",
                "backup_count": 5,
                "syslog_enabled": False,
                "syslog_server": "localhost",
                "syslog_port": 514
            },
            "alerting": {
                "enabled": True,
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "recipients": []
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "headers": {}
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": "",
                    "channel": "#alerts"
                }
            },
            "reporting": {
                "enabled": True,
                "interval": 3600,
                "retention_days": 30,
                "export_format": "json"
            }
        }
        
        try:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    default_config.update(user_config)
            return default_config
        except Exception as e:
            print(f"Failed to load config: {e}")
            return default_config
    
    def setup_logging(self):
        """Setup logging system"""
        logger = logging.getLogger("MIA.EnterpriseMonitor")
        logger.setLevel(getattr(logging, self.config["logging"]["level"]))
        
        # File handler
        log_file = Path(self.config["logging"]["file"])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=100*1024*1024,  # 100MB
            backupCount=self.config["logging"]["backup_count"]
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Syslog handler
        if self.config["logging"]["syslog_enabled"]:
            syslog_handler = logging.handlers.SysLogHandler(
                address=(
                    self.config["logging"]["syslog_server"],
                    self.config["logging"]["syslog_port"]
                )
            )
            syslog_handler.setFormatter(formatter)
            logger.addHandler(syslog_handler)
        
        return logger
    
    def start_monitoring(self):
        """Start monitoring system"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        self.logger.info("Enterprise monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Enterprise monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                metrics = self.collect_metrics()
                self.process_metrics(metrics)
                self.check_thresholds(metrics)
                
                if self.config["reporting"]["enabled"]:
                    self.store_metrics(metrics)
                
                time.sleep(self.config["monitoring"]["interval"])
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(10)
    
    def collect_metrics(self):
        """Collect system metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "hostname": socket.gethostname()
        }
        
        enabled_metrics = self.config["monitoring"]["metrics"]
        
        if "cpu" in enabled_metrics:
            metrics["cpu"] = {
                "usage_percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        
        if "memory" in enabled_metrics:
            memory = psutil.virtual_memory()
            metrics["memory"] = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "usage_percent": memory.percent
            }
        
        if "disk" in enabled_metrics:
            disk = psutil.disk_usage('/')
            metrics["disk"] = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "usage_percent": (disk.used / disk.total) * 100
            }
        
        if "network" in enabled_metrics:
            network = psutil.net_io_counters()
            metrics["network"] = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        
        if "processes" in enabled_metrics:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                if 'mia' in proc.info['name'].lower():
                    processes.append(proc.info)
            metrics["processes"] = processes
        
        return metrics
    
    def process_metrics(self, metrics):
        """Process collected metrics"""
        self.logger.info(f"Metrics collected: CPU {metrics.get('cpu', {}).get('usage_percent', 0):.1f}%, "
                        f"Memory {metrics.get('memory', {}).get('usage_percent', 0):.1f}%, "
                        f"Disk {metrics.get('disk', {}).get('usage_percent', 0):.1f}%")
    
    def check_thresholds(self, metrics):
        """Check metrics against thresholds"""
        thresholds = self.config["monitoring"]["thresholds"]
        alerts = []
        
        # CPU threshold check
        cpu_usage = metrics.get("cpu", {}).get("usage_percent", 0)
        if cpu_usage >= thresholds["cpu_critical"]:
            alerts.append({
                "level": "critical",
                "metric": "cpu",
                "value": cpu_usage,
                "threshold": thresholds["cpu_critical"],
                "message": f"CPU usage critical: {cpu_usage:.1f}%"
            })
        elif cpu_usage >= thresholds["cpu_warning"]:
            alerts.append({
                "level": "warning",
                "metric": "cpu",
                "value": cpu_usage,
                "threshold": thresholds["cpu_warning"],
                "message": f"CPU usage warning: {cpu_usage:.1f}%"
            })
        
        # Memory threshold check
        memory_usage = metrics.get("memory", {}).get("usage_percent", 0)
        if memory_usage >= thresholds["memory_critical"]:
            alerts.append({
                "level": "critical",
                "metric": "memory",
                "value": memory_usage,
                "threshold": thresholds["memory_critical"],
                "message": f"Memory usage critical: {memory_usage:.1f}%"
            })
        elif memory_usage >= thresholds["memory_warning"]:
            alerts.append({
                "level": "warning",
                "metric": "memory",
                "value": memory_usage,
                "threshold": thresholds["memory_warning"],
                "message": f"Memory usage warning: {memory_usage:.1f}%"
            })
        
        # Disk threshold check
        disk_usage = metrics.get("disk", {}).get("usage_percent", 0)
        if disk_usage >= thresholds["disk_critical"]:
            alerts.append({
                "level": "critical",
                "metric": "disk",
                "value": disk_usage,
                "threshold": thresholds["disk_critical"],
                "message": f"Disk usage critical: {disk_usage:.1f}%"
            })
        elif disk_usage >= thresholds["disk_warning"]:
            alerts.append({
                "level": "warning",
                "metric": "disk",
                "value": disk_usage,
                "threshold": thresholds["disk_warning"],
                "message": f"Disk usage warning: {disk_usage:.1f}%"
            })
        
        # Send alerts
        for alert in alerts:
            self.send_alert(alert)
    
    def send_alert(self, alert):
        """Send alert notification"""
        if not self.config["alerting"]["enabled"]:
            return
        
        self.logger.warning(f"ALERT: {alert['message']}")
        
        # Email alert
        if self.config["alerting"]["email"]["enabled"]:
            self.send_email_alert(alert)
        
        # Webhook alert
        if self.config["alerting"]["webhook"]["enabled"]:
            self.send_webhook_alert(alert)
        
        # Slack alert
        if self.config["alerting"]["slack"]["enabled"]:
            self.send_slack_alert(alert)
    
    def send_email_alert(self, alert):
        """Send email alert"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            email_config = self.config["alerting"]["email"]
            
            msg = MIMEMultipart()
            msg['From'] = email_config["username"]
            msg['Subject'] = f"MIA Enterprise AGI Alert - {alert['level'].upper()}"
            
            body = f"""
            Alert Level: {alert['level'].upper()}
            Metric: {alert['metric']}
            Current Value: {alert['value']}
            Threshold: {alert['threshold']}
            Message: {alert['message']}
            Timestamp: {datetime.now().isoformat()}
            Hostname: {socket.gethostname()}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            
            for recipient in email_config["recipients"]:
                msg['To'] = recipient
                server.send_message(msg)
            
            server.quit()
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def send_webhook_alert(self, alert):
        """Send webhook alert"""
        try:
            webhook_config = self.config["alerting"]["webhook"]
            
            payload = {
                "alert": alert,
                "timestamp": datetime.now().isoformat(),
                "hostname": socket.gethostname()
            }
            
            response = requests.post(
                webhook_config["url"],
                json=payload,
                headers=webhook_config.get("headers", {}),
                timeout=10
            )
            
            if response.status_code != 200:
                self.logger.error(f"Webhook alert failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to send webhook alert: {e}")
    
    def send_slack_alert(self, alert):
        """Send Slack alert"""
        try:
            slack_config = self.config["alerting"]["slack"]
            
            color = "danger" if alert["level"] == "critical" else "warning"
            
            payload = {
                "channel": slack_config["channel"],
                "attachments": [{
                    "color": color,
                    "title": f"MIA Enterprise AGI Alert - {alert['level'].upper()}",
                    "fields": [
                        {"title": "Metric", "value": alert["metric"], "short": True},
                        {"title": "Value", "value": f"{alert['value']:.1f}", "short": True},
                        {"title": "Threshold", "value": f"{alert['threshold']}", "short": True},
                        {"title": "Hostname", "value": socket.gethostname(), "short": True}
                    ],
                    "text": alert["message"],
                    "ts": int(self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200)
                }]
            }
            
            response = requests.post(
                slack_config["webhook_url"],
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                self.logger.error(f"Slack alert failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {e}")
    
    def store_metrics(self, metrics):
        """Store metrics for reporting"""
        try:
            metrics_dir = Path("/var/lib/mia-enterprise-agi/metrics")
            metrics_dir.mkdir(parents=True, exist_ok=True)
            
            date_str = datetime.now().strftime("%Y-%m-%d")
            metrics_file = metrics_dir / f"metrics-{date_str}.json"
            
            # Append metrics to daily file
            with open(metrics_file, 'a') as f:
                f.write(json.dumps(metrics) + "\n")
            
            # Cleanup old metrics
            self.cleanup_old_metrics(metrics_dir)
            
        except Exception as e:
            self.logger.error(f"Failed to store metrics: {e}")
    
    def cleanup_old_metrics(self, metrics_dir):
        """Cleanup old metric files"""
        try:
            retention_days = self.config["reporting"]["retention_days"]
            cutoff_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - (retention_days * 24 * 3600)
            
            for file_path in metrics_dir.glob("metrics-*.json"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    self.logger.info(f"Deleted old metrics file: {file_path}")
                    
        except Exception as e:
            self.logger.error(f"Failed to cleanup old metrics: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MIA Enterprise Monitoring System')
    parser.add_argument('--config', default='monitoring-config.json', help='Configuration file')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--test', action='store_true', help='Test configuration')
    
    args = parser.parse_args()
    
    monitor = EnterpriseMonitor(args.config)
    
    if args.test:
        print("Testing monitoring configuration...")
        metrics = monitor.collect_metrics()
        print(f"Collected metrics: {json.dumps(metrics, indent=2)}")
        return
    
    if args.daemon:
        print("Starting enterprise monitoring daemon...")
        monitor.start_monitoring()
        
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("Stopping monitoring...")
            monitor.stop_monitoring()
    else:
        print("Collecting single metrics sample...")
        metrics = monitor.collect_metrics()
        print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
