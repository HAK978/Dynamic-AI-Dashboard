"""
Production Query Engine State - Simplified
"""

from typing import Dict, List, Any, Optional
from typing_extensions import TypedDict

class QueryEngineState(TypedDict):
    """Production state following spec requirements"""

    # Input
    intent_type: str
    metric: str
    dimension: Optional[str]
    chart_type: str
    raw_prompt: str
    enhanced_prompt: str

    # Processing
    sql_query: str
    execution_time: float
    cache_key: str

    # Data
    raw_data: List[Dict[str, Any]]
    formatted_data: List[Dict[str, Any]]
    metadata: Dict[str, Any]

    # Error handling
    error: Optional[str]
    warnings: List[str]

    # Workflow
    nodes_executed: List[str]

class QueryEngineInput(TypedDict):
    """Input from Intent Resolver Agent"""
    intent_type: str
    metric: str
    dimension: Optional[str]
    chart_type: str
    raw_prompt: str
    enhanced_prompt: str

class QueryEngineOutput(TypedDict):
    """Output for Visualization Agent"""
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]