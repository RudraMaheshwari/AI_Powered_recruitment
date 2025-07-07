"""
TimeBot agent for interview scheduling
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from langchain.schema import HumanMessage, AIMessage
from src.models.llm_config import llm_config
from src.agentic_prompts.prompts import TIME_BOT_PROMPT
from src.tools.scheduler import Scheduler

class TimeBot:
    """TimeBot agent for interview scheduling"""
    
    def __init__(self):
        self.llm = llm_config.get_llm()
        self.scheduler = Scheduler()
        self.name = "TimeBot"
    
    def schedule_interview(self, candidate_id: str, job_id: str, 
                          preferred_time: Optional[str] = None) -> Dict[str, Any]:
        """Schedule an interview"""
        try:
            # Parse preferred time if provided
            pref_datetime = None
            if preferred_time:
                try:
                    pref_datetime = datetime.fromisoformat(preferred_time)
                except:
                    pref_datetime = None
            
            # Schedule the interview
            interview_data = self.scheduler.schedule_interview(
                candidate_id, job_id, pref_datetime
            )
            
            if "error" in interview_data:
                return interview_data
            
            # Add additional scheduling information
            interview_data.update({
                "id": self._generate_interview_id(),
                "created_at": datetime.now().isoformat(),
                "status": "scheduled",
                "type": "initial_interview",
                "duration": 60,  # 60 minutes
                "location": "Virtual Meeting"
            })
            
            return interview_data
            
        except Exception as e:
            return {"error": f"Error scheduling interview: {str(e)}"}
    
    def get_available_slots(self, date_range: int = 7) -> List[Dict[str, Any]]:
        """Get available interview slots"""
        try:
            start_date = datetime.now()
            available_slots = self.scheduler.generate_time_slots(start_date, date_range)
            
            formatted_slots = []
            for slot in available_slots:
                formatted_slots.append({
                    "datetime": slot.isoformat(),
                    "date": slot.strftime("%Y-%m-%d"),
                    "time": slot.strftime("%H:%M"),
                    "day_of_week": slot.strftime("%A"),
                    "available": True
                })
            
            return formatted_slots
            
        except Exception as e:
            return [{"error": f"Error getting available slots: {str(e)}"}]
    
    def reschedule_interview(self, interview_id: str, new_time: str) -> Dict[str, Any]:
        """Reschedule an existing interview"""
        try:
            # Parse new time
            new_datetime = datetime.fromisoformat(new_time)
            
            # Validate new time slot
            if new_datetime < datetime.now():
                return {"error": "Cannot schedule interview in the past"}
            
            # Check if slot is available
            available_slots = self.get_available_slots()
            slot_available = any(
                slot["datetime"] == new_datetime.isoformat() 
                for slot in available_slots
            )
            
            if not slot_available:
                return {"error": "Selected time slot is not available"}
            
            return {
                "interview_id": interview_id,
                "new_scheduled_time": new_datetime.isoformat(),
                "status": "rescheduled",
                "message": "Interview rescheduled successfully"
            }
            
        except Exception as e:
            return {"error": f"Error rescheduling interview: {str(e)}"}
    
    def cancel_interview(self, interview_id: str, reason: str = None) -> Dict[str, Any]:
        """Cancel an interview"""
        try:
            return {
                "interview_id": interview_id,
                "status": "cancelled",
                "reason": reason or "No reason provided",
                "cancelled_at": datetime.now().isoformat(),
                "message": "Interview cancelled successfully"
            }
            
        except Exception as e:
            return {"error": f"Error cancelling interview: {str(e)}"}
    
    def _generate_interview_id(self) -> str:
        """Generate unique interview ID"""
        from src.utils.helpers import generate_id
        return f"INT_{generate_id()[:8]}"
