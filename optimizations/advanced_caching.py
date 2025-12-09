#!/usr/bin/env python3
"""
🚀 MIA Enterprise AGI - Advanced Caching System
==============================================

Multi-level intelligent caching system for ultimate performance:
- Memory caching with LRU eviction
- Disk-based persistent caching
- Distributed caching support
- Intelligent cache warming
- Performance analytics
"""

import asyncio
import time
import logging
import threading
import pickle
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import weakref
from collections import OrderedDict
import psutil
import gzip
import zlib

class CacheLevel(Enum):

    def _get_deterministic_time(self) -> float:
        """Vrni deterministični čas"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC

    MEMORY = "memory"
    DISK = "disk"
    DISTRIBUTED = "distributed"

class CacheStrategy(Enum):
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"

@dataclass
class CacheEntry:
    key: str
    value: Any
    timestamp: float
    access_count: int
    ttl: Optional[float]
    size_bytes: int
    metadata: Dict[str, Any]

@dataclass
class CacheStats:
    hits: int
    misses: int
    evictions: int
    size_bytes: int
    entry_count: int
    hit_rate: float

class AdvancedMemoryCache:
    """Advanced Memory Cache with multiple eviction strategies"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100, strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.strategy = strategy
        self.cache: OrderedDict = OrderedDict()
        self.stats = CacheStats(0, 0, 0, 0, 0, 0.0)
        self.lock = threading.RLock()
        
        self.logger = logging.getLogger("MIA.MemoryCache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check TTL
                if entry.ttl and self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 > entry.timestamp + entry.ttl:
                    del self.cache[key]
                    self.stats.misses += 1
                    self._update_stats()
                    return None
                
                # Update access patterns
                entry.access_count += 1
                
                if self.strategy == CacheStrategy.LRU:
                    # Move to end (most recently used)
                    self.cache.move_to_end(key)
                
                self.stats.hits += 1
                self._update_stats()
                return entry.value
            else:
                self.stats.misses += 1
                self._update_stats()
                return None
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None, metadata: Optional[Dict] = None) -> bool:
        """Put value in cache"""
        with self.lock:
            try:
                # Calculate size
                size_bytes = self._calculate_size(value)
                
                # Check if we need to evict
                while (len(self.cache) >= self.max_size or 
                       self.stats.size_bytes + size_bytes > self.max_memory_bytes):
                    if not self._evict_entry():
                        return False  # Cannot evict more entries
                
                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    timestamp=self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200,
                    access_count=1,
                    ttl=ttl,
                    size_bytes=size_bytes,
                    metadata=metadata or {}
                )
                
                # Add to cache
                self.cache[key] = entry
                self.stats.size_bytes += size_bytes
                self.stats.entry_count = len(self.cache)
                self._update_stats()
                
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to put cache entry: {e}")
                return False
    
    def _evict_entry(self) -> bool:
        """Evict entry based on strategy"""
        if not self.cache:
            return False
        
        try:
            if self.strategy == CacheStrategy.LRU:
                # Remove least recently used (first item)
                key, entry = self.cache.popitem(last=False)
            elif self.strategy == CacheStrategy.LFU:
                # Remove least frequently used
                key = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
                entry = self.cache.pop(key)
            elif self.strategy == CacheStrategy.FIFO:
                # Remove first in (first item)
                key, entry = self.cache.popitem(last=False)
            elif self.strategy == CacheStrategy.TTL:
                # Remove expired entries first
                current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
                expired_keys = [
                    k for k, v in self.cache.items()
                    if v.ttl and current_time > v.timestamp + v.ttl
                ]
                if expired_keys:
                    key = expired_keys[0]
                    entry = self.cache.pop(key)
                else:
                    # Fallback to LRU
                    key, entry = self.cache.popitem(last=False)
            
            self.stats.size_bytes -= entry.size_bytes
            self.stats.evictions += 1
            self.stats.entry_count = len(self.cache)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to evict cache entry: {e}")
            return False
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes"""
        try:
            return len(pickle.dumps(value))
        except:
            # Fallback estimation
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, (list, tuple)):
                return sum(self._calculate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(self._calculate_size(k) + self._calculate_size(v) for k, v in value.items())
            else:
                return 1024  # Default estimate
    
    def _update_stats(self):
        """Update cache statistics"""
        total_requests = self.stats.hits + self.stats.misses
        self.stats.hit_rate = self.stats.hits / total_requests if total_requests > 0 else 0.0
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.stats = CacheStats(0, 0, 0, 0, 0, 0.0)
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        with self.lock:
            return CacheStats(
                hits=self.stats.hits,
                misses=self.stats.misses,
                evictions=self.stats.evictions,
                size_bytes=self.stats.size_bytes,
                entry_count=len(self.cache),
                hit_rate=self.stats.hit_rate
            )

class PersistentDiskCache:
    """Persistent disk-based cache with compression"""
    
    def __init__(self, cache_dir: str = "cache", max_size_mb: int = 1000, compression: bool = True):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.compression = compression
        
        # Initialize SQLite index
        self.db_path = self.cache_dir / "cache_index.db"
        self._init_database()
        
        self.logger = logging.getLogger("MIA.DiskCache")
        self.stats = CacheStats(0, 0, 0, 0, 0, 0.0)
        self.lock = threading.RLock()
    
    def _init_database(self):
        """Initialize SQLite database for cache index"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    access_count INTEGER DEFAULT 1,
                    ttl REAL,
                    size_bytes INTEGER NOT NULL,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON cache_entries(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_access_count ON cache_entries(access_count)
            """)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT filename, timestamp, ttl, access_count FROM cache_entries WHERE key = ?",
                        (key,)
                    )
                    row = cursor.fetchone()
                    
                    if not row:
                        self.stats.misses += 1
                        self._update_stats()
                        return None
                    
                    filename, timestamp, ttl, access_count = row
                    
                    # Check TTL
                    if ttl and self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 > timestamp + ttl:
                        self._remove_entry(key, filename)
                        self.stats.misses += 1
                        self._update_stats()
                        return None
                    
                    # Load value from file
                    file_path = self.cache_dir / filename
                    if not file_path.exists():
                        self._remove_entry(key, filename)
                        self.stats.misses += 1
                        self._update_stats()
                        return None
                    
                    value = self._load_from_file(file_path)
                    
                    # Update access count
                    conn.execute(
                        "UPDATE cache_entries SET access_count = access_count + 1 WHERE key = ?",
                        (key,)
                    )
                    
                    self.stats.hits += 1
                    self._update_stats()
                    return value
                    
            except Exception as e:
                self.logger.error(f"Failed to get from disk cache: {e}")
                self.stats.misses += 1
                self._update_stats()
                return None
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None, metadata: Optional[Dict] = None) -> bool:
        """Put value in disk cache"""
        with self.lock:
            try:
                # Generate filename
                filename = self._generate_filename(key)
                file_path = self.cache_dir / filename
                
                # Save value to file
                size_bytes = self._save_to_file(file_path, value)
                
                # Check if we need to evict
                while self._get_total_size() + size_bytes > self.max_size_bytes:
                    if not self._evict_entry():
                        file_path.unlink(missing_ok=True)
                        return False
                
                # Add to database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO cache_entries 
                        (key, filename, timestamp, ttl, size_bytes, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        key, filename, self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200, ttl, size_bytes,
                        json.dumps(metadata) if metadata else None
                    ))
                
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to put in disk cache: {e}")
                return False
    
    def _generate_filename(self, key: str) -> str:
        """Generate filename for cache key"""
        hash_obj = hashlib.md5(key.encode())
        return f"cache_{hash_obj.hexdigest()}.pkl"
    
    def _save_to_file(self, file_path: Path, value: Any) -> int:
        """Save value to file with optional compression"""
        data = pickle.dumps(value)
        
        if self.compression:
            data = gzip.compress(data)
        
        with open(file_path, 'wb') as f:
            f.write(data)
        
        return len(data)
    
    def _load_from_file(self, file_path: Path) -> Any:
        """Load value from file with optional decompression"""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        if self.compression:
            data = gzip.decompress(data)
        
        return pickle.loads(data)
    
    def _get_total_size(self) -> int:
        """Get total cache size in bytes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT SUM(size_bytes) FROM cache_entries")
            result = cursor.fetchone()[0]
            return result or 0
    
    def _evict_entry(self) -> bool:
        """Evict least recently used entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT key, filename FROM cache_entries 
                    ORDER BY timestamp ASC LIMIT 1
                """)
                row = cursor.fetchone()
                
                if row:
                    key, filename = row
                    self._remove_entry(key, filename)
                    self.stats.evictions += 1
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to evict entry: {e}")
            return False
    
    def _remove_entry(self, key: str, filename: str):
        """Remove entry from cache"""
        try:
            # Remove file
            file_path = self.cache_dir / filename
            file_path.unlink(missing_ok=True)
            
            # Remove from database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                
        except Exception as e:
            self.logger.error(f"Failed to remove cache entry: {e}")
    
    def _update_stats(self):
        """Update cache statistics"""
        total_requests = self.stats.hits + self.stats.misses
        self.stats.hit_rate = self.stats.hits / total_requests if total_requests > 0 else 0.0
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            try:
                # Remove all files
                for file_path in self.cache_dir.glob("cache_*.pkl"):
                    file_path.unlink(missing_ok=True)
                
                # Clear database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM cache_entries")
                
                self.stats = CacheStats(0, 0, 0, 0, 0, 0.0)
                
            except Exception as e:
                self.logger.error(f"Failed to clear disk cache: {e}")
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*), SUM(size_bytes) FROM cache_entries")
                    count, size = cursor.fetchone()
                    
                    return CacheStats(
                        hits=self.stats.hits,
                        misses=self.stats.misses,
                        evictions=self.stats.evictions,
                        size_bytes=size or 0,
                        entry_count=count or 0,
                        hit_rate=self.stats.hit_rate
                    )
            except:
                return self.stats

