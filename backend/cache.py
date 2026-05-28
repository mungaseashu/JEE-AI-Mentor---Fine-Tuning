# ==============================================================================
# JEE MENTOR AI - REDIS & IN-MEMORY HYBRID CACHING LAYER
# ==============================================================================
import json
import time
import threading
from typing import Any, Optional
from backend.config import settings

class JEECache:
    def __init__(self):
        """Initializes the active cache. Auto-toggles between Redis and Local memory."""
        self.redis_client = None
        self.local_store = {}
        self.local_expiry = {}
        self.lock = threading.Lock()
        self._initialize_cache()

    def _initialize_cache(self):
        """Attempts to establish Redis connection. Falls back to local memory if offline."""
        if settings.REDIS_URL:
            try:
                import redis
                print(f"[INFO] Connecting to Redis at: {settings.REDIS_URL}")
                self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                # Quick health ping
                self.redis_client.ping()
                print("[SUCCESS] Active Redis Connection established successfully.")
                return
            except Exception as e:
                print(f"[WARNING] Redis connection failed: {e}")
                
        print("[INFO] Redis offline. Initializing Thread-Safe Local In-Memory Cache Fallback.")
        self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """Queries the cache. Automatically deserializes JSON values if applicable."""
        if self.redis_client is not None:
            try:
                val = self.redis_client.get(key)
                if val:
                    return json.loads(val)
                return None
            except Exception as re:
                print(f"[WARNING] Redis GET error for key '{key}': {re}")
                return None
        
        # Local Memory Lookup with Expiry Validation
        with self.lock:
            if key in self.local_store:
                # Check for expiration
                expiry = self.local_expiry.get(key, 0)
                if expiry == 0 or expiry > time.time():
                    return self.local_store[key]
                else:
                    # Clear expired key
                    self.local_store.pop(key, None)
                    self.local_expiry.pop(key, None)
            return None

    def set(self, key: str, value: Any, expire_seconds: int = 3600):
        """Saves a value in the cache, serializing it to JSON and enforcing TTL."""
        serialized_val = json.dumps(value)
        
        if self.redis_client is not None:
            try:
                self.redis_client.set(key, serialized_val, ex=expire_seconds)
                return
            except Exception as re:
                print(f"[WARNING] Redis SET error for key '{key}': {re}")
                # Fallback to local memory on Redis crash
                pass

        # Local Memory Set
        with self.lock:
            self.local_store[key] = value
            self.local_expiry[key] = time.time() + expire_seconds

    def delete(self, key: str):
        """Evicts a key from the cache."""
        if self.redis_client is not None:
            try:
                self.redis_client.delete(key)
                return
            except Exception as re:
                print(f"[WARNING] Redis DELETE error for key '{key}': {re}")
                pass
                
        with self.lock:
            self.local_store.pop(key, None)
            self.local_expiry.pop(key, None)

    def clear(self):
        """Clears all cached items."""
        if self.redis_client is not None:
            try:
                self.redis_client.flushdb()
                return
            except Exception as re:
                print(f"[WARNING] Redis FLUSHDB error: {re}")
                pass
                
        with self.lock:
            self.local_store.clear()
            self.local_expiry.clear()

# Global cache instance
jee_cache = JEECache()
