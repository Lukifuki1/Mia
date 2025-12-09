#!/usr/bin/env python3
"""
🌐 Network Security
==================
"""

import socket
import ssl
import logging
import ipaddress
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class NetworkSecurityManager:
    """Network security manager"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.NetworkSecurity")
        
        # Dovoljeni IP ranges
        self.allowed_ip_ranges = [
            ipaddress.ip_network('127.0.0.0/8'),    # Localhost
            ipaddress.ip_network('10.0.0.0/8'),     # Private
            ipaddress.ip_network('172.16.0.0/12'),  # Private
            ipaddress.ip_network('192.168.0.0/16'), # Private
        ]
        
        # Prepovedani porti
        self.blocked_ports = {22, 23, 25, 53, 135, 139, 445, 1433, 3389}
        
        # SSL/TLS konfiguracija
        self.ssl_context = self._create_secure_ssl_context()
    
    def _create_secure_ssl_context(self) -> ssl.SSLContext:
        """Ustvari varni SSL context"""
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        return context
    
    def validate_url(self, url: str) -> bool:
        """Validiraj URL za varnost"""
        try:
            parsed = urlparse(url)
            
            # Preveri protokol
            if parsed.scheme not in ['http', 'https']:
                self.logger.warning(f"Nepodprt protokol: {parsed.scheme}")
                return False
            
            # Preveri hostname
            if not parsed.hostname:
                return False
            
            # Preveri IP naslov
            try:
                ip = ipaddress.ip_address(parsed.hostname)
                if not self._is_ip_allowed(ip):
                    self.logger.warning(f"Prepovedan IP: {ip}")
                    return False
            except ValueError:
                # Ni IP naslov, preveri hostname
                if not self._is_hostname_allowed(parsed.hostname):
                    return False
            
            # Preveri port
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            if port in self.blocked_ports:
                self.logger.warning(f"Prepovedan port: {port}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Napaka pri validaciji URL: {e}")
            return False
    
    def _is_ip_allowed(self, ip: ipaddress.IPv4Address) -> bool:
        """Preveri, če je IP naslov dovoljen"""
        for allowed_range in self.allowed_ip_ranges:
            if ip in allowed_range:
                return True
        return False
    
    def _is_hostname_allowed(self, hostname: str) -> bool:
        """Preveri, če je hostname dovoljen"""
        # Preprosta whitelist logika
        allowed_domains = [
            'localhost',
            'api.openai.com',
            'huggingface.co',
            'github.com'
        ]
        
        for domain in allowed_domains:
            if hostname.endswith(domain):
                return True
        
        return False
    
    def create_secure_session(self) -> requests.Session:
        """Ustvari varno HTTP session"""
        session = requests.Session()
        
        # Retry strategija
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Varnostni headers
        session.headers.update({
            'User-Agent': 'MIA-Enterprise-AGI/1.0',
            'Accept': 'application/json',
            'Connection': 'close'
        })
        
        # SSL verifikacija
        session.verify = True
        
        return session
    
    def scan_port(self, host: str, port: int, timeout: int = 3) -> bool:
        """Skeniraj port"""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, socket.error):
            return False
    
    def get_network_info(self) -> Dict[str, Any]:
        """Pridobi network informacije"""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            return {
                "hostname": hostname,
                "local_ip": local_ip,
                "ssl_context_configured": True,
                "allowed_ip_ranges": [str(range_) for range_ in self.allowed_ip_ranges],
                "blocked_ports": list(self.blocked_ports)
            }
            
        except Exception as e:
            self.logger.error(f"Napaka pri pridobivanju network info: {e}")
            return {}

# Globalni network security manager
network_security = NetworkSecurityManager()
