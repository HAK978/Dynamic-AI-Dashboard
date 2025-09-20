"""
Production LLM Configuration - Always On
"""

import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class LLMConfig:
    """Production LLM configuration"""

    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4000"))

    def get_llm(self):
        """Get configured LLM instance"""
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not configured for production mode")

        return ChatGroq(
            model=self.model,
            api_key=self.groq_api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

# Global LLM instance
llm_config = LLMConfig()
llm = llm_config.get_llm()