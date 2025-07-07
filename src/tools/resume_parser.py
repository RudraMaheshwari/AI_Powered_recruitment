"""
Resume parsing tools
"""

import re
import fitz  # PyMuPDF
import pdfplumber
from typing import Dict, List, Optional, Any
import os

class ResumeParser:
    """Resume parsing utility"""
    
    def __init__(self):
        self.skills_keywords = [
            # Programming languages
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            # Web technologies
            'react', 'angular', 'vue', 'html', 'css', 'node.js', 'express', 'django', 'flask',
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle',
            # Cloud and DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd',
            # Data Science
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy',
            # Other
            'git', 'linux', 'agile', 'scrum', 'rest api', 'microservices'
        ]
    
    def parse_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF resume"""
        try:
            text = ""
            # Try with PyMuPDF first
            try:
                doc = fitz.open(pdf_path)
                for page in doc:
                    text += page.get_text()
                doc.close()
            except:
                # Fallback to pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
            
            return text.strip()
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return ""
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        phone_patterns = [
            r'\b\d{3}-\d{3}-\d{4}\b',
            r'\b\d{3}\.\d{3}\.\d{4}\b',
            r'\b\d{3}\s\d{3}\s\d{4}\b',
            r'\b\(\d{3}\)\s\d{3}-\d{4}\b',
            r'\b\+\d{1,3}\s\d{3}-\d{3}-\d{4}\b'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return None
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return list(set(found_skills))
    
    def extract_experience(self, text: str) -> Optional[str]:
        """Extract experience information"""
        exp_patterns = [
            r'(\d+)\s*years?\s*of\s*experience',
            r'(\d+)\s*years?\s*experience',
            r'experience:\s*(\d+)\s*years?',
            r'(\d+)\+\s*years?'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return f"{matches[0]} years"
        
        return None
    
    def extract_education(self, text: str) -> Optional[str]:
        """Extract education information"""
        edu_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'university', 'college',
            'b.s.', 'b.a.', 'm.s.', 'm.a.', 'mba', 'ph.d.'
        ]
        
        text_lower = text.lower()
        education_info = []
        
        for keyword in edu_keywords:
            if keyword in text_lower:
                # Extract sentences containing education keywords
                sentences = text.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        education_info.append(sentence.strip())
                        break
        
        return '; '.join(education_info) if education_info else None
    
    def parse_resume(self, file_path: str = None, text: str = None) -> Dict[str, Any]:
        """Parse resume and extract structured information"""
        if file_path and os.path.exists(file_path):
            text = self.parse_pdf(file_path)
        
        if not text:
            return {"error": "No text content found"}
        
        parsed_data = {
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(text),
            "experience": self.extract_experience(text),
            "education": self.extract_education(text),
            "raw_text": text
        }
        
        return parsed_data