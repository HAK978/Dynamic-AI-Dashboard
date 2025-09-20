"""
SQL Generation Tool - Always uses LLM
"""

import logging
from ..llm_config import llm
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

class SQLGenerator:
    """Tool for generating SQL queries using LLM"""

    def __init__(self):
        self.schema_context = """
        Database Schema:
        - sales: sale_id, user_id, product_id, sale_date, quantity, unit_price, total_amount, discount_amount, sales_channel, region
        - users: user_id, username, registration_date, country, age, status
        - products: product_id, product_name, category, price, cost, launch_date, brand

        RULES:
        - Use 'sales' table for transactions
        - Use 'total_amount' for revenue
        - Always use proper JOINs
        - Limit results to 50 records max
        """

    def generate_sql(self, intent_type: str, metric: str, dimension: str = None,
                    raw_prompt: str = "", enhanced_prompt: str = "") -> str:
        """Generate SQL query using LLM"""

        system_prompt = f"""You are an expert SQL generator for business intelligence.

        {self.schema_context}

        Generate a single, executable SQLite query that retrieves the requested data.
        Return ONLY the SQL query, no explanations."""

        user_prompt = f"""
        Intent: {intent_type}
        Metric: {metric}
        Dimension: {dimension or 'None'}
        User Query: {raw_prompt}
        Context: {enhanced_prompt}

        Generate the optimal SQL query.
        """

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            response = llm.invoke(messages)
            sql_query = response.content.strip()

            # Clean SQL formatting
            if sql_query.startswith("```sql"):
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            elif sql_query.startswith("```"):
                sql_query = sql_query.replace("```", "").strip()

            # Remove extra whitespace
            sql_query = " ".join(sql_query.split())

            logger.info(f"Generated SQL: {sql_query[:100]}...")
            return sql_query

        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            # Simple fallback
            if dimension:
                return f"SELECT {dimension}, SUM(total_amount) as {metric} FROM sales LEFT JOIN products ON sales.product_id = products.product_id GROUP BY {dimension} ORDER BY {metric} DESC LIMIT 50"
            else:
                return f"SELECT SUM(total_amount) as {metric} FROM sales"