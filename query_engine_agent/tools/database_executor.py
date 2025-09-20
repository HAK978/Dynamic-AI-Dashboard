"""
Database Execution Tool
"""

import sqlite3
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DatabaseExecutor:
    """Tool for executing SQL queries against database"""

    def __init__(self, db_path: str = "test_dashboard.db"):
        self.db_path = db_path

    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        start_time = time.time()

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(sql_query)
            rows = cursor.fetchall()

            data = [dict(row) for row in rows]
            execution_time = time.time() - start_time

            conn.close()

            logger.info(f"Query executed: {len(data)} records in {execution_time*1000:.1f}ms")

            return {
                'success': True,
                'data': data,
                'execution_time': execution_time,
                'record_count': len(data)
            }

        except Exception as e:
            logger.error(f"Database execution failed: {e}")
            return {
                'success': False,
                'data': [],
                'execution_time': time.time() - start_time,
                'record_count': 0,
                'error': f"Database error: {str(e)}"
            }