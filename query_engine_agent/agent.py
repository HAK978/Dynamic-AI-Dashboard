"""
Production Query Engine Agent - Proper LangGraph Implementation
Always LLM mode with proper nodes and tools structure
"""

import time
import logging
from langgraph.graph import StateGraph, END

from .state import QueryEngineState, QueryEngineInput, QueryEngineOutput
from .nodes import (
    cache_checker_node,
    sql_generator_node,
    query_executor_node,
    error_handler_node,
    data_formatter_node,
    cache_manager_node
)

logger = logging.getLogger(__name__)

class QueryEngineAgent:
    """Production Query Engine Agent using LangGraph"""

    def __init__(self, db_path: str = "test_dashboard.db"):
        self.db_path = db_path
        self.graph = self._create_graph()
        logger.info(f"Production LangGraph Query Engine Agent initialized")

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow following spec diagram"""

        # Create workflow
        workflow = StateGraph(QueryEngineState)

        # Add nodes (core spec only)
        workflow.add_node("cache_checker", cache_checker_node)
        workflow.add_node("sql_generator", sql_generator_node)
        workflow.add_node("query_executor", query_executor_node)
        workflow.add_node("error_handler", error_handler_node)
        workflow.add_node("data_formatter", data_formatter_node)
        workflow.add_node("cache_manager", cache_manager_node)

        # Set entry point (matching spec: Start -> QueryBuilder)
        workflow.set_entry_point("sql_generator")

        # Workflow: QueryBuilder -> CacheChecker
        workflow.add_edge("sql_generator", "cache_checker")

        # CacheChecker -> QueryExecutor (if cache miss) or CacheManager (if cache hit)
        workflow.add_conditional_edges(
            "cache_checker",
            self._check_cache_result,
            {
                "cache_hit": "cache_manager",       # Skip to cache manager if cached
                "cache_miss": "query_executor"      # Execute query if not cached
            }
        )

        # QueryExecutor -> DataFormatter (if success) or ErrorHandler (if error)
        workflow.add_conditional_edges(
            "query_executor",
            self._check_execution_success,
            {
                "success": "data_formatter",
                "error": "error_handler"
            }
        )

        # ErrorHandler -> DataFormatter (after handling error)
        workflow.add_edge("error_handler", "data_formatter")

        # DataFormatter -> CacheManager
        workflow.add_edge("data_formatter", "cache_manager")

        # CacheManager -> END
        workflow.add_edge("cache_manager", END)

        return workflow.compile()

    def _check_cache_result(self, state: QueryEngineState) -> str:
        """Check if cache was hit or missed"""
        return "cache_hit" if state.get("metadata", {}).get("cache_hit", False) else "cache_miss"

    def _check_execution_success(self, state: QueryEngineState) -> str:
        """Check if query execution was successful"""
        return "error" if state.get("error") else "success"

    def process(self, intent_data: QueryEngineInput) -> QueryEngineOutput:
        """
        Process intent data through LangGraph workflow
        """
        start_time = time.time()
        logger.info("Starting LangGraph production workflow...")

        # Initialize state
        initial_state = QueryEngineState(
            intent_type=intent_data.get("intent_type", "summary"),
            metric=intent_data.get("metric", "revenue"),
            dimension=intent_data.get("dimension"),
            chart_type=intent_data.get("chart_type", "bar"),
            raw_prompt=intent_data.get("raw_prompt", ""),
            enhanced_prompt=intent_data.get("enhanced_prompt", ""),

            sql_query="",
            execution_time=0.0,
            cache_key="",
            raw_data=[],
            formatted_data=[],
            metadata={},
            error=None,
            warnings=[],
            nodes_executed=[]
        )

        try:
            # Execute the LangGraph workflow
            final_state = self.graph.invoke(initial_state)

            processing_time = (time.time() - start_time) * 1000

            # Build metadata
            metadata = final_state.get("metadata", {})
            metadata.update({
                "total_records": len(final_state.get("formatted_data", [])),
                "execution_time": f"{final_state.get('execution_time', 0)*1000:.1f}ms",
                "processing_time": f"{processing_time:.1f}ms",
                "chart_type": final_state["chart_type"],
                "status": "error" if final_state.get("error") else "success",
                "nodes_executed": final_state.get("nodes_executed", []),
                "llm_mode": "core_spec_only"
            })

            if final_state.get("error"):
                metadata["error"] = final_state["error"]

            logger.info(f"✅ LangGraph workflow completed in {processing_time:.1f}ms")

            return QueryEngineOutput(
                data=final_state.get("formatted_data", []),
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"❌ LangGraph workflow failed: {str(e)}")
            processing_time = (time.time() - start_time) * 1000

            return QueryEngineOutput(
                data=[{"error": True, "message": "LangGraph workflow failed"}],
                metadata={
                    "total_records": 0,
                    "execution_time": "0ms",
                    "processing_time": f"{processing_time:.1f}ms",
                    "chart_type": intent_data.get("chart_type", "unknown"),
                    "status": "error",
                    "error": str(e),
                    "llm_mode": "core_spec_only"
                }
            )