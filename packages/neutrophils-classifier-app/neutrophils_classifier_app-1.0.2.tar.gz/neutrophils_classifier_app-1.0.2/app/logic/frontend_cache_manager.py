#!/usr/bin/env python3
"""
Frontend Cache Manager
Simple caching system for the Neutrophils Classifier App frontend.
Does not depend on neutrophils-core module and has no smart prefetch functionality.
"""

import os
import time
import threading
from typing import Dict, Optional
from collections import OrderedDict
import numpy as np
import tifffile
import logging


class FrontendImageCache:
    """Simple LRU cache for frontend image loading without smart prefetch"""
    
    def __init__(self, max_memory_mb: int = 512, max_items: int = 100):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.max_items = max_items
        
        self._cache: OrderedDict[str, Dict] = OrderedDict()
        self._memory_usage = 0
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def get(self, key: str) -> Optional[np.ndarray]:
        """Get image from cache, returns None if not found"""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                entry = self._cache.pop(key)
                self._cache[key] = entry
                self._stats['hits'] += 1
                entry['access_time'] = time.time()
                return entry['data'].copy()
            else:
                self._stats['misses'] += 1
                return None
    
    def put(self, key: str, data: np.ndarray) -> None:
        """Store image in cache"""
        data_size = data.nbytes
        
        with self._lock:
            # Check if we need to make space
            while (self._memory_usage + data_size > self.max_memory_bytes or 
                   len(self._cache) >= self.max_items) and self._cache:
                self._evict_lru()
            
            # Add new entry
            entry = {
                'data': data.copy(),
                'size': data_size,
                'access_time': time.time()
            }
            
            self._cache[key] = entry
            self._memory_usage += data_size
    
    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if not self._cache:
            return
        
        key, entry = self._cache.popitem(last=False)  # Remove oldest
        self._memory_usage -= entry['size']
        self._stats['evictions'] += 1
    
    def clear(self) -> None:
        """Clear all cached items"""
        with self._lock:
            self._cache.clear()
            self._memory_usage = 0
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self._lock:
            hit_rate = self._stats['hits'] / (self._stats['hits'] + self._stats['misses']) if (self._stats['hits'] + self._stats['misses']) > 0 else 0
            return {
                **self._stats,
                'hit_rate': hit_rate,
                'current_items': len(self._cache),
                'memory_usage_mb': self._memory_usage / 1024 / 1024,
                'memory_usage_percent': (self._memory_usage / self.max_memory_bytes) * 100
            }


class FrontendImageLoader:
    """Frontend image loader with basic caching (no smart prefetch)"""
    
    def __init__(self, cache_size_mb=512):
        self.cache = FrontendImageCache(max_memory_mb=cache_size_mb)
        self.logger = logging.getLogger(__name__)
    
    def load_image(self, image_path: str, cache_key: Optional[str] = None) -> np.ndarray:
        """Load image with caching"""
        if cache_key is None:
            cache_key = image_path
        
        # Try cache first
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Load from disk
        try:
            data = tifffile.imread(image_path)
            
            # Store in cache
            self.cache.put(cache_key, data)
            
            return data
        except Exception as e:
            self.logger.error(f"Failed to load image {image_path}: {e}")
            raise
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def clear_cache(self) -> None:
        """Clear cache"""
        self.cache.clear()


class FrontendCacheManager:
    """Frontend cache manager singleton"""
    
    def __init__(self, cache_size_mb: int = 512):
        self.cache_size_mb = cache_size_mb
        self.loader = None
    
    def get_loader(self) -> FrontendImageLoader:
        """Get image loader instance"""
        if self.loader is None:
            self.loader = FrontendImageLoader(cache_size_mb=self.cache_size_mb)
        return self.loader


# Global instance
_frontend_cache_manager = None


def get_frontend_cache_manager() -> FrontendCacheManager:
    """Get global frontend cache manager instance"""
    global _frontend_cache_manager
    if _frontend_cache_manager is None:
        _frontend_cache_manager = FrontendCacheManager()
    return _frontend_cache_manager