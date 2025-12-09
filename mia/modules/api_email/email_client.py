#!/usr/bin/env python3
"""
MIA Email Client
Secure IMAP/SMTP client for API key retrieval and email automation
"""

import os
import json
import logging
import time
import re
import email
import imaplib
import smtplib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import threading
import queue

# Encryption
try:
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    Fernet = None

class EmailProvider(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    """Supported email providers"""
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    YAHOO = "yahoo"
    CUSTOM = "custom"

class EmailType(Enum):
    """Types of emails to process"""
    API_KEY = "api_key"
    VERIFICATION = "verification"
    NOTIFICATION = "notification"
    GENERAL = "general"

@dataclass
class EmailAccount:
    """Email account configuration"""
    name: str
    email: str
    password: str
    provider: EmailProvider
    imap_server: str
    imap_port: int
    smtp_server: str
    smtp_port: int
    use_ssl: bool = True
    use_tls: bool = True

@dataclass
class EmailMessage:
    """Email message data"""
    message_id: str
    sender: str
    recipient: str
    subject: str
    body: str
    html_body: Optional[str]
    timestamp: float
    email_type: EmailType
    attachments: List[str]
    processed: bool = False

@dataclass
class APIKeyExtraction:
    """Extracted API key information"""
    service_name: str
    api_key: str
    key_type: str
    expiration: Optional[str]
    usage_limits: Optional[str]
    documentation_url: Optional[str]
    extracted_from: str
    confidence: float

class EmailClient:
    """Secure email client for API key management"""
    
    def __init__(self, config_path: str = "mia/data/email/config.json"):
        self.config_path = config_path
        self.email_dir = Path("mia/data/email")
        self.email_dir.mkdir(parents=True, exist_ok=True)
        
        self.keys_dir = self.email_dir / "keys"
        self.keys_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger("MIA.EmailClient")
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        # Email accounts
        self.email_accounts: Dict[str, EmailAccount] = {}
        
        # Encryption key
        self.encryption_key = self._get_or_create_encryption_key()
        
        # Message processing
        self.message_queue = queue.Queue()
        self.processing_thread = None
        self.is_processing = False
        
        # API key patterns
        self.api_key_patterns = self._load_api_key_patterns()
        
        # Load accounts
        self._load_email_accounts()
        
        self.logger.info("📧 Email Client initialized")
    
    def _load_configuration(self) -> Dict:
        """Load email client configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load email config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default email configuration"""
        config = {
            "enabled": True,
            "auto_process_emails": True,
            "check_interval": 300,  # 5 minutes
            "max_messages_per_check": 50,
            "delete_processed_messages": False,
            "encryption_enabled": True,
            "providers": {
                "gmail": {
                    "imap_server": "imap.gmail.com",
                    "imap_port": 993,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "use_ssl": True,
                    "use_tls": True
                },
                "outlook": {
                    "imap_server": "outlook.office365.com",
                    "imap_port": 993,
                    "smtp_server": "smtp-mail.outlook.com",
                    "smtp_port": 587,
                    "use_ssl": True,
                    "use_tls": True
                },
                "yahoo": {
                    "imap_server": "imap.mail.yahoo.com",
                    "imap_port": 993,
                    "smtp_server": "smtp.mail.yahoo.com",
                    "smtp_port": 587,
                    "use_ssl": True,
                    "use_tls": True
                }
            },
            "api_key_services": [
                "openai", "anthropic", "google", "microsoft", "aws", "azure",
                "github", "gitlab", "stripe", "paypal", "twilio", "sendgrid"
            ],
            "security": {
                "require_encryption": True,
                "auto_delete_sensitive": True,
                "log_email_content": False,
                "max_stored_messages": 1000
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _get_or_create_encryption_key(self) -> Optional[bytes]:
        """Get or create encryption key"""
        try:
            if not ENCRYPTION_AVAILABLE:
                self.logger.warning("Encryption not available - passwords will be stored in plain text")
                return None
            
            key_file = self.email_dir / "encryption.key"
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                # Set restrictive permissions
                os.chmod(key_file, 0o600)
                
                return key
                
        except Exception as e:
            self.logger.error(f"Failed to handle encryption key: {e}")
            return None
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            if not self.encryption_key or not ENCRYPTION_AVAILABLE:
                return data
            
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(data.encode())
            return encrypted_data.decode()
            
        except Exception as e:
            self.logger.error(f"Failed to encrypt data: {e}")
            return data
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            if not self.encryption_key or not ENCRYPTION_AVAILABLE:
                return encrypted_data
            
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt data: {e}")
            return encrypted_data
    
    def _load_api_key_patterns(self) -> Dict[str, List[str]]:
        """Load API key extraction patterns"""
        return {
            "openai": [
                r"sk-[a-zA-Z0-9]{48}",
                r"API Key:\s*([a-zA-Z0-9\-_]{20,})",
                r"Your OpenAI API key:\s*([a-zA-Z0-9\-_]{20,})"
            ],
            "anthropic": [
                r"sk-ant-[a-zA-Z0-9\-_]{95}",
                r"Anthropic API Key:\s*([a-zA-Z0-9\-_]{20,})"
            ],
            "google": [
                r"AIza[0-9A-Za-z\-_]{35}",
                r"Google API Key:\s*([a-zA-Z0-9\-_]{20,})"
            ],
            "github": [
                r"ghp_[a-zA-Z0-9]{36}",
                r"gho_[a-zA-Z0-9]{36}",
                r"ghu_[a-zA-Z0-9]{36}",
                r"ghs_[a-zA-Z0-9]{36}",
                r"ghr_[a-zA-Z0-9]{36}"
            ],
            "aws": [
                r"AKIA[0-9A-Z]{16}",
                r"AWS Access Key ID:\s*([A-Z0-9]{20})"
            ],
            "stripe": [
                r"sk_live_[a-zA-Z0-9]{24}",
                r"sk_test_[a-zA-Z0-9]{24}",
                r"pk_live_[a-zA-Z0-9]{24}",
                r"pk_test_[a-zA-Z0-9]{24}"
            ],
            "generic": [
                r"API[_\s]?Key[:\s]*([a-zA-Z0-9\-_]{20,})",
                r"Token[:\s]*([a-zA-Z0-9\-_]{20,})",
                r"Secret[:\s]*([a-zA-Z0-9\-_]{20,})",
                r"Key[:\s]*([a-zA-Z0-9\-_]{20,})"
            ]
        }
    
    def _load_email_accounts(self):
        """Load email accounts from secure storage"""
        try:
            accounts_file = self.email_dir / "accounts.json"
            
            if accounts_file.exists():
                with open(accounts_file, 'r') as f:
                    accounts_data = json.load(f)
                
                for account_name, account_data in accounts_data.items():
                    # Decrypt password
                    password = self._decrypt_data(account_data["password"])
                    
                    account = EmailAccount(
                        name=account_data["name"],
                        email=account_data["email"],
                        password=password,
                        provider=EmailProvider(account_data["provider"]),
                        imap_server=account_data["imap_server"],
                        imap_port=account_data["imap_port"],
                        smtp_server=account_data["smtp_server"],
                        smtp_port=account_data["smtp_port"],
                        use_ssl=account_data.get("use_ssl", True),
                        use_tls=account_data.get("use_tls", True)
                    )
                    
                    self.email_accounts[account_name] = account
            
            self.logger.info(f"✅ Loaded {len(self.email_accounts)} email accounts")
            
        except Exception as e:
            self.logger.error(f"Failed to load email accounts: {e}")
    
    def _save_email_accounts(self):
        """Save email accounts to secure storage"""
        try:
            accounts_file = self.email_dir / "accounts.json"
            
            accounts_data = {}
            for account_name, account in self.email_accounts.items():
                # Encrypt password
                encrypted_password = self._encrypt_data(account.password)
                
                accounts_data[account_name] = {
                    "name": account.name,
                    "email": account.email,
                    "password": encrypted_password,
                    "provider": account.provider.value,
                    "imap_server": account.imap_server,
                    "imap_port": account.imap_port,
                    "smtp_server": account.smtp_server,
                    "smtp_port": account.smtp_port,
                    "use_ssl": account.use_ssl,
                    "use_tls": account.use_tls
                }
            
            with open(accounts_file, 'w') as f:
                json.dump(accounts_data, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(accounts_file, 0o600)
            
        except Exception as e:
            self.logger.error(f"Failed to save email accounts: {e}")
    
    def add_email_account(self, name: str, email: str, password: str,
                         provider: EmailProvider = EmailProvider.CUSTOM,
                         **kwargs) -> bool:
        """Add email account"""
        try:
            # Get provider settings
            if provider != EmailProvider.CUSTOM:
                provider_config = self.config["providers"].get(provider.value, {})
                
                account = EmailAccount(
                    name=name,
                    email=email,
                    password=password,
                    provider=provider,
                    imap_server=provider_config.get("imap_server", ""),
                    imap_port=provider_config.get("imap_port", 993),
                    smtp_server=provider_config.get("smtp_server", ""),
                    smtp_port=provider_config.get("smtp_port", 587),
                    use_ssl=provider_config.get("use_ssl", True),
                    use_tls=provider_config.get("use_tls", True)
                )
            else:
                # Custom provider
                account = EmailAccount(
                    name=name,
                    email=email,
                    password=password,
                    provider=provider,
                    imap_server=kwargs.get("imap_server", ""),
                    imap_port=kwargs.get("imap_port", 993),
                    smtp_server=kwargs.get("smtp_server", ""),
                    smtp_port=kwargs.get("smtp_port", 587),
                    use_ssl=kwargs.get("use_ssl", True),
                    use_tls=kwargs.get("use_tls", True)
                )
            
            # Test connection
            if not self._test_email_connection(account):
                self.logger.error(f"Failed to connect to email account: {email}")
                return False
            
            # Add account
            self.email_accounts[name] = account
            self._save_email_accounts()
            
            self.logger.info(f"✅ Added email account: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add email account: {e}")
            return False
    
    def _test_email_connection(self, account: EmailAccount) -> bool:
        """Test email account connection"""
        try:
            # Test IMAP connection
            if account.use_ssl:
                imap = imaplib.IMAP4_SSL(account.imap_server, account.imap_port)
            else:
                imap = imaplib.IMAP4(account.imap_server, account.imap_port)
                if account.use_tls:
                    imap.starttls()
            
            imap.login(account.email, account.password)
            imap.logout()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Email connection test failed: {e}")
            return False
    
    def start_email_monitoring(self, account_name: str) -> bool:
        """Start monitoring email account for API keys"""
        try:
            if account_name not in self.email_accounts:
                self.logger.error(f"Email account not found: {account_name}")
                return False
            
            if self.is_processing:
                self.logger.warning("Email monitoring already active")
                return True
            
            self.is_processing = True
            
            # Start processing thread
            self.processing_thread = threading.Thread(
                target=self._email_monitoring_loop,
                args=(account_name,),
                daemon=True
            )
            self.processing_thread.start()
            
            self.logger.info(f"📧 Started email monitoring: {account_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start email monitoring: {e}")
            return False
    
    def stop_email_monitoring(self):
        """Stop email monitoring"""
        self.is_processing = False
        self.logger.info("📧 Stopped email monitoring")
    
    def _email_monitoring_loop(self, account_name: str):
        """Email monitoring loop"""
        account = self.email_accounts[account_name]
        check_interval = self.config.get("check_interval", 300)
        
        while self.is_processing:
            try:
                # Check for new emails
                messages = self._fetch_new_emails(account)
                
                # Process messages
                for message in messages:
                    self._process_email_message(message)
                
                # Wait before next check
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"Email monitoring error: {e}")
                time.sleep(60)  # Wait before retry
    
    def _fetch_new_emails(self, account: EmailAccount) -> List[EmailMessage]:
        """Fetch new emails from account"""
        try:
            messages = []
            
            # Connect to IMAP
            if account.use_ssl:
                imap = imaplib.IMAP4_SSL(account.imap_server, account.imap_port)
            else:
                imap = imaplib.IMAP4(account.imap_server, account.imap_port)
                if account.use_tls:
                    imap.starttls()
            
            imap.login(account.email, account.password)
            imap.select('INBOX')
            
            # Search for unread emails
            status, message_ids = imap.search(None, 'UNSEEN')
            
            if status == 'OK':
                max_messages = self.config.get("max_messages_per_check", 50)
                message_ids = message_ids[0].split()[:max_messages]
                
                for msg_id in message_ids:
                    try:
                        # Fetch message
                        status, msg_data = imap.fetch(msg_id, '(RFC822)')
                        
                        if status == 'OK':
                            email_message = email.message_from_bytes(msg_data[0][1])
                            
                            # Parse message
                            parsed_message = self._parse_email_message(email_message, account.email)
                            
                            if parsed_message:
                                messages.append(parsed_message)
                    
                    except Exception as e:
                        self.logger.error(f"Failed to process message {msg_id}: {e}")
            
            imap.logout()
            
            return messages
            
        except Exception as e:
            self.logger.error(f"Failed to fetch emails: {e}")
            return []
    
    def _parse_email_message(self, email_message, recipient: str) -> Optional[EmailMessage]:
        """Parse email message"""
        try:
            # Get sender
            sender = email_message.get('From', '')
            
            # Get subject
            subject = email_message.get('Subject', '')
            if subject:
                decoded_subject = decode_header(subject)[0]
                if decoded_subject[1]:
                    subject = decoded_subject[0].decode(decoded_subject[1])
                else:
                    subject = str(decoded_subject[0])
            
            # Get message ID
            message_id = email_message.get('Message-ID', '')
            
            # Get timestamp
            timestamp = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Get body
            body = ""
            html_body = None
            attachments = []
            
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition'))
                    
                    if content_type == 'text/plain' and 'attachment' not in content_disposition:
                        body = part.get_payload(decode=True).decode()
                    elif content_type == 'text/html' and 'attachment' not in content_disposition:
                        html_body = part.get_payload(decode=True).decode()
                    elif 'attachment' in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            attachments.append(filename)
            else:
                body = email_message.get_payload(decode=True).decode()
            
            # Determine email type
            email_type = self._classify_email_type(subject, body, sender)
            
            return EmailMessage(
                message_id=message_id,
                sender=sender,
                recipient=recipient,
                subject=subject,
                body=body,
                html_body=html_body,
                timestamp=timestamp,
                email_type=email_type,
                attachments=attachments
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse email message: {e}")
            return None
    
    def _classify_email_type(self, subject: str, body: str, sender: str) -> EmailType:
        """Classify email type"""
        try:
            subject_lower = subject.lower()
            body_lower = body.lower()
            sender_lower = sender.lower()
            
            # API key indicators
            api_indicators = [
                'api key', 'api token', 'access token', 'secret key',
                'authentication', 'credentials', 'authorization'
            ]
            
            if any(indicator in subject_lower or indicator in body_lower for indicator in api_indicators):
                return EmailType.API_KEY
            
            # Verification indicators
            verification_indicators = [
                'verify', 'confirmation', 'activate', 'welcome'
            ]
            
            if any(indicator in subject_lower for indicator in verification_indicators):
                return EmailType.VERIFICATION
            
            # Notification indicators
            notification_indicators = [
                'notification', 'alert', 'update', 'news'
            ]
            
            if any(indicator in subject_lower for indicator in notification_indicators):
                return EmailType.NOTIFICATION
            
            return EmailType.GENERAL
            
        except Exception as e:
            self.logger.error(f"Failed to classify email: {e}")
            return EmailType.GENERAL
    
    def _process_email_message(self, message: EmailMessage):
        """Process email message"""
        try:
            if message.email_type == EmailType.API_KEY:
                # Extract API keys
                api_keys = self._extract_api_keys(message)
                
                for api_key in api_keys:
                    self._store_api_key(api_key)
                    
                    # Notify about new API key
                    self.logger.info(f"🔑 Extracted API key for {api_key.service_name}")
            
            elif message.email_type == EmailType.VERIFICATION:
                # Process verification email
                self._process_verification_email(message)
            
            # Store message if configured
            if not self.config.get("security", {}).get("auto_delete_sensitive", True):
                self._store_email_message(message)
            
            # Mark as processed
            message.processed = True
            
        except Exception as e:
            self.logger.error(f"Failed to process email message: {e}")
    
    def _extract_api_keys(self, message: EmailMessage) -> List[APIKeyExtraction]:
        """Extract API keys from email message"""
        try:
            api_keys = []
            
            # Combine subject and body for analysis
            content = f"{message.subject}\n{message.body}"
            if message.html_body:
                content += f"\n{message.html_body}"
            
            # Try to identify service
            service_name = self._identify_service(message.sender, content)
            
            # Extract keys using patterns
            for service, patterns in self.api_key_patterns.items():
                if service_name and service != service_name and service != "generic":
                    continue
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        if isinstance(match, tuple):
                            api_key = match[0]
                        else:
                            api_key = match
                        
                        # Validate key length and format
                        if len(api_key) >= 20:
                            extraction = APIKeyExtraction(
                                service_name=service_name or service,
                                api_key=api_key,
                                key_type=self._determine_key_type(api_key),
                                expiration=self._extract_expiration(content),
                                usage_limits=self._extract_usage_limits(content),
                                documentation_url=self._extract_documentation_url(content),
                                extracted_from=message.sender,
                                confidence=self._calculate_confidence(service, pattern, content)
                            )
                            
                            api_keys.append(extraction)
            
            return api_keys
            
        except Exception as e:
            self.logger.error(f"Failed to extract API keys: {e}")
            return []
    
    def _identify_service(self, sender: str, content: str) -> Optional[str]:
        """Identify service from sender and content"""
        try:
            sender_lower = sender.lower()
            content_lower = content.lower()
            
            # Service indicators
            services = {
                'openai': ['openai', 'chatgpt'],
                'anthropic': ['anthropic', 'claude'],
                'google': ['google', 'gmail', 'gcp', 'cloud'],
                'microsoft': ['microsoft', 'azure', 'outlook'],
                'aws': ['amazon', 'aws'],
                'github': ['github'],
                'gitlab': ['gitlab'],
                'stripe': ['stripe'],
                'twilio': ['twilio'],
                'sendgrid': ['sendgrid']
            }
            
            for service, indicators in services.items():
                if any(indicator in sender_lower or indicator in content_lower for indicator in indicators):
                    return service
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to identify service: {e}")
            return None
    
    def _determine_key_type(self, api_key: str) -> str:
        """Determine API key type"""
        try:
            if api_key.startswith('sk-'):
                return 'secret_key'
            elif api_key.startswith('pk_'):
                return 'public_key'
            elif api_key.startswith('AKIA'):
                return 'access_key'
            elif 'test' in api_key.lower():
                return 'test_key'
            elif 'live' in api_key.lower():
                return 'live_key'
            else:
                return 'api_key'
                
        except Exception as e:
            self.logger.error(f"Failed to determine key type: {e}")
            return 'unknown'
    
    def _extract_expiration(self, content: str) -> Optional[str]:
        """Extract expiration information"""
        try:
            expiration_patterns = [
                r'expires?\s+(?:on\s+)?([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
                r'valid\s+until\s+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
                r'expiration\s*:\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})'
            ]
            
            for pattern in expiration_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract expiration: {e}")
            return None
    
    def _extract_usage_limits(self, content: str) -> Optional[str]:
        """Extract usage limits information"""
        try:
            limit_patterns = [
                r'(\d+)\s+requests?\s+per\s+(minute|hour|day|month)',
                r'rate\s+limit\s*:\s*(\d+)',
                r'quota\s*:\s*(\d+)'
            ]
            
            for pattern in limit_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(0)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract usage limits: {e}")
            return None
    
    def _extract_documentation_url(self, content: str) -> Optional[str]:
        """Extract documentation URL"""
        try:
            url_patterns = [
                r'https?://[^\s]+(?:doc|api|guide)[^\s]*',
                r'documentation\s*:\s*(https?://[^\s]+)',
                r'api\s+reference\s*:\s*(https?://[^\s]+)'
            ]
            
            for pattern in url_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(1) if match.groups() else match.group(0)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract documentation URL: {e}")
            return None
    
    def _calculate_confidence(self, service: str, pattern: str, content: str) -> float:
        """Calculate extraction confidence"""
        try:
            confidence = 0.5  # Base confidence
            
            # Service-specific patterns have higher confidence
            if service != "generic":
                confidence += 0.3
            
            # Longer patterns have higher confidence
            if len(pattern) > 30:
                confidence += 0.1
            
            # Context indicators
            context_indicators = [
                'api key', 'secret', 'token', 'credentials',
                'authentication', 'authorization'
            ]
            
            context_matches = sum(1 for indicator in context_indicators if indicator in content.lower())
            confidence += min(context_matches * 0.05, 0.2)
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate confidence: {e}")
            return 0.5
    
    def _store_api_key(self, api_key: APIKeyExtraction):
        """Store extracted API key securely"""
        try:
            # Create service directory
            service_dir = self.keys_dir / api_key.service_name
            service_dir.mkdir(exist_ok=True)
            
            # Generate key filename
            key_hash = hashlib.sha256(api_key.api_key.encode()).hexdigest()[:16]
            key_file = service_dir / f"{api_key.key_type}_{key_hash}.json"
            
            # Encrypt API key
            encrypted_key = self._encrypt_data(api_key.api_key)
            
            # Prepare data
            key_data = asdict(api_key)
            key_data["api_key"] = encrypted_key
            key_data["stored_at"] = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            # Save to file
            with open(key_file, 'w') as f:
                json.dump(key_data, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            
            # Also store in environment format
            env_file = service_dir / f"{api_key.service_name.upper()}_API_KEY.env"
            with open(env_file, 'w') as f:
                f.write(f"{api_key.service_name.upper()}_API_KEY={api_key.api_key}\n")
            
            os.chmod(env_file, 0o600)
            
            self.logger.info(f"🔐 Stored API key for {api_key.service_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to store API key: {e}")
    
    def _process_verification_email(self, message: EmailMessage):
        """Process verification email"""
        try:
            # Extract verification links
            verification_links = re.findall(
                r'https?://[^\s]+(?:verify|confirm|activate)[^\s]*',
                message.body,
                re.IGNORECASE
            )
            
            if verification_links:
                self.logger.info(f"📧 Found verification links: {len(verification_links)}")
                
                # Store verification info
                verification_file = self.email_dir / "verifications.json"
                
                verifications = []
                if verification_file.exists():
                    with open(verification_file, 'r') as f:
                        verifications = json.load(f)
                
                verification_data = {
                    "timestamp": self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                    "sender": message.sender,
                    "subject": message.subject,
                    "links": verification_links,
                    "processed": False
                }
                
                verifications.append(verification_data)
                
                with open(verification_file, 'w') as f:
                    json.dump(verifications, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to process verification email: {e}")
    
    def _store_email_message(self, message: EmailMessage):
        """Store email message"""
        try:
            # Check storage limits
            max_stored = self.config.get("security", {}).get("max_stored_messages", 1000)
            
            messages_file = self.email_dir / "messages.json"
            
            messages = []
            if messages_file.exists():
                with open(messages_file, 'r') as f:
                    messages = json.load(f)
            
            # Add new message
            message_data = asdict(message)
            message_data["email_type"] = message.email_type.value
            
            # Don't log email content if configured
            if not self.config.get("security", {}).get("log_email_content", False):
                message_data["body"] = "[Content not logged]"
                message_data["html_body"] = "[Content not logged]"
            
            messages.append(message_data)
            
            # Trim to max size
            if len(messages) > max_stored:
                messages = messages[-max_stored:]
            
            # Save messages
            with open(messages_file, 'w') as f:
                json.dump(messages, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to store email message: {e}")
    
    def get_stored_api_keys(self, service: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get stored API keys"""
        try:
            api_keys = {}
            
            for service_dir in self.keys_dir.iterdir():
                if service_dir.is_dir():
                    service_name = service_dir.name
                    
                    if service and service != service_name:
                        continue
                    
                    service_keys = []
                    
                    for key_file in service_dir.glob("*.json"):
                        try:
                            with open(key_file, 'r') as f:
                                key_data = json.load(f)
                            
                            # Decrypt API key for display (masked)
                            encrypted_key = key_data.get("api_key", "")
                            decrypted_key = self._decrypt_data(encrypted_key)
                            
                            # Mask key for security
                            if len(decrypted_key) > 8:
                                masked_key = decrypted_key[:4] + "*" * (len(decrypted_key) - 8) + decrypted_key[-4:]
                            else:
                                masked_key = "*" * len(decrypted_key)
                            
                            key_data["api_key"] = masked_key
                            service_keys.append(key_data)
                            
                        except Exception as e:
                            self.logger.error(f"Failed to load key file {key_file}: {e}")
                    
                    if service_keys:
                        api_keys[service_name] = service_keys
            
            return api_keys
            
        except Exception as e:
            self.logger.error(f"Failed to get stored API keys: {e}")
            return {}
    
    def get_api_key(self, service: str, key_type: str = "api_key") -> Optional[str]:
        """Get decrypted API key for use"""
        try:
            service_dir = self.keys_dir / service
            
            if not service_dir.exists():
                return None
            
            # Find matching key file
            for key_file in service_dir.glob(f"{key_type}_*.json"):
                try:
                    with open(key_file, 'r') as f:
                        key_data = json.load(f)
                    
                    # Decrypt and return API key
                    encrypted_key = key_data.get("api_key", "")
                    return self._decrypt_data(encrypted_key)
                    
                except Exception as e:
                    self.logger.error(f"Failed to load key file {key_file}: {e}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get API key: {e}")
            return None
    
    def delete_api_key(self, service: str, key_hash: str) -> bool:
        """Delete stored API key"""
        try:
            service_dir = self.keys_dir / service
            
            if not service_dir.exists():
                return False
            
            # Find and delete key file
            for key_file in service_dir.glob(f"*_{key_hash}.json"):
                key_file.unlink()
                
                # Also delete env file
                env_file = service_dir / f"{service.upper()}_API_KEY.env"
                if env_file.exists():
                    env_file.unlink()
                
                self.logger.info(f"🗑️ Deleted API key for {service}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete API key: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get email client status"""
        try:
            stored_keys = self.get_stored_api_keys()
            total_keys = sum(len(keys) for keys in stored_keys.values())
            
            return {
                "enabled": self.config.get("enabled", True),
                "encryption_available": ENCRYPTION_AVAILABLE,
                "accounts_count": len(self.email_accounts),
                "is_monitoring": self.is_processing,
                "stored_api_keys": total_keys,
                "services_with_keys": list(stored_keys.keys()),
                "auto_process_emails": self.config.get("auto_process_emails", True),
                "check_interval": self.config.get("check_interval", 300)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {"error": str(e)}

# Global instance
email_client = EmailClient()