#!/usr/bin/env python3
"""
MIA Enterprise AGI - Ollama LLM Backend
Integration with Ollama for local LLM inference
"""

import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass

@dataclass
class OllamaModel:
    """Represents an Ollama model"""
    name: str
    size: int
    modified: str
    digest: str

class OllamaBackend:
    """
    Ollama LLM Backend for MIA Enterprise AGI
    
    Provides:
    - Local LLM inference via Ollama
    - Streaming and non-streaming responses
    - Model management and discovery
    - Performance optimization
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.logger = self._setup_logging()
        self.session: Optional[aiohttp.ClientSession] = None
        self.available_models: List[OllamaModel] = []
        self.default_model = "llama3.2:1b"
        
    def _setup_logging(self) -> logging.Logger:
        """Setup Ollama backend logging"""
        logger = logging.getLogger("MIA.Ollama")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def initialize(self):
        """Initialize Ollama backend"""
        try:
            self.session = aiohttp.ClientSession()
            await self.discover_models()
            self.logger.info(f"🤖 Ollama backend initialized with {len(self.available_models)} models")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Ollama backend: {e}")
            return False
    
    async def discover_models(self):
        """Discover available Ollama models"""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with self.session.get(f"{self.base_url}/api/tags", timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    self.available_models = [
                        OllamaModel(
                            name=model["name"],
                            size=model["size"],
                            modified=model["modified_at"],
                            digest=model["digest"]
                        )
                        for model in data.get("models", [])
                    ]
                    self.logger.info(f"🔍 Discovered {len(self.available_models)} Ollama models")
                else:
                    self.logger.warning(f"⚠️ Failed to discover models: HTTP {response.status}")
        except Exception as e:
            self.logger.error(f"❌ Error discovering models: {e}")
    
    async def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> str:
        """Generate response from Ollama model"""
        if not self.session:
            await self.initialize()
        
        model = model or self.default_model
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                **kwargs
            }
            
            if stream:
                return await self._generate_streaming(payload)
            else:
                return await self._generate_non_streaming(payload)
                
        except Exception as e:
            self.logger.error(f"❌ Error generating response: {e}")
            return f"Error: {str(e)}"
    
    async def _generate_non_streaming(self, payload: Dict[str, Any]) -> str:
        """Generate non-streaming response"""
        try:
            timeout = aiohttp.ClientTimeout(total=60)  # Increased timeout
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", "")
                else:
                    self.logger.error(f"❌ HTTP Error: {response.status}")
                    return f"HTTP Error: {response.status}"
        except asyncio.TimeoutError:
            self.logger.error("❌ Ollama request timed out")
            return "I apologize, but the response took too long to generate. Please try again."
        except Exception as e:
            self.logger.error(f"❌ Non-streaming generation error: {e}")
            return f"Error: {str(e)}"
    
    async def _generate_streaming(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        try:
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
                else:
                    yield f"HTTP Error: {response.status}"
        except Exception as e:
            self.logger.error(f"❌ Streaming generation error: {e}")
            yield f"Error: {str(e)}"
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> str:
        """Chat completion with message history"""
        if not self.session:
            await self.initialize()
        
        model = model or self.default_model
        
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream,
                **kwargs
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=timeout
            ) as response:
                if response.status == 200:
                    if stream:
                        full_response = ""
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    if "message" in data and "content" in data["message"]:
                                        content = data["message"]["content"]
                                        full_response += content
                                        if data.get("done", False):
                                            break
                                except json.JSONDecodeError:
                                    continue
                        return full_response
                    else:
                        data = await response.json()
                        return data.get("message", {}).get("content", "")
                else:
                    return f"HTTP Error: {response.status}"
        except Exception as e:
            self.logger.error(f"❌ Chat completion error: {e}")
            return f"Error: {str(e)}"
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model},
                timeout=timeout
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            self.logger.error(f"❌ Error getting model info: {e}")
            return {"error": str(e)}
    
    async def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            timeout = aiohttp.ClientTimeout(total=5)
            async with self.session.get(f"{self.base_url}/api/tags", timeout=timeout) as response:
                return response.status == 200
        except Exception:
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None
        self.logger.info("🧹 Ollama backend cleaned up")

# Global Ollama backend instance
ollama_backend = OllamaBackend()