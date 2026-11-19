"""Google Gemini API integration for resume optimization."""
import json
import google.generativeai as genai
from typing import Dict, List
from pydantic import BaseModel, Field


class OptimizationResult(BaseModel):
    """Result from AI-powered resume optimization."""
    optimized_summary: str
    optimized_experience: List[Dict[str, str]] = Field(default_factory=list)
    optimized_skills: List[str] = Field(default_factory=list)
    optimized_projects: List[Dict[str, str]] = Field(default_factory=list)
    keywords_added: List[str] = Field(default_factory=list)
    changes_made: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ClaudeClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        if not api_key:
            raise ValueError("Google API key is required")
        
        genai.configure(api_key=api_key)
        self.model_name = model
    
    def optimize_resume(self, resume_text: str, job_analysis: Dict, job_title: str, company_name: str) -> OptimizationResult:
        """Optimize resume content based on job description analysis."""
        prompt = self._build_prompt(resume_text, job_analysis, job_title, company_name)
        
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 4000,
                }
            )
            
            result_text = response.text
            
            # Clean up markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()

            try:
                result_dict = json.loads(result_text)
                return OptimizationResult(**result_dict)
            except json.JSONDecodeError:
                return self._parse_text_response(result_text)
                
        except Exception as e:
            raise ValueError(f"Gemini API error: {str(e)}")
    
    def _build_prompt(self, resume_text: str, job_analysis: Dict, job_title: str, company_name: str) -> str:
        """Build the optimization prompt for Gemini."""
        return f"""
You are an expert resume optimizer. Optimize the following resume for the job: {job_title} at {company_name}.

JOB REQUIREMENTS:
- Required Skills: {', '.join(job_analysis.get('required_skills', []))}
- Keywords: {', '.join(job_analysis.get('keywords', [])[:15])}

ORIGINAL RESUME:
{resume_text}

INSTRUCTIONS:
1. Rewrite professional summary to match the job.
2. Reorder skills by relevance.
3. Optimize bullet points with relevant keywords.
4. NEVER add fake experience or skills.
5. Maintain all factual information (dates, companies, metrics).

Return ONLY a valid JSON object with these keys: 
- "optimized_summary" (string)
- "optimized_skills" (list of strings)
- "changes_made" (list of strings describing what you improved)
- "warnings" (list of strings for any concerns)
"""
    
    def _parse_text_response(self, text: str) -> OptimizationResult:
        """Parse non-JSON text response from Gemini."""
        return OptimizationResult(
            optimized_summary=text[:500],
            optimized_skills=[],
            changes_made=["Parsed from text response"],
            warnings=["Response was not in valid JSON format"]
        )