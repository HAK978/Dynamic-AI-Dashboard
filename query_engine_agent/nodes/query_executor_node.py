"""
Query Executor Node
"""

import logging
from ..state import QueryEngineState
from ..tools.database_executor import DatabaseExecutor

logger = logging.getLogger(__name__)

# Global tool instance
database_executor = DatabaseExecutor()

def query_executor_node(state: QueryEngineState) -> QueryEngineState:
    """Execute SQL query against database"""

    logger.info("⚡ Executing SQL query...")

    try:
        result = database_executor.execute_query(state["sql_query"])

        if result["success"]:
            state["raw_data"] = result["data"]
            state["execution_time"] = result["execution_time"]
            state["nodes_executed"].append("query_executor")

            logger.info(f"✅ Query executed: {result['record_count']} records")
        else:
            state["error"] = result["error"]
            logger.error(f"❌ Query failed: {result['error']}")

    except Exception as e:
        error_msg = f"Query execution failed: {str(e)}"
        logger.error(error_msg)
        state["error"] = error_msg

    return state