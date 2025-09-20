"""
Cache Manager Node - Store results in cache
"""

import logging
from ..state import QueryEngineState
from ..tools.cache_client import CacheClient

logger = logging.getLogger(__name__)

# Global cache client instance (shared with cache_checker)
cache_client = CacheClient(default_ttl=300)

def cache_manager_node(state: QueryEngineState) -> QueryEngineState:
    """Store query results in cache for future requests"""

    logger.info("💾 Managing cache storage...")

    try:
        # Only cache if we have successful results and no cache hit
        if (state.get('formatted_data') and
            len(state['formatted_data']) > 0 and
            not state.get('metadata', {}).get('cache_hit', False) and
            not state.get('error')):

            # Determine if we should cache these results
            should_cache, ttl = cache_client.should_cache(
                query_data={
                    'intent_type': state['intent_type'],
                    'metric': state['metric'],
                    'dimension': state.get('dimension'),
                    'chart_type': state['chart_type']
                },
                record_count=len(state['formatted_data'])
            )

            if should_cache:
                cache_key = state.get('cache_key')
                if cache_key:
                    # Prepare data for caching
                    cache_data = {
                        'data': state['formatted_data'],
                        'metadata': state.get('metadata', {})
                    }

                    # Store in cache
                    success = cache_client.set(cache_key, cache_data, ttl)

                    if success:
                        logger.info(f"✅ Results cached (TTL: {ttl}s)")
                        state['metadata']['cached'] = True
                        state['metadata']['cache_ttl'] = ttl
                    else:
                        logger.warning("❌ Cache storage failed")
                        state['warnings'].append("Cache storage failed")
                else:
                    logger.warning("No cache key available for storage")
            else:
                logger.info("⏭️ Results not suitable for caching")
        else:
            logger.info("⏭️ Skipping cache storage (cache hit or empty results)")

        state["nodes_executed"].append("cache_manager")

    except Exception as e:
        error_msg = f"Cache management failed: {str(e)}"
        logger.error(error_msg)
        state["warnings"].append(error_msg)

    return state