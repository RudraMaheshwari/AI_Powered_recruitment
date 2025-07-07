"""
Scheduling utilities
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class Scheduler:
    """Interview scheduling utility"""
    
    def __init__(self):
        self.business_hours = (9, 17)  # 9 AM to 5 PM
        self.working_days = [0, 1, 2, 3, 4]  # Monday to Friday
    
    def generate_time_slots(self, start_date: datetime, days: int = 7) -> List[datetime]:
        """Generate available time slots"""
        slots = []
        current_date = start_date
        
        for _ in range(days):
            if current_date.weekday() in self.working_days:
                for hour in range(self.business_hours[0], self.business_hours[1]):
                    slot_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    slots.append(slot_time)
            current_date += timedelta(days=1)
        
        return slots
    
    def find_available_slots(self, existing_interviews: List[Dict[str, Any]], 
                            preferred_time: Optional[datetime] = None) -> List[datetime]:
        """Find available interview slots"""
        start_date = preferred_time or datetime.now()
        all_slots = self.generate_time_slots(start_date)
        
        # Filter out already booked slots
        booked_times = []
        for interview in existing_interviews:
            if interview.get('scheduled_time'):
                booked_times.append(datetime.fromisoformat(interview['scheduled_time']))
        
        available_slots = [slot for slot in all_slots if slot not in booked_times]
        return available_slots[:10]  # Return top 10 available slots
    
    def schedule_interview(self, candidate_id: str, job_id: str, 
                            preferred_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Schedule an interview"""
        available_slots = self.find_available_slots([], preferred_time)
        
        if not available_slots:
            return {"error": "No available slots found"}
        
        selected_slot = available_slots[0]
        
        return {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "scheduled_time": selected_slot.isoformat(),
            "status": "scheduled"
        }