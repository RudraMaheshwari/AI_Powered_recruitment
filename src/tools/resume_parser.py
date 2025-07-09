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
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name from text"""
        # Look for common name patterns at the beginning of the resume
        lines = text.split('\n')
        
        # Check first few lines for name patterns
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            if len(line) > 0 and len(line) < 50:  # Reasonable name length
                # Look for patterns like "First Last" or "First M. Last"
                name_patterns = [
                    r'^[A-Z][a-z]+\s+[A-Z][a-z]+$',  # First Last
                    r'^[A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+$',  # First M. Last
                    r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+$',  # First Middle Last
                    r'^[A-Z][A-Z\s]+$',  # ALL CAPS names
                ]
                
                for pattern in name_patterns:
                    if re.match(pattern, line):
                        return line.strip()
        
        # If no clear name found, try to extract from contact information
        contact_patterns = [
            r'name[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[-|]\s*resume',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[-|]\s*cv'
        ]
        
        for pattern in contact_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        # More comprehensive phone patterns
        phone_patterns = [
            # Standard US format
            r'\b\d{3}-\d{3}-\d{4}\b',
            r'\b\d{3}\.\d{3}\.\d{4}\b',
            r'\b\d{3}\s\d{3}\s\d{4}\b',
            r'\b\(\d{3}\)\s\d{3}-\d{4}\b',
            # International format
            r'\b\+\d{1,3}\s\d{3}-\d{3}-\d{4}\b',
            r'\b\+\d{1,3}\s\d{3}\s\d{3}\s\d{4}\b',
            # Indian format (10 digits)
            r'\b\d{10}\b',
            r'\b\d{5}\s\d{5}\b',
            r'\b\d{3}\s\d{3}\s\d{4}\b',
            r'\b\d{2}\s\d{4}\s\d{4}\b',
            r'\b\d{4}\s\d{3}\s\d{3}\b',
            # With country code
            r'\b\+91\s?\d{10}\b',
            r'\b\+1\s?\d{10}\b',
            r'\b\+91\s?\d{5}\s\d{5}\b',
            r'\b\+91\s?\d{3}\s\d{3}\s\d{4}\b',
            # Various separators
            r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',
            r'\b\d{3}[-.\s]\d{4}[-.\s]\d{3}\b'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        
        # Try to find any sequence of 10-15 digits that might be a phone number
        digit_pattern = r'\b\d{10,15}\b'
        digits = re.findall(digit_pattern, text)
        if digits:
            # Filter out obvious non-phone numbers (like years, IDs, etc.)
            for digit in digits:
                if len(digit) == 10 or len(digit) == 11:
                    return digit
        
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
        # More comprehensive experience patterns
        exp_patterns = [
            # Standard formats
            r'(\d+)\s*years?\s*of\s*experience',
            r'(\d+)\s*years?\s*experience',
            r'experience:\s*(\d+)\s*years?',
            r'(\d+)\+\s*years?',
            # Alternative formats
            r'(\d+)\s*years?\s*in\s*the\s*field',
            r'(\d+)\s*years?\s*of\s*work',
            r'(\d+)\s*years?\s*professional',
            r'(\d+)\s*years?\s*industry',
            # With months
            r'(\d+)\s*years?\s*(\d+)\s*months?\s*experience',
            r'(\d+)\s*years?\s*(\d+)\s*months?',
            # Experience keywords
            r'experience.*?(\d+)\s*years?',
            r'(\d+)\s*years?.*?experience',
            # Work history patterns
            r'worked\s*for\s*(\d+)\s*years?',
            r'(\d+)\s*years?\s*of\s*work\s*history',
            # Internship/part-time
            r'(\d+)\s*years?\s*internship',
            r'(\d+)\s*years?\s*part.?time',
            # Project experience
            r'(\d+)\s*years?\s*project\s*experience'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if len(matches[0]) == 2:  # Years and months
                    years, months = matches[0]
                    return f"{years} years {months} months"
                else:
                    return f"{matches[0]} years"
        
        # Try to extract from work history sections
        work_sections = [
            'work experience', 'employment history', 'professional experience',
            'career history', 'work history', 'employment'
        ]
        
        for section in work_sections:
            if section.lower() in text.lower():
                # Look for date ranges that might indicate experience
                date_patterns = [
                    r'(\d{4})\s*[-–]\s*(\d{4}|\bpresent\b|\bcurrent\b)',
                    r'(\d{4})\s*to\s*(\d{4}|\bpresent\b|\bcurrent\b)',
                    r'(\d{4})\s*-\s*(\d{4}|\bpresent\b|\bcurrent\b)'
                ]
                
                for pattern in date_patterns:
                    date_matches = re.findall(pattern, text, re.IGNORECASE)
                    if date_matches:
                        # Calculate years from date ranges
                        for start_year, end_year in date_matches:
                            try:
                                start = int(start_year)
                                if end_year.lower() in ['present', 'current']:
                                    from datetime import datetime
                                    end = datetime.now().year
                                else:
                                    end = int(end_year)
                                years = end - start
                                if 0 <= years <= 50:  # Reasonable range
                                    return f"{years} years"
                            except ValueError:
                                continue
        
        # If no specific experience found, look for keywords indicating experience level
        experience_keywords = {
            'entry level': '0-1 years',
            'junior': '1-3 years', 
            'mid level': '3-5 years',
            'senior': '5-10 years',
            'lead': '5-10 years',
            'principal': '10+ years',
            'expert': '10+ years',
            'fresher': '0-1 years',
            'new graduate': '0-1 years',
            'student': '0-1 years',
            'undergraduate': '0-1 years',
            'bachelor': '0-1 years',
            'final year': '0-1 years',
            'graduating': '0-1 years',
            'internship': '0-1 years',
            'project': '0-1 years'
        }
        
        text_lower = text.lower()
        for keyword, experience in experience_keywords.items():
            if keyword in text_lower:
                return experience
        
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
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(text),
            "experience": self.extract_experience(text),
            "education": self.extract_education(text),
            "raw_text": text
        }
        
        return parsed_data