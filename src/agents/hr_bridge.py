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