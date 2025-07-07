"""
ResumeBot agent for collecting and parsing resumes
"""

from typing import Dict, List, Any, Optional
from langchain.schema import HumanMessage, AIMessage
from src.models.llm_config import llm_config
from src.agentic_prompts.prompts import RESUME_BOT_PROMPT
from src.tools.resume_parser import ResumeParser
from src.tools.file_handler import FileHandler
from src.utils.helpers import generate_id, get_timestamp
from src.schema.data_models import Candidate

class ResumeBot:
    """ResumeBot agent for resume collection and parsing"""
    
    def __init__(self):
        self.llm = llm_config.get_llm()
        self.parser = ResumeParser()
        self.file_handler = FileHandler()
        self.name = "ResumeBot"
    
    def process_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process resume data and extract information"""
        try:
            # Parse resume content
            if 'file_path' in resume_data:
                parsed_data = self.parser.parse_resume(file_path=resume_data['file_path'])
            elif 'text' in resume_data:
                parsed_data = self.parser.parse_resume(text=resume_data['text'])
            else:
                return {"error": "No resume content provided"}
            
            # Create candidate profile
            candidate_id = generate_id()
            candidate = Candidate(
                id=candidate_id,
                name=resume_data.get('name', 'Unknown'),
                email=parsed_data.get('email', ''),
                phone=parsed_data.get('phone'),
                skills=parsed_data.get('skills', []),
                experience=parsed_data.get('experience'),
                education=parsed_data.get('education'),
                resume_path=resume_data.get('file_path'),
                created_at=get_timestamp()
            )
            
            return {
                "candidate": candidate.to_dict(),
                "parsed_data": parsed_data,
                "success": True
            }
            
        except Exception as e:
            return {"error": f"Error processing resume: {str(e)}"}
    
    def chat_with_candidate(self, message: str, context: Dict[str, Any]) -> str:
        """Chat with candidate for resume collection"""
        try:
            prompt = RESUME_BOT_PROMPT.format(context=context)
            
            messages = [
                HumanMessage(content=prompt),
                HumanMessage(content=message)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"Error in chat: {str(e)}"
    
    def validate_candidate_data(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Validate candidate data completeness"""
        required_fields = ['name', 'email']
        missing_fields = []
        
        for field in required_fields:
            if not candidate.get(field):
                missing_fields.append(field)
        
        validation_result = {
            "is_valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "candidate": candidate
        }
        
        return validation_result