"""DOCX formatting preservation module.
Modifies DOCX content while preserving original formatting, styles, and structure."""
import os
from typing import Dict, List
from docx import Document
from pydantic import BaseModel


class FormattingPreservationResult(BaseModel):
    """Result of DOCX formatting preservation operation."""
    success: bool
    output_path: str
    warnings: List[str] = []
    preserved_elements: Dict[str, int] = {}


class DOCXFormatter:
    """Preserves and applies DOCX formatting during resume optimization."""
    
    def __init__(self):
        self.preserved_styles = {}
    
    def create_tailored_docx(self, original_path: str, optimized_content: Dict, output_path: str) -> FormattingPreservationResult:
        """Create tailored DOCX preserving original formatting."""
        try:
            doc = Document(original_path)
            
            preserved = {
                "paragraphs": len(doc.paragraphs),
                "tables": len(doc.tables),
                "sections": len(doc.sections)
            }
            
            self._apply_optimizations(doc, optimized_content)
            
            doc.save(output_path)
            
            return FormattingPreservationResult(
                success=True,
                output_path=output_path,
                preserved_elements=preserved
            )
        except Exception as e:
            return FormattingPreservationResult(
                success=False,
                output_path="",
                warnings=[f"Error: {str(e)}"]
            )
    
    def _apply_optimizations(self, doc: Document, optimized_content: Dict):
        """Apply optimized content to document while preserving formatting."""
        if "optimized_summary" in optimized_content:
            self._replace_section_text(doc, ["summary", "professional summary"], optimized_content["optimized_summary"])
        
        if "optimized_skills" in optimized_content:
            self._update_skills_section(doc, optimized_content["optimized_skills"])
    
    def _replace_section_text(self, doc: Document, section_headers: List[str], new_text: str):
        """Replace text in a specific section while preserving formatting."""
        in_target_section = False
        
        for para in doc.paragraphs:
            para_text = para.text.lower().strip()
            
            if any(header in para_text for header in section_headers):
                in_target_section = True
                continue
            
            if in_target_section and para_text:
                while para.runs:
                    para._element.remove(para.runs[0]._element)
                
                run = para.add_run(new_text[:300])
                break
    
    def _update_skills_section(self, doc: Document, new_skills: List[str]):
        """Update skills section with optimized skills list."""
        in_skills_section = False
        
        for para in doc.paragraphs:
            para_text = para.text.lower().strip()
            
            if "skills" in para_text:
                in_skills_section = True
                continue
            
            if in_skills_section and para.runs:
                skills_text = ", ".join(new_skills[:15])
                para.runs[0].text = skills_text
                break
    
    def validate_docx(self, file_path: str) -> List[str]:
        """Validate DOCX file integrity."""
        warnings = []
        try:
            doc = Document(file_path)
            if not doc.paragraphs:
                warnings.append("Document has no paragraphs")
        except Exception as e:
            warnings.append(f"Validation error: {str(e)}")
        return warnings