"""Cache service for storing user sessions and application data."""

import json
import time
import threading
import os
from pathlib import Path
from typing import Optional, Any, Dict


class CacheService:
    """
    File-based cache service with expiration and automatic cleanup.
    Thread-safe implementation for internal app use.
    """
    
    def __init__(self, default_ttl: int = 3600, cleanup_interval: int = 300, cache_file: Optional[str] = None):
        """
        Initialize cache service.
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
            cleanup_interval: Interval in seconds for automatic cleanup (default: 5 minutes)
            cache_file: Path to cache file (default: cache.json in project root)
        """
        if cache_file is None:
            # Default to cache.json in project root
            project_root = Path(__file__).parent.parent.parent
            cache_file = str(project_root / "cache.json")
        
        self._cache_file = cache_file
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        self._default_ttl = default_ttl
        self._cleanup_interval = cleanup_interval
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'expired': 0
        }
        self._last_cleanup = time.time()
        self._last_save = time.time()
        
        # Load existing cache from file
        self._load_cache()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
            # Load fresh data from file
            self._load_cache()
            
            # Auto-cleanup expired entries periodically
            self._auto_cleanup()
            
            if key not in self._cache:
                self._stats['misses'] += 1
                return None
            
            value, expire_time = self._cache[key]
            current_time = time.time()
            
            if expire_time is None or current_time < expire_time:
                self._stats['hits'] += 1
                return value
            else:
                # Expired, remove from cache
                del self._cache[key]
                self._save_cache()
                self._stats['expired'] += 1
                self._stats['misses'] += 1
                return None
    
    def set(self, key: str, value: Any, expire: Optional[int] = None):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds (None uses default_ttl)
        """
        with self._lock:
            # Load existing cache first
            self._load_cache()
            
            expire_time = time.time() + (expire if expire is not None else self._default_ttl)
            self._cache[key] = (value, expire_time)
            self._stats['sets'] += 1
            
            # Save to file
            self._save_cache()
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            # Load existing cache first
            self._load_cache()
            
            if key in self._cache:
                del self._cache[key]
                self._stats['deletes'] += 1
                self._save_cache()
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache (and is not expired).
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and is valid, False otherwise
        """
        with self._lock:
            # Load fresh data from file
            self._load_cache()
            
            self._auto_cleanup()
            if key not in self._cache:
                return False
            
            _, expire_time = self._cache[key]
            if expire_time is None or time.time() < expire_time:
                return True
            else:
                # Expired, remove it
                del self._cache[key]
                self._save_cache()
                self._stats['expired'] += 1
                return False
    
    def clear(self):
        """Clear all cache."""
        with self._lock:
            self._cache.clear()
            self._stats = {
                'hits': 0,
                'misses': 0,
                'sets': 0,
                'deletes': 0,
                'expired': 0
            }
            self._save_cache()
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self._stats,
                'size': len(self._cache),
                'hit_rate': round(hit_rate, 2)
            }
    
    def _auto_cleanup(self):
        """Automatically cleanup expired entries periodically."""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = current_time
        expired_keys = []
        
        for key, (_, expire_time) in self._cache.items():
            if expire_time is not None and current_time >= expire_time:
                expired_keys.append(key)
        
        if expired_keys:
            for key in expired_keys:
                del self._cache[key]
            self._stats['expired'] += len(expired_keys)
            self._save_cache()
    
    def cleanup_expired(self) -> int:
        """
        Manually cleanup all expired entries.
        
        Returns:
            Number of expired entries removed
        """
        with self._lock:
            # Load fresh data from file
            self._load_cache()
            
            current_time = time.time()
            expired_keys = []
            
            for key, (_, expire_time) in self._cache.items():
                if expire_time is not None and current_time >= expire_time:
                    expired_keys.append(key)
            
            if expired_keys:
                for key in expired_keys:
                    del self._cache[key]
                self._stats['expired'] += len(expired_keys)
                self._save_cache()
            
            return len(expired_keys)
    
    def get_all_keys(self, pattern: Optional[str] = None) -> list:
        """
        Get all cache keys, optionally filtered by pattern.
        
        Args:
            pattern: Optional pattern to filter keys (simple substring match)
            
        Returns:
            List of cache keys
        """
        with self._lock:
            # Load fresh data from file
            self._load_cache()
            
            self._auto_cleanup()
            keys = list(self._cache.keys())
            
            if pattern:
                keys = [k for k in keys if pattern in k]
            
            return keys
    
    def get_size(self) -> int:
        """Get current cache size (number of entries)."""
        with self._lock:
            # Load fresh data from file
            self._load_cache()
            
            self._auto_cleanup()
            return len(self._cache)
    
    def _load_cache(self):
        """Load cache data from file."""
        if not os.path.exists(self._cache_file):
            self._cache: Dict[str, tuple] = {}
            return
        
        try:
            with open(self._cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._cache = {}
                current_time = time.time()
                
                # Restore cache entries, filtering out expired ones
                for key, entry in data.items():
                    value = entry.get('value')
                    expire_time = entry.get('expire_time')
                    
                    # Skip expired entries
                    if expire_time is not None and current_time >= expire_time:
                        continue
                    
                    self._cache[key] = (value, expire_time)
        except (json.JSONDecodeError, IOError, KeyError) as e:
            # If file is corrupted or missing, start with empty cache
            print(f"Warning: Failed to load cache from file: {e}")
            self._cache: Dict[str, tuple] = {}
    
    def _save_cache(self):
        """Save cache data to file."""
        try:
            # Create directory if it doesn't exist
            cache_dir = os.path.dirname(self._cache_file)
            if cache_dir and not os.path.exists(cache_dir):
                os.makedirs(cache_dir, exist_ok=True)
            
            # Prepare data for JSON serialization
            data = {}
            for key, (value, expire_time) in self._cache.items():
                data[key] = {
                    'value': value,
                    'expire_time': expire_time
                }
            
            # Write to file atomically
            temp_file = self._cache_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Replace original file with temp file
            if os.path.exists(self._cache_file):
                os.replace(temp_file, self._cache_file)
            else:
                os.rename(temp_file, self._cache_file)
            
            self._last_save = time.time()
        except (IOError, OSError) as e:
            print(f"Warning: Failed to save cache to file: {e}")

