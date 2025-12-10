#!/usr/bin/env python3
"""
MIA Enterprise API Gateway
Provides enterprise-grade API management and routing
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

from .security import security_manager, validate_session
from .analytics import analytics, record_performance_metric, record_usage_metric

class APIVersion(Enum):
    """API versions"""
    V1 = "v1"
    V2 = "v2"
    BETA = "beta"

class RateLimitType(Enum):
    """Rate limit types"""
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"

@dataclass
class RateLimit:
    """Rate limit configuration"""
    limit: int
    window: int  # seconds
    limit_type: RateLimitType

@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    path: str
    method: str
    handler: Callable
    version: APIVersion
    auth_required: bool = True
    rate_limit: Optional[RateLimit] = None
    permissions: List[str] = None

class EnterpriseAPIGateway:
    """Enterprise API Gateway"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.app = FastAPI(
            title="MIA Enterprise API Gateway",
            description="Enterprise-grade API gateway for MIA platform",
            version="1.0.0"
        )
        
        self.logger = self._setup_logging()
        self.endpoints = {}
        self.rate_limits = {}
        self.security = HTTPBearer()
        
        self._setup_middleware()
        self._setup_routes()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup API gateway logging"""
        logger = logging.getLogger("MIA.APIGateway")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _setup_middleware(self):
        """Setup API middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify allowed origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # In production, specify allowed hosts
        )
        
        # Custom middleware for logging and metrics
        @self.app.middleware("http")
        async def logging_middleware(request: Request, call_next):
            start_time = time.time()
            
            # Log request
            self.logger.info(f"Request: {request.method} {request.url}")
            
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Record metrics
            record_performance_metric("response_time", process_time, {
                "method": request.method,
                "path": str(request.url.path),
                "status_code": str(response.status_code)
            })
            
            record_usage_metric("api_call", 1, {
                "method": request.method,
                "path": str(request.url.path)
            })
            
            # Add response headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-API-Version"] = "1.0.0"
            
            return response
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "version": "1.0.0"
            }
        
        @self.app.get("/metrics")
        async def get_metrics(credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Get real-time metrics"""
            # Validate authentication
            username = validate_session(credentials.credentials)
            if not username:
                raise HTTPException(status_code=401, detail="Invalid authentication")
            
            return analytics.get_real_time_metrics()
        
        @self.app.post("/v1/chat")
        async def chat_endpoint(request: Request, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Chat endpoint"""
            # Validate authentication
            username = validate_session(credentials.credentials)
            if not username:
                raise HTTPException(status_code=401, detail="Invalid authentication")
            
            # Check rate limits
            if not self._check_rate_limit(username, "chat"):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Process chat request
            data = await request.json()
            message = data.get("message", "")
            
            # In production, this would route to actual chat handler
            response = {
                "response": f"Hello {username}, you said: {message}",
                "timestamp": time.time(),
                "user": username
            }
            
            return response
        
        @self.app.post("/v1/image/generate")
        async def generate_image_endpoint(request: Request, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Image generation endpoint"""
            # Validate authentication
            username = validate_session(credentials.credentials)
            if not username:
                raise HTTPException(status_code=401, detail="Invalid authentication")
            
            # Check rate limits
            if not self._check_rate_limit(username, "image_generation"):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Process image generation request
            data = await request.json()
            prompt = data.get("prompt", "")
            style = data.get("style", "realistic")
            
            # In production, this would route to actual image generator
            response = {
                "image_url": f"/generated/image_{int(time.time())}.png",
                "prompt": prompt,
                "style": style,
                "timestamp": time.time(),
                "user": username
            }
            
            return response
        
        @self.app.post("/v1/voice/synthesize")
        async def synthesize_voice_endpoint(request: Request, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Voice synthesis endpoint"""
            # Validate authentication
            username = validate_session(credentials.credentials)
            if not username:
                raise HTTPException(status_code=401, detail="Invalid authentication")
            
            # Check rate limits
            if not self._check_rate_limit(username, "voice_synthesis"):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Process voice synthesis request
            data = await request.json()
            text = data.get("text", "")
            voice_profile = data.get("voice_profile", "default")
            
            # In production, this would route to actual TTS engine
            response = {
                "audio_url": f"/generated/audio_{int(time.time())}.wav",
                "text": text,
                "voice_profile": voice_profile,
                "timestamp": time.time(),
                "user": username
            }
            
            return response
        
        @self.app.get("/v1/analytics/report/{report_type}")
        async def get_analytics_report(report_type: str, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Get analytics report"""
            # Validate authentication
            username = validate_session(credentials.credentials)
            if not username:
                raise HTTPException(status_code=401, detail="Invalid authentication")
            
            # Check permissions (in production, implement proper RBAC)
            if not self._check_permission(username, "analytics.read"):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            if report_type == "performance":
                report = analytics.generate_performance_report()
            elif report_type == "usage":
                report = analytics.generate_usage_report()
            else:
                raise HTTPException(status_code=400, detail="Invalid report type")
            
            return report
    
    def _check_rate_limit(self, user: str, endpoint: str) -> bool:
        """Check rate limits for user and endpoint"""
        current_time = time.time()
        key = f"{user}:{endpoint}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Clean old entries (last minute)
        self.rate_limits[key] = [
            timestamp for timestamp in self.rate_limits[key]
            if current_time - timestamp < 60
        ]
        
        # Check limit (10 requests per minute for demo)
        if len(self.rate_limits[key]) >= 10:
            return False
        
        # Add current request
        self.rate_limits[key].append(current_time)
        return True
    
    def _check_permission(self, user: str, permission: str) -> bool:
        """Check user permissions"""
        # In production, implement proper RBAC
        # For demo, admin has all permissions
        if user == "admin":
            return True
        
        # Basic permissions for other users
        basic_permissions = [
            "chat.use",
            "image.generate",
            "voice.synthesize"
        ]
        
        return permission in basic_permissions
    
    def register_endpoint(self, endpoint: APIEndpoint):
        """Register new API endpoint"""
        key = f"{endpoint.method}:{endpoint.path}"
        self.endpoints[key] = endpoint
        self.logger.info(f"Registered endpoint: {key}")
    
    def start_server(self):
        """Start the API gateway server"""
        self.logger.info(f"Starting API Gateway on {self.host}:{self.port}")
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
    
    async def start_async(self):
        """Start the API gateway asynchronously"""
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def get_api_documentation(self) -> Dict[str, Any]:
        """Get API documentation"""
        return {
            "title": "MIA Enterprise API Gateway",
            "version": "1.0.0",
            "description": "Enterprise-grade API gateway for MIA platform",
            "endpoints": [
                {
                    "path": "/health",
                    "method": "GET",
                    "description": "Health check endpoint",
                    "auth_required": False
                },
                {
                    "path": "/metrics",
                    "method": "GET",
                    "description": "Get real-time metrics",
                    "auth_required": True
                },
                {
                    "path": "/v1/chat",
                    "method": "POST",
                    "description": "Chat with MIA",
                    "auth_required": True
                },
                {
                    "path": "/v1/image/generate",
                    "method": "POST",
                    "description": "Generate images",
                    "auth_required": True
                },
                {
                    "path": "/v1/voice/synthesize",
                    "method": "POST",
                    "description": "Synthesize voice",
                    "auth_required": True
                },
                {
                    "path": "/v1/analytics/report/{report_type}",
                    "method": "GET",
                    "description": "Get analytics reports",
                    "auth_required": True
                }
            ]
        }

# Global API gateway instance
api_gateway = EnterpriseAPIGateway()

def start_api_gateway(host: str = "0.0.0.0", port: int = 8000):
    """Start the API gateway"""
    gateway = EnterpriseAPIGateway(host, port)
    gateway.start_server()

async def start_api_gateway_async(host: str = "0.0.0.0", port: int = 8000):
    """Start the API gateway asynchronously"""
    gateway = EnterpriseAPIGateway(host, port)
    await gateway.start_async()