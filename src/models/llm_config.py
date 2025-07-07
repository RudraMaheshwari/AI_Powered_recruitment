"""
LLM configuration and setup
"""

import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.config import config

class LLMConfig:
    """LLM configuration class"""
    
    def __init__(self):
        self.api_key = config.google_api_key
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize LangChain LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.api_key,
            temperature=0.7,
            convert_system_message_to_human=True
        )
    
    def get_llm(self):
        """Get the configured LLM instance"""
        return self.llm

llm_config = LLMConfig()