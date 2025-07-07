"""
Data models for the recruitment assistant
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Candidate:
    """Candidate data model"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    skills: List[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    resume_path: Optional[str] = None
    status: str = "new"
    created_at: str = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Job:
    """Job data model"""
    id: str
    title: str
    description: str
    requirements: List[str]
    skills_required: List[str]
    experience_level: str
    department: str
    status: str = "active"
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Interview:
    """Interview data model"""
    id: str
    candidate_id: str
    job_id: str
    scheduled_time: str
    status: str = "scheduled"
    notes: Optional[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AgentState:
    """State management for agents"""
    messages: List[Dict[str, Any]]
    current_agent: str
    context: Dict[str, Any]
    candidates: List[Candidate]
    jobs: List[Job]
    interviews: List[Interview]
    
    def __post_init__(self):
        if not self.messages:
            self.messages = []
        if not self.context:
            self.context = {}
        if not self.candidates:
            self.candidates = []
        if not self.jobs:
            self.jobs = []
        if not self.interviews:
            self.interviews = []