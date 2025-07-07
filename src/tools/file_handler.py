"""
File handling utilities
"""

import os
import shutil
from typing import Dict, Any, Optional
from src.utils.config import config

class FileHandler:
    """File handling utility"""
    
    def __init__(self):
        self.config = config.get_config()
    
    def save_resume_file(self, file_content: bytes, filename: str) -> str:
        """Save resume file and return path"""
        try:
            file_path = os.path.join(self.config["resumes_dir"], filename)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            return file_path
        except Exception as e:
            print(f"Error saving resume file: {e}")
            return None
    
    def delete_resume_file(self, file_path: str) -> bool:
        """Delete resume file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting resume file: {e}")
            return False
    
    def get_resume_path(self, filename: str) -> str:
        """Get full path for resume file"""
        return os.path.join(self.config["resumes_dir"], filename)
    
    def list_resume_files(self) -> list:
        """List all resume files"""
        try:
            return os.listdir(self.config["resumes_dir"])
        except Exception as e:
            print(f"Error listing resume files: {e}")
            return []
