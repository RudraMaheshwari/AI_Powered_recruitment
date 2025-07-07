import os
import google.generativeai as genai
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class LLMConfig:
    """Configuration class for Gemini 2.0 Flash LLM"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.project_id = os.getenv("GOOGLE_PROJECT_ID")
        self.model_name = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2048"))
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self._configure_genai()
    
    def _configure_genai(self):
        """Configure Google Generative AI"""
        try:
            genai.configure(api_key=self.api_key)
            logger.info(f"Configured Gemini with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to configure Gemini: {e}")
            raise
    
    def get_model(self):
        """Get configured Gemini model"""
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                }
            )
            return model
        except Exception as e:
            logger.error(f"Failed to get model: {e}")
            raise
    
    def get_chat_model(self):
        """Get configured Gemini chat model"""
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                }
            )
            return model.start_chat(history=[])
        except Exception as e:
            logger.error(f"Failed to get chat model: {e}")
            raise
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration as dictionary"""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "project_id": self.project_id
        }

# Global LLM configuration instance
llm_config = LLMConfig() 