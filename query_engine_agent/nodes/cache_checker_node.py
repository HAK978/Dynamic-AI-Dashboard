"""
Cache Checker Node - Check for cached results
"""

import logging
from ..state import QueryEngineState
from ..tools.cache_client import CacheClient

logger = logging.getLogger(__name__)

# Global cache client instance
cache_client = CacheClient(default_ttl=300)

def cache_checker_node(state: QueryEngineState) -> QueryEngineState:
    """Check for cached results before query execution"""

    logger.info("🔍 Checking cache for existing results...")

    try:
        # Generate cache key
        cache_key = cache_client.generate_cache_key({
            'intent_type': state['intent_type'],
            'metric': state['metric'],
            'dimension': state.get('dimension'),
            'chart_type': state['chart_type']
        })

        # Check cache
        cached_data, cache_hit = cache_client.get(cache_key)

        if cache_hit and cached_data:
            # Cache hit - populate state with cached data
            state['formatted_data'] = cached_data.get('data', [])
            state['metadata'] = cached_data.get('metadata', {})
            state['metadata']['cache_hit'] = True
            state['execution_time'] = 0.001  # Minimal cache retrieval time

            logger.info(f"✅ Cache HIT: {len(state['formatted_data'])} records")
        else:
            # Cache miss - continue to query execution
            state['metadata'] = {'cache_hit': False}
            logger.info("❌ Cache MISS: will execute query")

        # Store cache key for later use
        state['cache_key'] = cache_key
        state["nodes_executed"].append("cache_checker")

    except Exception as e:
        error_msg = f"Cache check failed: {str(e)}"
        logger.error(error_msg)
        state["warnings"].append(error_msg)
        state['metadata'] = {'cache_hit': False}

    return state