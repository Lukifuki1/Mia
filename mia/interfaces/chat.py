#!/usr/bin/env python3
"""
MIA Enterprise AGI - Chat Interface
Real-time conversational interface with the AGI core
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from mia.core.agi_core import agi_core, ThoughtType

class MessageType(Enum):
    """Types of chat messages"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    THOUGHT = "thought"
    ERROR = "error"

@dataclass
class ChatMessage:
    """Represents a chat message"""
    id: str
    type: MessageType
    content: str
    timestamp: float
    metadata: Dict[str, Any]

class ChatInterface:
    """
    Real-time chat interface for MIA Enterprise AGI
    
    Provides:
    - WebSocket-based real-time communication
    - Message history and context management
    - Thought streaming and transparency
    - File upload and processing
    - Voice input/output integration
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.active_connections: List[WebSocket] = []
        self.message_history: List[ChatMessage] = []
        self.conversation_context: Dict[str, Any] = {}
        
        # Chat settings
        self.max_history = 100
        self.show_thoughts = True
        self.stream_responses = True
        
        self.logger.info("💬 Chat Interface initialized")
    
    async def initialize(self):
        """Initialize chat interface"""
        self.logger.info("🚀 Initializing Chat Interface...")
        # Chat interface is already initialized in __init__
        self.logger.info("✅ Chat Interface ready")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup chat interface logging"""
        logger = logging.getLogger("MIA.Chat")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        self.active_connections.append(websocket)
        self.logger.info(f"🔌 New chat connection established. Total: {len(self.active_connections)}")
        
        # Send welcome message
        welcome_msg = ChatMessage(
            id=f"msg_{int(time.time() * 1000)}",
            type=MessageType.SYSTEM,
            content="🤖 MIA Enterprise AGI is ready. How can I help you today?",
            timestamp=time.time(),
            metadata={"system": "welcome"}
        )
        
        await self._send_message(websocket, welcome_msg)
        
        # Send recent message history
        if self.message_history:
            for message in self.message_history[-10:]:  # Last 10 messages
                await self._send_message(websocket, message)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.logger.info(f"🔌 Chat connection closed. Total: {len(self.active_connections)}")
    
    async def process_message(self, websocket: WebSocket, message_data: Dict[str, Any]):
        """Process incoming chat message"""
        try:
            # Create user message
            user_message = ChatMessage(
                id=f"msg_{int(time.time() * 1000)}",
                type=MessageType.USER,
                content=message_data.get("content", ""),
                timestamp=time.time(),
                metadata=message_data.get("metadata", {})
            )
            
            # Add to history
            self._add_to_history(user_message)
            
            # Broadcast user message to all connections
            await self._broadcast_message(user_message)
            
            self.logger.info(f"💬 Processing message: {user_message.content[:50]}...")
            
            # Show thinking indicator if enabled
            if self.show_thoughts:
                thinking_msg = ChatMessage(
                    id=f"thinking_{int(time.time() * 1000)}",
                    type=MessageType.THOUGHT,
                    content="🤔 Thinking...",
                    timestamp=time.time(),
                    metadata={"status": "thinking"}
                )
                await self._broadcast_message(thinking_msg)
            
            # Process with AGI core
            if self.stream_responses:
                await self._process_streaming_response(user_message)
            else:
                await self._process_complete_response(user_message)
                
        except Exception as e:
            self.logger.error(f"❌ Error processing message: {e}")
            
            error_msg = ChatMessage(
                id=f"error_{int(time.time() * 1000)}",
                type=MessageType.ERROR,
                content=f"Sorry, I encountered an error: {str(e)}",
                timestamp=time.time(),
                metadata={"error": str(e)}
            )
            
            await self._broadcast_message(error_msg)
    
    async def _process_streaming_response(self, user_message: ChatMessage):
        """Process message with streaming response"""
        
        # Generate thought about the message
        thought = await agi_core.think(user_message.content, ThoughtType.REASONING)
        
        # Show thought process if enabled
        if self.show_thoughts:
            thought_msg = ChatMessage(
                id=f"thought_{thought.id}",
                type=MessageType.THOUGHT,
                content=f"💭 {thought.content[:100]}... (confidence: {thought.confidence:.2f})",
                timestamp=time.time(),
                metadata={
                    "thought_id": thought.id,
                    "confidence": thought.confidence,
                    "reasoning_chain": thought.reasoning_chain
                }
            )
            await self._broadcast_message(thought_msg)
        
        # Generate response using AGI core
        response_content = await agi_core.chat(user_message.content)
        
        # Stream the response
        await self._stream_response(response_content)
    
    async def _process_complete_response(self, user_message: ChatMessage):
        """Process message with complete response"""
        
        # Generate response using AGI core
        response_content = await agi_core.chat(user_message.content)
        
        # Create assistant message
        assistant_message = ChatMessage(
            id=f"msg_{int(time.time() * 1000)}",
            type=MessageType.ASSISTANT,
            content=response_content,
            timestamp=time.time(),
            metadata={"processing_time": 0.5}  # Would be actual processing time
        )
        
        # Add to history and broadcast
        self._add_to_history(assistant_message)
        await self._broadcast_message(assistant_message)
    
    async def _stream_response(self, content: str):
        """Stream response content word by word"""
        if not content or not content.strip():
            content = "I apologize, but I couldn't generate a proper response."
        
        words = content.split()
        if not words:
            words = ["No", "response", "generated."]
        
        streamed_content = ""
        message_id = f"msg_{int(time.time() * 1000)}"
        
        try:
            for i, word in enumerate(words):
                streamed_content += word + " "
                
                # Create streaming message
                stream_msg = ChatMessage(
                    id=message_id,
                    type=MessageType.ASSISTANT,
                    content=streamed_content.strip(),
                    timestamp=time.time(),
                    metadata={
                        "streaming": True,
                        "progress": (i + 1) / len(words),
                        "complete": i == len(words) - 1
                    }
                )
                
                # Check if we still have active connections before sending
                if self.active_connections:
                    await self._broadcast_message(stream_msg)
                    await asyncio.sleep(0.05)  # Small delay for streaming effect
                else:
                    break  # No active connections, stop streaming
            
            # Final complete message only if we have connections
            if self.active_connections:
                final_msg = ChatMessage(
                    id=message_id,
                    type=MessageType.ASSISTANT,
                    content=content,
                    timestamp=time.time(),
                    metadata={"streaming": False, "complete": True}
                )
                
                self._add_to_history(final_msg)
                await self._broadcast_message(final_msg)
                
        except Exception as e:
            self.logger.error(f"❌ Error during streaming: {e}")
            # Send error message if we still have connections
            if self.active_connections:
                error_msg = ChatMessage(
                    id=f"error_{int(time.time() * 1000)}",
                    type=MessageType.ERROR,
                    content="Sorry, there was an error during response streaming.",
                    timestamp=time.time(),
                    metadata={"error": str(e), "complete": True}
                )
                await self._broadcast_message(error_msg)
    
    async def _send_message(self, websocket: WebSocket, message: ChatMessage):
        """Send message to specific WebSocket"""
        try:
            message_dict = asdict(message)
            # Convert enum to string for JSON serialization
            message_dict['type'] = message.type.value
            await websocket.send_text(json.dumps(message_dict))
        except Exception as e:
            self.logger.error(f"❌ Failed to send message: {e}")
    
    async def _broadcast_message(self, message: ChatMessage):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        # Convert message to dict and handle enum serialization
        message_dict = asdict(message)
        message_dict['type'] = message.type.value  # Convert enum to string
        message_json = json.dumps(message_dict)
        
        # Send to all connections
        disconnected = []
        for websocket in self.active_connections.copy():  # Use copy to avoid modification during iteration
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to send to connection: {e}")
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket)
    
    def _add_to_history(self, message: ChatMessage):
        """Add message to history"""
        self.message_history.append(message)
        
        # Maintain history limit
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
    
    async def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return [asdict(msg) for msg in self.message_history]
    
    async def clear_history(self):
        """Clear conversation history"""
        self.message_history.clear()
        self.conversation_context.clear()
        self.logger.info("🗑️ Conversation history cleared")
    
    async def get_chat_statistics(self) -> Dict[str, Any]:
        """Get chat statistics"""
        user_messages = len([msg for msg in self.message_history if msg.type == MessageType.USER])
        assistant_messages = len([msg for msg in self.message_history if msg.type == MessageType.ASSISTANT])
        
        return {
            "total_messages": len(self.message_history),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "active_connections": len(self.active_connections),
            "conversation_started": self.message_history[0].timestamp if self.message_history else None,
            "last_activity": self.message_history[-1].timestamp if self.message_history else None
        }

# Global chat interface instance
chat_interface = ChatInterface()