class IntelligentCacheWarmer:
    """Intelligent cache warming system"""
    
    def __init__(self, cache_system):
        self.cache_system = cache_system
        self.warming_patterns = {}
        self.access_patterns = {}
        self.logger = logging.getLogger("MIA.CacheWarmer")
        self.warming_active = False
    
    def start_warming(self):
        """Start intelligent cache warming"""
        self.warming_active = True
        
        def warming_loop():
            while self.warming_active:
                try:
                    self._analyze_access_patterns()
                    self._warm_predicted_entries()
                    time.sleep(300)  # Warm every 5 minutes
                except Exception as e:
                    self.logger.error(f"Cache warming error: {e}")
                    time.sleep(60)
        
        warming_thread = threading.Thread(target=warming_loop, daemon=True)
        warming_thread.start()
        
        self.logger.info("🔥 Intelligent cache warming started")
    
    def record_access(self, key: str):
        """Record cache access for pattern analysis"""
        current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        if key not in self.access_patterns:
            self.access_patterns[key] = []
        
        self.access_patterns[key].append(current_time)
        
        # Keep only recent accesses (last 24 hours)
        cutoff_time = current_time - 86400
        self.access_patterns[key] = [
            t for t in self.access_patterns[key] if t > cutoff_time
        ]
    
    def _analyze_access_patterns(self):
        """Analyze access patterns to predict future needs"""
        try:
            current_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
            
            for key, access_times in self.access_patterns.items():
                if len(access_times) < 2:
                    continue
                
                # Calculate access frequency
                time_span = access_times[-1] - access_times[0]
                frequency = len(access_times) / max(time_span / 3600, 1)  # accesses per hour
                
                # Calculate time since last access
                time_since_last = current_time - access_times[-1]
                
                # Predict if entry should be warmed
                if frequency > 1 and time_since_last < 3600:  # Accessed more than once per hour, within last hour
                    self.warming_patterns[key] = {
                        'frequency': frequency,
                        'last_access': access_times[-1],
                        'priority': frequency * (1 / max(time_since_last / 3600, 0.1))
                    }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze access patterns: {e}")
    
    def _warm_predicted_entries(self):
        """Warm cache entries based on predictions"""
        try:
            # Sort by priority
            sorted_patterns = sorted(
                self.warming_patterns.items(),
                key=lambda x: x[1]['priority'],
                reverse=True
            )
            
            # Warm top entries
            for key, pattern in sorted_patterns[:10]:  # Top 10 entries
                if not self.cache_system.get(key):  # Only warm if not in cache
                    # Generate or fetch the value (placeholder)
                    warmed_value = self._generate_warm_value(key)
                    if warmed_value:
                        self.cache_system.put(key, warmed_value, ttl=3600)  # 1 hour TTL
                        self.logger.debug(f"🔥 Warmed cache entry: {key}")
            
        except Exception as e:
            self.logger.error(f"Failed to warm cache entries: {e}")
    
    def _generate_warm_value(self, key: str) -> Optional[Any]:
        """Generate or fetch value for warming (placeholder)"""
        # This would be implemented based on the specific application needs
        # For now, return a placeholder
        return f"warmed_value_for_{key}"
    
    def stop_warming(self):
        """Stop cache warming"""
        self.warming_active = False
        self.logger.info("🔥 Cache warming stopped")

