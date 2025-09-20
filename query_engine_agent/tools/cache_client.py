"""
Cache Client Tool - Simple in-memory cache for production
"""

import time
import json
import hashlib
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class CacheClient:
    """Simple in-memory cache client (production can use Redis)"""

    def __init__(self, default_ttl: int = 300):
        self.cache = {}
        self.default_ttl = default_ttl
        logger.info("Cache client initialized (in-memory)")

    def get(self, key: str) -> Tuple[Optional[Dict[str, Any]], bool]:
        """Get cached data"""
        try:
            if key in self.cache:
                entry = self.cache[key]

                # Check TTL
                if time.time() - entry['timestamp'] < entry['ttl']:
                    logger.info(f"Cache HIT for key: {key[:12]}...")
                    return entry['data'], True
                else:
                    # Expired
                    del self.cache[key]
                    logger.info(f"Cache EXPIRED for key: {key[:12]}...")

            logger.info(f"Cache MISS for key: {key[:12]}...")
            return None, False

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None, False

    def set(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set cached data"""
        try:
            ttl = ttl or self.default_ttl

            self.cache[key] = {
                'data': data,
                'timestamp': time.time(),
                'ttl': ttl
            }

            logger.info(f"Cache SET for key: {key[:12]}... (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def generate_cache_key(self, query_data: Dict[str, Any]) -> str:
        """Generate cache key from query parameters"""
        key_data = {
            'intent_type': query_data.get('intent_type'),
            'metric': query_data.get('metric'),
            'dimension': query_data.get('dimension'),
            'chart_type': query_data.get('chart_type')
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def should_cache(self, query_data: Dict[str, Any], record_count: int) -> Tuple[bool, int]:
        """Determine if results should be cached and TTL"""

        # Don't cache empty results
        if record_count == 0:
            return False, 0

        # Cache summary queries longer
        if query_data.get('intent_type') == 'summary':
            return True, 600  # 10 minutes

        # Cache trend data moderately
        if query_data.get('intent_type') == 'trend':
            return True, 300  # 5 minutes

        # Cache complex queries briefly
        return True, 180  # 3 minutes

    def clear_all(self) -> bool:
        """Clear all cached data"""
        try:
            self.cache.clear()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        valid_entries = 0
        expired_entries = 0

        current_time = time.time()

        for entry in self.cache.values():
            if current_time - entry['timestamp'] < entry['ttl']:
                valid_entries += 1
            else:
                expired_entries += 1

        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_type': 'in_memory'
        }