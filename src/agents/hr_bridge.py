"""
HRBridge agent for HR interface
"""

from typing import Dict, List, Any, Optional
from langchain.schema import HumanMessage, AIMessage
from src.models.llm_config import llm_config
from src.agentic_prompts.prompts import HR_BRIDGE_PROMPT

class HRBridge:
    """HRBridge agent for HR interactions"""
    
    def __init__(self):
        self.llm = llm_config.get_llm()
        self.name = "HRBridge"
    
    def present_candidates(self, candidates: List[Dict[str, Any]], 
                            job: Dict[str, Any]) -> Dict[str, Any]:
        """Present filtered candidates to HR"""
        try:
            # Prepare candidate summary
            candidate_summary = self._prepare_candidate_summary(candidates)
            
            # Generate HR presentation
            presentation = {
                "job_title": job.get("title", "Unknown Position"),
                "job_id": job.get("id"),
                "total_candidates": len(candidates),
                "top_candidates": candidates[:5],  # Top 5 candidates
                "candidate_summary": candidate_summary,
                "recommendations": self._generate_hr_recommendations(candidates)
            }
            
            return presentation
            
        except Exception as e:
            return {"error": f"Error presenting candidates: {str(e)}"}
    
    def process_hr_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Process HR feedback and decisions"""
        try:
            action = feedback.get("action")
            candidate_id = feedback.get("candidate_id")
            
            if action == "approve":
                return {
                    "action": "schedule_interview",
                    "candidate_id": candidate_id,
                    "status": "approved"
                }
            elif action == "reject":
                return {
                    "action": "update_status",
                    "candidate_id": candidate_id,
                    "status": "rejected"
                }
            elif action == "hold":
                return {
                    "action": "update_status",
                    "candidate_id": candidate_id,
                    "status": "on_hold"
                }
            else:
                return {"error": "Invalid action"}
                
        except Exception as e:
            return {"error": f"Error processing HR feedback: {str(e)}"}
    
    def generate_hr_report(self, candidates: List[Dict[str, Any]], 
                            job: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive HR report"""
        try:
            report = {
                "job_details": {
                    "title": job.get("title"),
                    "id": job.get("id"),
                    "requirements": job.get("requirements", [])
                },
                "candidate_statistics": {
                    "total_candidates": len(candidates),
                    "excellent_candidates": len([c for c in candidates if c.get("ranking") == "Excellent"]),
                    "good_candidates": len([c for c in candidates if c.get("ranking") == "Good"]),
                    "average_candidates": len([c for c in candidates if c.get("ranking") == "Average"]),
                    "below_average_candidates": len([c for c in candidates if c.get("ranking") == "Below Average"])
                },
                "top_candidates": candidates[:3],
                "skill_analysis": self._analyze_skills(candidates),
                "recommendations": self._generate_hiring_recommendations(candidates)
            }
            
            return report
            
        except Exception as e:
            return {"error": f"Error generating HR report: {str(e)}"}
    
    def _prepare_candidate_summary(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare candidate summary for HR"""
        summary = []
        for candidate in candidates:
            candidate_data = candidate.get("candidate_data", {})
            summary.append({
                "id": candidate_data.get("id"),
                "name": candidate_data.get("name"),
                "email": candidate_data.get("email"),
                "skills": candidate_data.get("skills", []),
                "experience": candidate_data.get("experience"),
                "overall_score": candidate.get("overall_score"),
                "ranking": candidate.get("ranking"),
                "recommendations": candidate.get("recommendations", [])
            })
        return summary
    
    def _generate_hr_recommendations(self, candidates: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for HR"""
        recommendations = []
        
        excellent_count = len([c for c in candidates if c.get("ranking") == "Excellent"])
        good_count = len([c for c in candidates if c.get("ranking") == "Good"])
        
        if excellent_count >= 3:
            recommendations.append("Multiple excellent candidates available - proceed with interviews")
        elif excellent_count >= 1:
            recommendations.append("Strong candidates identified - prioritize top performers")
        elif good_count >= 2:
            recommendations.append("Good candidates available - consider multiple interviews")
        else:
            recommendations.append("Limited qualified candidates - consider expanding search")
        
        return recommendations
    
    def _analyze_skills(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze skills across all candidates"""
        all_skills = []
        for candidate in candidates:
            candidate_data = candidate.get("candidate_data", {})
            all_skills.extend(candidate_data.get("skills", []))
        
        # Count skill frequency
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Get top skills
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_unique_skills": len(skill_counts),
            "top_skills": top_skills,
            "skill_distribution": skill_counts
        }
    
    def _generate_hiring_recommendations(self, candidates: List[Dict[str, Any]]) -> List[str]:
        """Generate hiring recommendations"""
        recommendations = []
        
        if len(candidates) == 0:
            recommendations.append("No candidates found - expand search criteria")
        elif len(candidates) < 3:
            recommendations.append("Limited candidate pool - consider broader recruitment")
        else:
            recommendations.append("Sufficient candidates for selection process")
        
        return recommendations
    
    def review_candidate(self, candidate_id: str, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review a candidate and provide feedback"""
        try:
            # Process the review data
            rating = review_data.get('rating', 0)
            notes = review_data.get('notes', '')
            decision = review_data.get('decision', 'pending')
            
            # Generate AI-powered review insights
            review_insights = self._generate_review_insights(rating, notes, decision)
            
            result = {
                "success": True,
                "candidate_id": candidate_id,
                "review_data": review_data,
                "insights": review_insights,
                "recommendation": self._get_recommendation_from_rating(rating),
                "next_steps": self._get_next_steps(decision)
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error reviewing candidate: {str(e)}"
            }
    
    def submit_interview_feedback(self, interview_id: str, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit interview feedback"""
        try:
            # Process interview feedback
            technical_rating = feedback_data.get('technical_rating', 0)
            communication_rating = feedback_data.get('communication_rating', 0)
            culture_fit_rating = feedback_data.get('culture_fit_rating', 0)
            recommendation = feedback_data.get('recommendation', 'no_hire')
            notes = feedback_data.get('notes', '')
            
            # Calculate overall interview score
            overall_score = (technical_rating + communication_rating + culture_fit_rating) / 3
            
            # Generate feedback insights
            feedback_insights = self._generate_feedback_insights(
                technical_rating, communication_rating, culture_fit_rating, recommendation
            )
            
            result = {
                "success": True,
                "interview_id": interview_id,
                "feedback_data": feedback_data,
                "overall_score": round(overall_score, 2),
                "insights": feedback_insights,
                "recommendation": recommendation
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error submitting interview feedback: {str(e)}"
            }
    
    def make_final_decision(self, candidate_id: str, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make final hiring decision"""
        try:
            decision = decision_data.get('decision', '')
            salary_offer = decision_data.get('salary_offer')
            notes = decision_data.get('notes', '')
            
            # Generate decision insights
            decision_insights = self._generate_decision_insights(decision, salary_offer, notes)
            
            result = {
                "success": True,
                "candidate_id": candidate_id,
                "decision_data": decision_data,
                "insights": decision_insights,
                "status": decision
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error making final decision: {str(e)}"
            }
    
    def _generate_review_insights(self, rating: int, notes: str, decision: str) -> List[str]:
        """Generate insights from candidate review"""
        insights = []
        
        if rating >= 8:
            insights.append("High potential candidate with strong qualifications")
        elif rating >= 6:
            insights.append("Good candidate with room for growth")
        elif rating >= 4:
            insights.append("Average candidate requiring careful consideration")
        else:
            insights.append("Below average candidate - not recommended")
        
        if decision == 'approved':
            insights.append("Recommended for interview stage")
        elif decision == 'rejected':
            insights.append("Not suitable for current position")
        elif decision == 'interview_required':
            insights.append("Additional evaluation needed")
        
        return insights
    
    def _get_recommendation_from_rating(self, rating: int) -> str:
        """Get recommendation based on rating"""
        if rating >= 8:
            return "Strongly recommend"
        elif rating >= 6:
            return "Recommend"
        elif rating >= 4:
            return "Consider"
        else:
            return "Do not recommend"
    
    def _get_next_steps(self, decision: str) -> List[str]:
        """Get next steps based on decision"""
        if decision == 'approved':
            return ["Schedule interview", "Prepare interview questions", "Notify candidate"]
        elif decision == 'rejected':
            return ["Send rejection notification", "Update candidate status", "Archive application"]
        elif decision == 'interview_required':
            return ["Schedule additional screening", "Prepare technical assessment", "Request references"]
        else:
            return ["Review application further", "Request additional information"]
    
    def _generate_feedback_insights(self, technical: int, communication: int, 
                                  culture_fit: int, recommendation: str) -> List[str]:
        """Generate insights from interview feedback"""
        insights = []
        
        if technical >= 8:
            insights.append("Excellent technical skills")
        elif technical >= 6:
            insights.append("Good technical foundation")
        else:
            insights.append("Technical skills need improvement")
        
        if communication >= 8:
            insights.append("Strong communication abilities")
        elif communication >= 6:
            insights.append("Adequate communication skills")
        else:
            insights.append("Communication skills need development")
        
        if culture_fit >= 8:
            insights.append("Excellent cultural fit")
        elif culture_fit >= 6:
            insights.append("Good cultural alignment")
        else:
            insights.append("Cultural fit concerns")
        
        if recommendation == 'hire':
            insights.append("Recommended for hire")
        elif recommendation == 'second_interview':
            insights.append("Recommended for second interview")
        else:
            insights.append("Not recommended for hire")
        
        return insights
    
    def _generate_decision_insights(self, decision: str, salary_offer: Optional[int], 
                                  notes: str) -> List[str]:
        """Generate insights from final decision"""
        insights = []
        
        if decision == 'hire':
            insights.append("Candidate selected for position")
            if salary_offer:
                insights.append(f"Salary offer: ${salary_offer:,}")
        elif decision == 'reject':
            insights.append("Candidate not selected")
        elif decision == 'hold':
            insights.append("Decision deferred")
        
        if notes:
            insights.append(f"Additional notes: {notes}")
        
        return insights