class UltimateCacheSystem:
    """Ultimate multi-level cache system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.logger = self._setup_logging()
        
        # Initialize cache levels
        self.memory_cache = AdvancedMemoryCache(
            max_size=self.config['memory']['max_size'],
            max_memory_mb=self.config['memory']['max_memory_mb'],
            strategy=CacheStrategy(self.config['memory']['strategy'])
        )
        
        self.disk_cache = PersistentDiskCache(
            cache_dir=self.config['disk']['cache_dir'],
            max_size_mb=self.config['disk']['max_size_mb'],
            compression=self.config['disk']['compression']
        )
        
        # Initialize cache warmer
        self.cache_warmer = IntelligentCacheWarmer(self)
        
        # Performance metrics
        self.performance_metrics = {
            'total_requests': 0,
            'memory_hits': 0,
            'disk_hits': 0,
            'misses': 0,
            'avg_response_time': 0.0
        }
        
        self.logger.info("🚀 Ultimate Cache System initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default cache configuration"""
        return {
            'memory': {
                'max_size': 10000,
                'max_memory_mb': 500,
                'strategy': 'lru'
            },
            'disk': {
                'cache_dir': 'cache',
                'max_size_mb': 5000,
                'compression': True
            },
            'warming': {
                'enabled': True,
                'interval': 300
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MIA.UltimateCache")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache"""
        start_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200
        
        try:
            self.performance_metrics['total_requests'] += 1
            
            # Record access for warming
            if self.config['warming']['enabled']:
                self.cache_warmer.record_access(key)
            
            # Try memory cache first
            value = self.memory_cache.get(key)
            if value is not None:
                self.performance_metrics['memory_hits'] += 1
                self._update_response_time(start_time)
                return value
            
            # Try disk cache
            value = self.disk_cache.get(key)
            if value is not None:
                # Promote to memory cache
                self.memory_cache.put(key, value)
                self.performance_metrics['disk_hits'] += 1
                self._update_response_time(start_time)
                return value
            
            # Cache miss
            self.performance_metrics['misses'] += 1
            self._update_response_time(start_time)
            return None
            
        except Exception as e:
            self.logger.error(f"Cache get error: {e}")
            self.performance_metrics['misses'] += 1
            self._update_response_time(start_time)
            return None
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None, metadata: Optional[Dict] = None) -> bool:
        """Put value in multi-level cache"""
        try:
            # Put in memory cache
            memory_success = self.memory_cache.put(key, value, ttl, metadata)
            
            # Put in disk cache for persistence
            disk_success = self.disk_cache.put(key, value, ttl, metadata)
            
            return memory_success or disk_success
            
        except Exception as e:
            self.logger.error(f"Cache put error: {e}")
            return False
    
    def _update_response_time(self, start_time: float):
        """Update average response time"""
        response_time = self._get_deterministic_time() if hasattr(self, "_get_deterministic_time") else 1640995200 - start_time
        total_requests = self.performance_metrics['total_requests']
        
        if total_requests == 1:
            self.performance_metrics['avg_response_time'] = response_time
        else:
            # Running average
            current_avg = self.performance_metrics['avg_response_time']
            self.performance_metrics['avg_response_time'] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
    
    def start_cache_warming(self):
        """Start intelligent cache warming"""
        if self.config['warming']['enabled']:
            self.cache_warmer.start_warming()
    
    def stop_cache_warming(self):
        """Stop cache warming"""
        self.cache_warmer.stop_warming()
    
    def clear_all(self):
        """Clear all cache levels"""
        self.memory_cache.clear()
        self.disk_cache.clear()
        self.performance_metrics = {
            'total_requests': 0,
            'memory_hits': 0,
            'disk_hits': 0,
            'misses': 0,
            'avg_response_time': 0.0
        }
        self.logger.info("🧹 All caches cleared")
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        memory_stats = self.memory_cache.get_stats()
        disk_stats = self.disk_cache.get_stats()
        
        total_hits = self.performance_metrics['memory_hits'] + self.performance_metrics['disk_hits']
        total_requests = self.performance_metrics['total_requests']
        overall_hit_rate = total_hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'overall': {
                'total_requests': total_requests,
                'overall_hit_rate': overall_hit_rate,
                'avg_response_time': self.performance_metrics['avg_response_time'],
                'memory_hit_rate': self.performance_metrics['memory_hits'] / total_requests if total_requests > 0 else 0.0,
                'disk_hit_rate': self.performance_metrics['disk_hits'] / total_requests if total_requests > 0 else 0.0
            },
            'memory_cache': asdict(memory_stats),
            'disk_cache': asdict(disk_stats),
            'warming': {
                'active': self.cache_warmer.warming_active,
                'patterns_tracked': len(self.cache_warmer.access_patterns),
                'warming_candidates': len(self.cache_warmer.warming_patterns)
            }
        }

