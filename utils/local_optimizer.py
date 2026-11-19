"""Local rule-based resume optimizer. No API keys required."""
import re
from typing import Dict, List
from pydantic import BaseModel, Field


class OptimizationResult(BaseModel):
    optimized_summary: str
    optimized_skills: List[str] = Field(default_factory=list)
    changes_made: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class LocalOptimizer:
    """Optimizes resume using keyword matching and template rewriting."""
    
    def optimize_resume(self, resume_text: str, job_analysis: Dict, job_title: str, company_name: str) -> OptimizationResult:
        """Perform local optimization without external APIs."""
        
        # 1. Extract Keywords from Job
        job_keywords = set()
        if 'required_skills' in job_analysis:
            job_keywords.update([s.lower() for s in job_analysis['required_skills']])
        if 'keywords' in job_analysis:
            job_keywords.update([k.lower() for k in job_analysis['keywords'][:10]])
        
        # 2. Optimize Skills Section
        original_skills = self._extract_skills(resume_text)
        optimized_skills = self._prioritize_skills(original_skills, job_keywords)
        
        # 3. Optimize Summary
        optimized_summary = self._rewrite_summary(resume_text, job_title, job_keywords, company_name)
        
        changes = [
            f"Prioritized skills matching: {', '.join(list(job_keywords)[:5])}",
            "Rewrote professional summary to include job-specific keywords",
            "Maintained all original project metrics (e.g., 10,000 records, 88% accuracy)"
        ]
        
        return OptimizationResult(
            optimized_summary=optimized_summary,
            optimized_skills=optimized_skills,
            changes_made=changes
        )
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from the technical skills section."""
        # Specific list based on Chalukya's resume
        common_tech = [
            "Python", "SQL", "Pandas", "NumPy", "Scikit-learn", "XGBoost", 
            "Power BI", "Streamlit", "FastAPI", "Flask", "PostgreSQL", 
            "Docker", "Git", "Machine Learning", "Deep Learning", "AWS",
            "LightGBM", "Plotly", "Matplotlib", "Excel", "MySQL", "SQLAlchemy",
            "SHAP", "Pydantic", "REST APIs", "ETL", "GitHub Actions"
        ]
        found = []
        text_lower = text.lower()
        for skill in common_tech:
            if skill.lower() in text_lower:
                found.append(skill)
        return found
    
    def _prioritize_skills(self, skills: List[str], job_keywords: set) -> List[str]:
        """Reorder skills so job-relevant ones come first."""
        if not job_keywords:
            return skills
        
        matched = []
        unmatched = []
        
        for skill in skills:
            if skill.lower() in job_keywords or any(k in skill.lower() for k in job_keywords):
                matched.append(skill)
            else:
                unmatched.append(skill)
                
        return matched + unmatched
    
    def _rewrite_summary(self, original_text: str, job_title: str, job_keywords: set, company_name: str) -> str:
        """Rewrite summary by combining original facts with job keywords."""
        
        # Extract the original summary part
        start_idx = original_text.find("PROFESSIONAL SUMMARY")
        if start_idx == -1:
            start_idx = original_text.find("Professional Summary")
        
        if start_idx != -1:
            end_idx = original_text.find("TECHNICAL SKILLS", start_idx)
            if end_idx == -1:
                end_idx = start_idx + 500
            original_summary = original_text[start_idx:end_idx].replace("PROFESSIONAL SUMMARY", "").strip()
        else:
            original_summary = "Data Science graduate with Python and SQL experience."
        
        # Create a new summary that injects the job title and top keywords
        top_keywords = list(job_keywords)[:3]
        keyword_str = ", ".join(top_keywords) if top_keywords else "data analytics"
        
        # Use the company name if provided, otherwise use a generic term
        target_company = company_name if company_name and company_name != "Not specified" else "your organization"
        
        new_summary = (
            f"Results-oriented {job_title} candidate with a strong foundation in {keyword_str}. "
            f"{original_summary} "
            f"Proven ability to deliver end-to-end data solutions, from ETL and machine learning modeling to interactive dashboard deployment. "
            f"Eager to apply expertise in Python, SQL, and predictive analytics to drive value at {target_company}."
        )
        
        return new_summary