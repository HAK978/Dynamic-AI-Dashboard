"""
Data Formatter Node
"""

import logging
from ..state import QueryEngineState
from ..tools.data_validator import DataValidator

logger = logging.getLogger(__name__)

# Global validator instance
data_validator = DataValidator()

def data_formatter_node(state: QueryEngineState) -> QueryEngineState:
    """Format and validate raw data for visualization"""

    logger.info("🎨 Formatting and validating data...")

    try:
        raw_data = state["raw_data"]

        if not raw_data:
            state["formatted_data"] = []
            state["nodes_executed"].append("data_formatter")
            return state

        # Validate and clean data
        query_context = {
            'intent_type': state['intent_type'],
            'metric': state['metric'],
            'dimension': state.get('dimension'),
            'chart_type': state['chart_type']
        }

        validation_result = data_validator.validate_data(raw_data, query_context)

        # Use cleaned data from validator
        state["formatted_data"] = validation_result['cleaned_data']

        # Add validation warnings to state
        if validation_result['warnings']:
            state["warnings"].extend(validation_result['warnings'])

        # Add validation stats to metadata
        if 'metadata' not in state:
            state['metadata'] = {}
        state['metadata']['validation_stats'] = validation_result['stats']

        state["nodes_executed"].append("data_formatter")

        logger.info(f"✅ Data formatted and validated: {len(state['formatted_data'])} records")

    except Exception as e:
        error_msg = f"Data formatting failed: {str(e)}"
        logger.error(error_msg)
        state["error"] = error_msg

    return state