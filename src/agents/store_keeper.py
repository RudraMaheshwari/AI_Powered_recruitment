"""
StoreKeeper agent for data management
"""

from typing import Dict, List, Any, Optional
from src.utils.helpers import save_json, load_json, append_to_json_list, generate_id
from src.utils.config import config
from src.schema.data_models import Candidate, Job, Interview

class StoreKeeper:
    """StoreKeeper agent for data storage and retrieval"""
    
    def __init__(self):
        self.config = config.get_config()
        self.name = "StoreKeeper"
    
    def store_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store candidate data"""
        try:
            result = append_to_json_list(
                candidate_data, 
                self.config["candidates_file"], 
                "candidates"
            )
            
            if result:
                return {"success": True, "message": "Candidate stored successfully"}
            else:
                return {"success": False, "message": "Failed to store candidate"}
                
        except Exception as e:
            return {"success": False, "message": f"Error storing candidate: {str(e)}"}
    
    def get_candidates(self) -> List[Dict[str, Any]]:
        """Retrieve all candidates"""
        try:
            data = load_json(self.config["candidates_file"])
            return data.get("candidates", [])
        except Exception as e:
            print(f"Error retrieving candidates: {e}")
            return []
    
    def get_candidate_by_id(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve candidate by ID"""
        try:
            candidates = self.get_candidates()
            for candidate in candidates:
                if candidate.get("id") == candidate_id:
                    return candidate
            return None
        except Exception as e:
            print(f"Error retrieving candidate by ID: {e}")
            return None
    
    def store_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store job data"""
        try:
            result = append_to_json_list(
                job_data, 
                self.config["jobs_file"], 
                "jobs"
            )
            
            if result:
                return {"success": True, "message": "Job stored successfully"}
            else:
                return {"success": False, "message": "Failed to store job"}
                
        except Exception as e:
            return {"success": False, "message": f"Error storing job: {str(e)}"}
    
    def get_jobs(self) -> List[Dict[str, Any]]:
        """Retrieve all jobs"""
        try:
            data = load_json(self.config["jobs_file"])
            return data.get("jobs", [])
        except Exception as e:
            print(f"Error retrieving jobs: {e}")
            return []
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve job by ID"""
        try:
            jobs = self.get_jobs()
            for job in jobs:
                if job.get("id") == job_id:
                    return job
            return None
        except Exception as e:
            print(f"Error retrieving job by ID: {e}")
            return None
    
    def store_interview(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store interview data"""
        try:
            result = append_to_json_list(
                interview_data, 
                self.config["interviews_file"], 
                "interviews"
            )
            
            if result:
                return {"success": True, "message": "Interview stored successfully"}
            else:
                return {"success": False, "message": "Failed to store interview"}
                
        except Exception as e:
            return {"success": False, "message": f"Error storing interview: {str(e)}"}
    
    def get_interviews(self) -> List[Dict[str, Any]]:
        """Retrieve all interviews"""
        try:
            data = load_json(self.config["interviews_file"])
            return data.get("interviews", [])
        except Exception as e:
            print(f"Error retrieving interviews: {e}")
            return []
    
    def update_candidate_status(self, candidate_id: str, status: str) -> Dict[str, Any]:
        """Update candidate status"""
        try:
            data = load_json(self.config["candidates_file"])
            candidates = data.get("candidates", [])
            
            for candidate in candidates:
                if candidate.get("id") == candidate_id:
                    candidate["status"] = status
                    break
            
            data["candidates"] = candidates
            result = save_json(data, self.config["candidates_file"])
            
            if result:
                return {"success": True, "message": "Status updated successfully"}
            else:
                return {"success": False, "message": "Failed to update status"}
                
        except Exception as e:
            return {"success": False, "message": f"Error updating status: {str(e)}"}
    
    def update_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update candidate data"""
        try:
            data = load_json(self.config["candidates_file"])
            candidates = data.get("candidates", [])
            
            # Find and update the candidate
            for i, candidate in enumerate(candidates):
                if candidate.get("id") == candidate_data.get("id"):
                    candidates[i] = candidate_data
                    break
            
            data["candidates"] = candidates
            result = save_json(data, self.config["candidates_file"])
            
            if result:
                return {"success": True, "message": "Candidate updated successfully"}
            else:
                return {"success": False, "message": "Failed to update candidate"}
                
        except Exception as e:
            return {"success": False, "message": f"Error updating candidate: {str(e)}"}
    
    def update_interview(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update interview data"""
        try:
            data = load_json(self.config["interviews_file"])
            interviews = data.get("interviews", [])
            
            # Find and update the interview
            for i, interview in enumerate(interviews):
                if interview.get("id") == interview_data.get("id"):
                    interviews[i] = interview_data
                    break
            
            data["interviews"] = interviews
            result = save_json(data, self.config["interviews_file"])
            
            if result:
                return {"success": True, "message": "Interview updated successfully"}
            else:
                return {"success": False, "message": "Failed to update interview"}
                
        except Exception as e:
            return {"success": False, "message": f"Error updating interview: {str(e)}"}