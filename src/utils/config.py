"""
Configuration management for the recruitment assistant
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

class Config:
    """Configuration class for the recruitment assistant"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.data_dir = "data"
        self.resumes_dir = os.path.join(self.data_dir, "resumes")
        self.candidates_file = os.path.join(self.data_dir, "candidates.json")
        self.jobs_file = os.path.join(self.data_dir, "jobs.json")
        self.interviews_file = os.path.join(self.data_dir, "interviews.json")
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.resumes_dir, exist_ok=True)
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration dictionary"""
        return {
            "google_api_key": self.google_api_key,
            "data_dir": self.data_dir,
            "resumes_dir": self.resumes_dir,
            "candidates_file": self.candidates_file,
            "jobs_file": self.jobs_file,
            "interviews_file": self.interviews_file
        }

config = Config()