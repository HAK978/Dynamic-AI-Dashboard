"""
SQL Generator Node
"""

import logging
from ..state import QueryEngineState
from ..tools.sql_generator import SQLGenerator

logger = logging.getLogger(__name__)

# Global tool instance
sql_generator = SQLGenerator()

def sql_generator_node(state: QueryEngineState) -> QueryEngineState:
    """Generate SQL query using LLM"""

    logger.info("🧠 Generating SQL query with LLM...")

    try:
        sql_query = sql_generator.generate_sql(
            intent_type=state["intent_type"],
            metric=state["metric"],
            dimension=state.get("dimension"),
            raw_prompt=state["raw_prompt"],
            enhanced_prompt=state["enhanced_prompt"]
        )

        state["sql_query"] = sql_query
        state["nodes_executed"].append("sql_generator")

        logger.info(f"✅ SQL generated: {sql_query[:50]}...")

    except Exception as e:
        error_msg = f"SQL generation failed: {str(e)}"
        logger.error(error_msg)
        state["error"] = error_msg

    return state