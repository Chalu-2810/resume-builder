"""ATS (Applicant Tracking System) readability validation module."""
import re
from typing import Dict, List
from pydantic import BaseModel


class ATSValidationResult(BaseModel):
    """Result of ATS validation."""
    score: float
    passed: bool
    issues: List[str] = []
    recommendations: List[str] = []
    details: Dict = {}


class ATSValidator:
    """Validates resume for ATS readability."""
    
    def __init__(self):
        self.max_score = 100
    
    def validate(self, docx_path: str, text_content: str) -> ATSValidationResult:
        """Perform comprehensive ATS validation."""
        issues = []
        recommendations = []
        score = self.max_score
        
        if not docx_path.endswith('.docx'):
            issues.append("Not in .docx format")
            score -= 20
        
        if len(text_content.strip()) < 200:
            issues.append("Content too short (< 200 characters)")
            score -= 15
            recommendations.append("Add more detail to experience and skills")
        
        required_sections = ["experience", "education", "skills"]
        text_lower = text_content.lower()
        
        missing_sections = [s for s in required_sections if s not in text_lower]
        if missing_sections:
            issues.append(f"Missing sections: {', '.join(missing_sections)}")
            score -= 10 * len(missing_sections)
        
        has_email = bool(re.search(r'[\w.-]+@[\w.-]+\.\w+', text_content))
        if not has_email:
            issues.append("No email address found")
            score -= 10
            recommendations.append("Add your email address")
        
        bullet_count = len(re.findall(r'[•\-\*]\s', text_content))
        if bullet_count == 0:
            issues.append("No bullet points found")
            score -= 10
            recommendations.append("Use bullet points for achievements")
        
        score = max(0, min(self.max_score, score))
        passed = score >= 60
        
        return ATSValidationResult(
            score=score,
            passed=passed,
            issues=issues,
            recommendations=recommendations,
            details={
                "word_count": len(text_content.split()),
                "bullet_points": bullet_count,
                "has_email": has_email,
                "sections_missing": missing_sections
            }
        )
    
    def get_ats_tips(self) -> List[str]:
        """Return general ATS optimization tips."""
        return [
            "Use standard section headings (Experience, Education, Skills)",
            "Avoid tables, columns, and text boxes",
            "Use simple bullet points",
            "Include relevant keywords from job description",
            "Save as .docx or PDF",
            "Use standard fonts (Arial, Calibri, Times New Roman)",
            "Quantify achievements with numbers"
        ]