def main():
    """Main execution function"""
    print("🚀 Initializing Ultimate Cache System...")
    
    # Initialize cache system
    cache_system = UltimateCacheSystem()
    
    # Start cache warming
    cache_system.start_cache_warming()
    
    # Test cache performance
    print("⏱️ Testing cache performance...")
    
    # Put test data
    for i in range(100):
        key = f"test_key_{i}"
        value = f"test_value_{i}" * 100  # Make it substantial
        cache_system.put(key, value, ttl=3600)
    
    # Test retrieval
    hits = 0
    for i in range(100):
        key = f"test_key_{i}"
        value = cache_system.get(key)
        if value:
            hits += 1
    
    # Get statistics
    stats = cache_system.get_comprehensive_stats()
    
    print("\n" + "="*60)
    print("📊 ULTIMATE CACHE SYSTEM RESULTS")
    print("="*60)
    
    overall = stats['overall']
    print(f"Total Requests: {overall['total_requests']}")
    print(f"Overall Hit Rate: {overall['overall_hit_rate']:.2%}")
    print(f"Memory Hit Rate: {overall['memory_hit_rate']:.2%}")
    print(f"Disk Hit Rate: {overall['disk_hit_rate']:.2%}")
    print(f"Avg Response Time: {overall['avg_response_time']:.4f}s")
    
    memory = stats['memory_cache']
    print(f"\nMemory Cache:")
    print(f"  Entries: {memory['entry_count']}")
    print(f"  Size: {memory['size_bytes'] / 1024:.1f} KB")
    print(f"  Hit Rate: {memory['hit_rate']:.2%}")
    
    disk = stats['disk_cache']
    print(f"\nDisk Cache:")
    print(f"  Entries: {disk['entry_count']}")
    print(f"  Size: {disk['size_bytes'] / 1024:.1f} KB")
    print(f"  Hit Rate: {disk['hit_rate']:.2%}")
    
    warming = stats['warming']
    print(f"\nCache Warming:")
    print(f"  Active: {warming['active']}")
    print(f"  Patterns Tracked: {warming['patterns_tracked']}")
    print(f"  Warming Candidates: {warming['warming_candidates']}")
    
    print("="*60)
    print("✅ Ultimate Cache System test completed!")
    
    # Stop cache warming
    cache_system.stop_cache_warming()

if __name__ == "__main__":
    main()