"""
FilterAI agent for candidate filtering and ranking
"""

from typing import Dict, List, Any, Optional
from langchain.schema import HumanMessage, AIMessage
from src.models.llm_config import llm_config
from src.agentic_prompts.prompts import FILTER_AI_PROMPT
import json

class FilterAI:
    """FilterAI agent for candidate analysis and filtering"""
    
    def __init__(self):
        self.llm = llm_config.get_llm()
        self.name = "FilterAI"
    
    def analyze_candidate(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single candidate against job requirements"""
        try:
            # Calculate skill match score
            skill_score = self._calculate_skill_match(candidate.get('skills', []), 
                                                    job.get('skills_required', []))
            
            # Calculate experience match score
            exp_score = self._calculate_experience_match(candidate.get('experience', ''), 
                                                       job.get('experience_level', ''))
            
            # Calculate education match score
            edu_score = self._calculate_education_match(candidate.get('education', ''), 
                                                       job.get('requirements', []))
            
            # Calculate overall score
            overall_score = (skill_score * 0.4) + (exp_score * 0.3) + (edu_score * 0.2) + (10 * 0.1)
            
            analysis = {
                "candidate_id": candidate.get('id'),
                "job_id": job.get('id'),
                "skill_match_score": skill_score,
                "experience_match_score": exp_score,
                "education_match_score": edu_score,
                "overall_score": round(overall_score, 2),
                "ranking": self._get_ranking_category(overall_score),
                "recommendations": self._generate_recommendations(candidate, job, overall_score)
            }
            
            return analysis
            
        except Exception as e:
            return {"error": f"Error analyzing candidate: {str(e)}"}
    
    def rank_candidates(self, candidates: List[Dict[str, Any]], 
                       job: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank all candidates for a job"""
        try:
            analyzed_candidates = []
            
            for candidate in candidates:
                analysis = self.analyze_candidate(candidate, job)
                if 'error' not in analysis:
                    analysis['candidate_data'] = candidate
                    analyzed_candidates.append(analysis)
            
            # Sort by overall score in descending order
            analyzed_candidates.sort(key=lambda x: x['overall_score'], reverse=True)
            
            return analyzed_candidates
            
        except Exception as e:
            return [{"error": f"Error ranking candidates: {str(e)}"}]
    
    def _calculate_skill_match(self, candidate_skills: List[str], 
                             required_skills: List[str]) -> float:
        """Calculate skill match percentage"""
        if not required_skills:
            return 50.0
        
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        matches = sum(1 for skill in required_skills_lower if skill in candidate_skills_lower)
        return (matches / len(required_skills_lower)) * 100
    
    def _calculate_experience_match(self, candidate_exp: str, required_exp: str) -> float:
        """Calculate experience match score"""
        if not required_exp:
            return 50.0
        
        # Extract years from experience strings
        candidate_years = self._extract_years(candidate_exp)
        required_years = self._extract_years(required_exp)
        
        if candidate_years >= required_years:
            return 100.0
        elif candidate_years >= required_years * 0.8:
            return 80.0
        elif candidate_years >= required_years * 0.6:
            return 60.0
        else:
            return 30.0
    
    def _calculate_education_match(self, candidate_edu: str, requirements: List[str]) -> float:
        """Calculate education match score"""
        if not requirements:
            return 50.0
        
        edu_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college']
        candidate_edu_lower = candidate_edu.lower() if candidate_edu else ''
        
        education_score = 0
        for keyword in edu_keywords:
            if keyword in candidate_edu_lower:
                education_score += 20
        
        return min(education_score, 100.0)
    
    def _extract_years(self, text: str) -> int:
        """Extract years from text"""
        import re
        if not text:
            return 0
        
        pattern = r'(\d+)\s*years?'
        matches = re.findall(pattern, text.lower())
        return int(matches[0]) if matches else 0
    
    def _get_ranking_category(self, score: float) -> str:
        """Get ranking category based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Average"
        else:
            return "Below Average"
    
    def _generate_recommendations(self, candidate: Dict[str, Any], 
                                job: Dict[str, Any], score: float) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if score >= 80:
            recommendations.append("Highly recommended for interview")
            recommendations.append("Strong match for the position")
        elif score >= 60:
            recommendations.append("Good candidate worth considering")
            recommendations.append("May need some additional evaluation")
        elif score >= 40:
            recommendations.append("Average candidate")
            recommendations.append("Consider for backup positions")
        else:
            recommendations.append("Below requirements")
            recommendations.append("May not be suitable for this role")
        
        return recommendations
    
    def filter_candidates(self, candidates: List[Dict[str, Any]], 
                         job: Dict[str, Any], 
                         filter_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Filter candidates based on criteria and job requirements"""
        try:
            # First rank all candidates
            ranked_candidates = self.rank_candidates(candidates, job)
            
            # Apply filter criteria
            filtered_candidates = []
            
            for candidate_analysis in ranked_candidates:
                if 'error' in candidate_analysis:
                    continue
                
                candidate = candidate_analysis['candidate_data']
                score = candidate_analysis['overall_score']
                
                # Check minimum experience
                min_experience = filter_criteria.get('min_experience', 0)
                candidate_years = self._extract_years(candidate.get('experience', ''))
                if candidate_years < min_experience:
                    continue
                
                # Check required skills
                required_skills = filter_criteria.get('required_skills', [])
                if required_skills:
                    candidate_skills = [skill.lower() for skill in candidate.get('skills', [])]
                    required_skills_lower = [skill.lower() for skill in required_skills]
                    if not all(skill in candidate_skills for skill in required_skills_lower):
                        continue
                
                # Check education level
                education_level = filter_criteria.get('education_level', 'Any')
                if education_level != 'Any':
                    candidate_edu = candidate.get('education', '').lower()
                    if education_level.lower() not in candidate_edu:
                        continue
                
                # Check minimum score threshold
                score_threshold = filter_criteria.get('score_threshold', 0)
                if score < score_threshold:
                    continue
                
                # Add candidate to filtered list with analysis data
                filtered_candidate = candidate.copy()
                filtered_candidate.update({
                    'match_score': score,
                    'ranking': candidate_analysis['ranking'],
                    'recommendations': candidate_analysis['recommendations']
                })
                filtered_candidates.append(filtered_candidate)
            
            return {
                "success": True,
                "filtered_candidates": filtered_candidates,
                "total_candidates": len(candidates),
                "filtered_count": len(filtered_candidates),
                "filter_criteria": filter_criteria
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error filtering candidates: {str(e)}",
                "filtered_candidates": []
            }