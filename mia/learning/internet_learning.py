"""
Complete internet learning implementation for MIA
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class InternetLearningEngine:
    """Complete internet learning implementation"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.knowledge_file = data_dir / "internet_knowledge.json"
        self.learning_stats = data_dir / "learning_stats.json"
        self.session = None
        
    async def initialize(self):
        """Initialize internet learning"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        
    async def learn_from_url(self, url: str) -> Dict[str, Any]:
        """Learn from a specific URL"""
        try:
            if not self.session:
                await self.initialize()
                
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Extract knowledge from content
                    knowledge = self._extract_knowledge(content, url)
                    
                    # Store knowledge
                    await self._store_knowledge(knowledge)
                    
                    return knowledge
                    
        except Exception as e:
            logger.error(f"Error learning from {url}: {e}")
            
        return {}
        
    def _extract_knowledge(self, content: str, source: str) -> Dict[str, Any]:
        """Extract knowledge from content"""
        # Simple knowledge extraction
        knowledge = {
            'source': source,
            'timestamp': time.time(),
            'content_length': len(content),
            'title': self._extract_title(content),
            'keywords': self._extract_keywords(content),
            'summary': content[:500] + "..." if len(content) > 500 else content
        }
        return knowledge
        
    def _extract_title(self, content: str) -> str:
        """Extract title from HTML content"""
        import re
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        return title_match.group(1) if title_match else "Unknown Title"
        
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        # Simple keyword extraction
        words = content.lower().split()
        # Filter common words and get unique keywords
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = list(set([word for word in words if len(word) > 3 and word not in common_words]))
        return keywords[:20]  # Return top 20 keywords
        
    async def _store_knowledge(self, knowledge: Dict[str, Any]):
        """Store knowledge to file"""
        try:
            # Load existing knowledge
            existing_knowledge = []
            if self.knowledge_file.exists():
                with open(self.knowledge_file, 'r') as f:
                    existing_knowledge = json.load(f)
                    
            # Add new knowledge
            existing_knowledge.append(knowledge)
            
            # Keep only last 1000 entries
            if len(existing_knowledge) > 1000:
                existing_knowledge = existing_knowledge[-1000:]
                
            # Save knowledge
            with open(self.knowledge_file, 'w') as f:
                json.dump(existing_knowledge, f, indent=2)
                
            # Update stats
            await self._update_stats()
            
        except Exception as e:
            logger.error(f"Error storing knowledge: {e}")
            
    async def _update_stats(self):
        """Update learning statistics"""
        try:
            stats = {
                'last_update': time.time(),
                'total_sources': 0,
                'total_knowledge_items': 0
            }
            
            if self.knowledge_file.exists():
                with open(self.knowledge_file, 'r') as f:
                    knowledge = json.load(f)
                    stats['total_knowledge_items'] = len(knowledge)
                    stats['total_sources'] = len(set(item.get('source', '') for item in knowledge))
                    
            with open(self.learning_stats, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            
    async def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        try:
            if self.learning_stats.exists():
                with open(self.learning_stats, 'r') as f:
                    return json.load(f)
        except:
            pass
            
        return {'total_sources': 0, 'total_knowledge_items': 0}
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

# Test function
async def test_internet_learning():
    """Test internet learning functionality"""
    try:
        engine = InternetLearningEngine(Path("test_data"))
        await engine.initialize()
        
        # Test with a simple URL
        knowledge = await engine.learn_from_url("https://httpbin.org/html")
        
        await engine.cleanup()
        
        return len(knowledge) > 0
    except Exception as e:
        print(f"Internet learning test failed: {e}")
        return False
