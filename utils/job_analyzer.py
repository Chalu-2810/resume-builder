"""Job description analysis module.
Extracts keywords, skills, and requirements from job descriptions."""
import re
from typing import Dict, List, Set
from pydantic import BaseModel, Field


class JobAnalysis(BaseModel):
    """Structured analysis of a job description."""
    job_title: str
    company_name: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    experience_level: str = "not specified"
    education_requirements: List[str] = Field(default_factory=list)


class JobAnalyzer:
    """Analyzes job descriptions to extract key information."""
    
    def __init__(self):
        self.tech_skills = {
            "programming": ["python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go"],
            "web": ["html", "css", "react", "angular", "vue", "node.js", "django", "flask", "fastapi"],
            "data": ["sql", "nosql", "mongodb", "postgresql", "mysql", "pandas", "numpy"],
            "ml_ai": ["machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "nlp"],
            "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins"],
            "tools": ["git", "github", "jira", "agile", "scrum", "linux"]
        }
    
    def analyze(self, job_title: str, company_name: str, job_description: str) -> JobAnalysis:
        """Perform comprehensive job description analysis."""
        if not job_description or len(job_description.strip()) < 50:
            raise ValueError("Job description is too short or empty")
        
        jd_lower = job_description.lower()
        
        required_skills = self._find_skills_in_text(jd_lower)
        preferred_skills = []
        keywords = self._extract_keywords(jd_lower)
        responsibilities = self._extract_responsibilities(job_description)
        qualifications = self._extract_qualifications(job_description)
        experience_level = self._determine_experience_level(jd_lower)
        education_requirements = self._extract_education(jd_lower)
        
        return JobAnalysis(
            job_title=job_title,
            company_name=company_name,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            responsibilities=responsibilities,
            qualifications=qualifications,
            keywords=keywords,
            experience_level=experience_level,
            education_requirements=education_requirements
        )
    
    def _find_skills_in_text(self, text: str) -> List[str]:
        """Find technical skills in text."""
        found_skills = []
        for category, skill_list in self.tech_skills.items():
            for skill in skill_list:
                if skill in text:
                    found_skills.append(skill)
        return list(set(found_skills))
    
    def _extract_keywords(self, jd_lower: str) -> List[str]:
        """Extract important keywords from job description."""
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        words = re.findall(r'\b[a-z]{3,}\b', jd_lower)
        keywords = [w for w in words if w not in stop_words]
        
        from collections import Counter
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(30)]
    
    def _extract_responsibilities(self, job_description: str) -> List[str]:
        """Extract job responsibilities."""
        responsibilities = []
        bullet_patterns = [r'[•\-\*]\s*(.+?)(?:\n|$)', r'\d+\.\s*(.+?)(?:\n|$)']
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, job_description)
            for match in matches:
                if len(match.strip()) > 10:
                    responsibilities.append(match.strip())
        
        return responsibilities[:20]
    
    def _extract_qualifications(self, job_description: str) -> List[str]:
        """Extract qualifications and requirements."""
        qualifications = []
        qual_patterns = [r'(?:qualification|requirement)[:\s]*(.*?)(?:\n|$)']
        
        for pattern in qual_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:
                    qualifications.append(match.strip())
        
        return qualifications[:15]
    
    def _determine_experience_level(self, jd_lower: str) -> str:
        """Determine required experience level."""
        if any(term in jd_lower for term in ['entry level', 'junior', '0-2 years']):
            return "entry"
        elif any(term in jd_lower for term in ['mid-level', '3-5 years']):
            return "mid"
        elif any(term in jd_lower for term in ['senior', 'lead', '5+ years']):
            return "senior"
        else:
            return "not specified"
    
    def _extract_education(self, jd_lower: str) -> List[str]:
        """Extract education requirements."""
        education = []
        edu_patterns = [r'(?:bachelor|master|phd|degree)[\s\w]*?(?:in|of)[\s\w]+']
        
        for pattern in edu_patterns:
            matches = re.findall(pattern, jd_lower)
            education.extend(matches)
        
        return list(set(education))
    
    def calculate_skill_match(self, resume_skills: Set[str], job_analysis: JobAnalysis) -> Dict:
        """Calculate skill match between resume and job."""
        required = set(job_analysis.required_skills)
        preferred = set(job_analysis.preferred_skills)
        all_job_skills = required | preferred
        
        matched_required = resume_skills & required
        matched_preferred = resume_skills & preferred
        missing_required = required - resume_skills
        missing_preferred = preferred - resume_skills
        
        if all_job_skills:
            match_percentage = len(resume_skills & all_job_skills) / len(all_job_skills) * 100
        else:
            match_percentage = 0
        
        return {
            "match_percentage": round(match_percentage, 1),
            "matched_required": list(matched_required),
            "matched_preferred": list(matched_preferred),
            "missing_required": list(missing_required),
            "missing_preferred": list(missing_preferred),
            "total_matched": len(matched_required) + len(matched_preferred),
            "total_required": len(required),
            "total_preferred": len(preferred)
        }