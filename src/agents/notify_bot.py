"""
NotifyBot agent for candidate communications
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain.schema import HumanMessage, AIMessage
from src.models.llm_config import llm_config
from src.agentic_prompts.prompts import NOTIFY_BOT_PROMPT

class NotifyBot:
    """NotifyBot agent for candidate notifications"""
    
    def __init__(self):
        self.llm = llm_config.get_llm()
        self.name = "NotifyBot"
    
    def send_interview_confirmation(self, candidate: Dict[str, Any], 
                                  interview: Dict[str, Any]) -> Dict[str, Any]:
        """Send interview confirmation to candidate"""
        try:
            message = self._generate_interview_confirmation_message(candidate, interview)
            
            notification = {
                "id": self._generate_notification_id(),
                "type": "interview_confirmation",
                "recipient": candidate.get("email"),
                "subject": "Interview Confirmation",
                "message": message,
                "status": "sent",
                "sent_at": datetime.now().isoformat()
            }
            
            return notification
            
        except Exception as e:
            return {"error": f"Error sending interview confirmation: {str(e)}"}
    
    def send_interview_notification(self, candidate: Dict[str, Any], 
                                  interview: Dict[str, Any]) -> Dict[str, Any]:
        """Send interview notification to candidate (alias for send_interview_confirmation)"""
        try:
            # Use the existing interview confirmation logic
            result = self.send_interview_confirmation(candidate, interview)
            
            # Update the type to match the expected method name
            if "error" not in result:
                result["type"] = "interview_notification"
                result["success"] = True
            else:
                result["success"] = False
                result["message"] = result["error"]
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error sending interview notification: {str(e)}"
            }
    
    def send_decision_notification(self, candidate: Dict[str, Any], 
                                 decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send final decision notification to candidate"""
        try:
            message = self._generate_decision_notification_message(candidate, decision_data)
            
            notification = {
                "id": self._generate_notification_id(),
                "type": "decision_notification",
                "recipient": candidate.get("email"),
                "subject": "Application Decision",
                "message": message,
                "status": "sent",
                "sent_at": datetime.now().isoformat(),
                "success": True
            }
            
            return notification
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error sending decision notification: {str(e)}"
            }
    
    def send_interview_reminder(self, candidate: Dict[str, Any], 
                              interview: Dict[str, Any]) -> Dict[str, Any]:
        """Send interview reminder to candidate"""
        try:
            message = self._generate_interview_reminder_message(candidate, interview)
            
            notification = {
                "id": self._generate_notification_id(),
                "type": "interview_reminder",
                "recipient": candidate.get("email"),
                "subject": "Interview Reminder",
                "message": message,
                "status": "sent",
                "sent_at": datetime.now().isoformat()
            }
            
            return notification
            
        except Exception as e:
            return {"error": f"Error sending interview reminder: {str(e)}"}
    
    def send_status_update(self, candidate: Dict[str, Any], 
                          status: str, message: str = None) -> Dict[str, Any]:
        """Send status update to candidate"""
        try:
            notification_message = self._generate_status_update_message(candidate, status, message)
            
            notification = {
                "id": self._generate_notification_id(),
                "type": "status_update",
                "recipient": candidate.get("email"),
                "subject": f"Application Status Update",
                "message": notification_message,
                "status": "sent",
                "sent_at": datetime.now().isoformat()
            }
            
            return notification
            
        except Exception as e:
            return {"error": f"Error sending status update: {str(e)}"}
    
    def send_custom_message(self, candidate: Dict[str, Any], 
                           subject: str, message: str) -> Dict[str, Any]:
        """Send custom message to candidate"""
        try:
            notification = {
                "id": self._generate_notification_id(),
                "type": "custom_message",
                "recipient": candidate.get("email"),
                "subject": subject,
                "message": message,
                "status": "sent",
                "sent_at": datetime.now().isoformat()
            }
            
            return notification
            
        except Exception as e:
            return {"error": f"Error sending custom message: {str(e)}"}
    
    def _generate_interview_confirmation_message(self, candidate: Dict[str, Any], 
                                                interview: Dict[str, Any]) -> str:
        """Generate interview confirmation message"""
        interview_time = datetime.fromisoformat(interview.get("scheduled_time"))
        
        message = f"""
Dear {candidate.get('name', 'Candidate')},

We are pleased to confirm your interview for the position you applied for.

Interview Details:
- Date: {interview_time.strftime('%B %d, %Y')}
- Time: {interview_time.strftime('%I:%M %p')}
- Duration: {interview.get('duration', 60)} minutes
- Location: {interview.get('location', 'Virtual Meeting')}

Please ensure you are available at the scheduled time. If you need to reschedule, please contact us at least 24 hours in advance.

Best regards,
HR Team
"""
        return message.strip()
    
    def _generate_interview_reminder_message(self, candidate: Dict[str, Any], 
                                           interview: Dict[str, Any]) -> str:
        """Generate interview reminder message"""
        interview_time = datetime.fromisoformat(interview.get("scheduled_time"))
        
        message = f"""
Dear {candidate.get('name', 'Candidate')},

This is a friendly reminder about your upcoming interview.

Interview Details:
- Date: {interview_time.strftime('%B %d, %Y')}
- Time: {interview_time.strftime('%I:%M %p')}
- Duration: {interview.get('duration', 60)} minutes
- Location: {interview.get('location', 'Virtual Meeting')}

Please join the meeting on time. We look forward to speaking with you.

Best regards,
HR Team
"""
        return message.strip()
    
    def _generate_status_update_message(self, candidate: Dict[str, Any], 
                                      status: str, custom_message: str = None) -> str:
        """Generate status update message"""
        if custom_message:
            return custom_message
        
        status_messages = {
            "approved": "Congratulations! Your application has been approved for the next stage.",
            "rejected": "Thank you for your interest. Unfortunately, we have decided to move forward with other candidates.",
            "on_hold": "Your application is currently on hold. We will update you as soon as possible.",
            "interviewed": "Thank you for taking the time to interview with us. We will be in touch soon.",
            "hired": "Congratulations! We are pleased to offer you the position."
        }
        
        base_message = status_messages.get(status, "Your application status has been updated.")
        
        message = f"""
Dear {candidate.get('name', 'Candidate')},

{base_message}

If you have any questions, please don't hesitate to contact us.

Best regards,
HR Team
"""
        return message.strip()
    
    def _generate_decision_notification_message(self, candidate: Dict[str, Any], 
                                              decision_data: Dict[str, Any]) -> str:
        """Generate decision notification message"""
        decision = decision_data.get('decision', '')
        salary_offer = decision_data.get('salary_offer')
        notes = decision_data.get('notes', '')
        
        if decision == 'hire':
            message = f"""
Dear {candidate.get('name', 'Candidate')},

Congratulations! We are pleased to offer you the position.

{f'Salary Offer: ${salary_offer:,}' if salary_offer else ''}

{notes if notes else ''}

Please review the offer and respond within 5 business days.

Best regards,
HR Team
"""
        elif decision == 'reject':
            message = f"""
Dear {candidate.get('name', 'Candidate')},

Thank you for your interest in our company and for taking the time to interview with us.

After careful consideration, we have decided to move forward with other candidates for this position.

{notes if notes else ''}

We wish you the best in your future endeavors.

Best regards,
HR Team
"""
        else:  # hold
            message = f"""
Dear {candidate.get('name', 'Candidate')},

Thank you for your interest in our company.

Your application is currently on hold while we complete our review process.

{notes if notes else ''}

We will be in touch with you soon.

Best regards,
HR Team
"""
        
        return message.strip()
    
    def _generate_notification_id(self) -> str:
        """Generate unique notification ID"""
        from src.utils.helpers import generate_id
        return f"NOT_{generate_id()[:8]}"