"""
Error Handler Node - Handle query failures with fallbacks
"""

import logging
from ..state import QueryEngineState

logger = logging.getLogger(__name__)

def error_handler_node(state: QueryEngineState) -> QueryEngineState:
    """Handle query execution errors and provide fallback responses"""

    logger.info("⚠️ Handling query execution error...")

    try:
        error_message = state.get('error', 'Unknown error')
        logger.error(f"Original error: {error_message}")

        # Generate fallback data based on intent type
        fallback_data = _generate_fallback_data(state, error_message)

        # Update state with fallback
        state['formatted_data'] = fallback_data
        state['metadata'] = {
            'status': 'error_handled',
            'original_error': error_message,
            'fallback_used': True,
            'cache_hit': False,
            'total_records': len(fallback_data)
        }

        # Clear the error since we've handled it
        state['error'] = None

        state["nodes_executed"].append("error_handler")

        logger.info(f"✅ Error handled with {len(fallback_data)} fallback records")

    except Exception as e:
        logger.error(f"Error handler failed: {e}")
        # If error handler fails, provide minimal fallback
        state['formatted_data'] = [{'error': True, 'message': 'System error - please try again'}]
        state['metadata'] = {
            'status': 'error',
            'total_records': 1,
            'error_handler_failed': True
        }

    return state

def _generate_fallback_data(state: QueryEngineState, error_message: str) -> list:
    """Generate appropriate fallback data based on query context"""

    intent_type = state.get('intent_type', 'summary')
    metric = state.get('metric', 'value')
    dimension = state.get('dimension')

    # Different fallbacks for different intent types
    if intent_type == 'summary':
        if dimension:
            return [
                {dimension: 'No Data Available', metric: 0},
                {dimension: 'System Error', metric: 0}
            ]
        else:
            return [{metric: 0, 'status': 'error'}]

    elif intent_type == 'trend':
        return [
            {'period': '2024-01', metric: 0},
            {'period': '2024-02', metric: 0},
            {'period': '2024-03', metric: 0}
        ]

    elif intent_type == 'comparison':
        if dimension:
            return [
                {dimension: 'Category A', metric: 0},
                {dimension: 'Category B', metric: 0},
                {dimension: 'Category C', metric: 0}
            ]
        else:
            return [{'comparison': 'No data available', metric: 0}]

    else:
        # Generic fallback
        return [
            {'error': True, 'message': 'Data temporarily unavailable'},
            {'info': 'Please try again in a few moments'}
        ]