"""Resume parsing and content extraction module.
Handles DOCX file parsing while preserving formatting information."""
import os
from typing import Dict, List, Optional, Tuple
from docx import Document
from pydantic import BaseModel, Field


class ParagraphInfo(BaseModel):
    """Information about a paragraph including formatting."""
    text: str
    style_name: str
    font_name: Optional[str] = None
    font_size: Optional[int] = None
    is_bold: bool = False
    is_italic: bool = False
    alignment: str = "left"
    is_heading: bool = False
    level: int = 0


class ResumeContent(BaseModel):
    """Structured resume content with formatting metadata."""
    paragraphs: List[ParagraphInfo] = Field(default_factory=list)
    raw_text: str = ""
    sections: Dict[str, List[ParagraphInfo]] = Field(default_factory=dict)
    has_tables: bool = False
    table_count: int = 0
    original_filename: str = ""
    
    class Config:
        arbitrary_types_allowed = True


class DocumentParser:
    """Parses DOCX resumes and extracts content with formatting."""
    
    def __init__(self):
        self.supported_extensions = ['.docx']
    
    def validate_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate uploaded resume file."""
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.supported_extensions:
            return False, f"Unsupported format: {ext}. Supported: {self.supported_extensions}"
        
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > 10:
            return False, f"File too large: {file_size_mb:.2f}MB (max 10MB)"
        
        return True, "Valid"
    
    def parse_docx(self, file_path: str) -> ResumeContent:
        """Parse DOCX file and extract content with formatting."""
        try:
            doc = Document(file_path)
            
            paragraphs_info = []
            raw_text_parts = []
            sections = {}
            current_section = "header"
            
            for para in doc.paragraphs:
                para_info = self._extract_paragraph_info(para)
                paragraphs_info.append(para_info)
                
                if para_info.text.strip():
                    raw_text_parts.append(para_info.text)
                    
                    if para_info.is_heading or self._is_section_header(para_info):
                        current_section = para_info.text.strip().rstrip(':').lower()
                        if current_section not in sections:
                            sections[current_section] = []
                        sections[current_section].append(para_info)
                    elif current_section in sections:
                        sections[current_section].append(para_info)
            
            table_count = len(doc.tables)
            
            return ResumeContent(
                paragraphs=paragraphs_info,
                raw_text="\n".join(raw_text_parts),
                sections=sections,
                has_tables=table_count > 0,
                table_count=table_count,
                original_filename=os.path.basename(file_path)
            )
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")
    
    def _extract_paragraph_info(self, para) -> ParagraphInfo:
        """Extract formatting information from a paragraph."""
        text = para.text
        style_name = para.style.name if para.style else "Normal"
        is_heading = style_name.startswith("Heading") or "Title" in style_name
        
        level = 0
        if is_heading:
            try:
                level = int(style_name.replace("Heading ", "").replace("Title", "0"))
            except:
                level = 1
        
        font_name = None
        font_size = None
        is_bold = False
        is_italic = False
        
        for run in para.runs:
            if run.font.name and not font_name:
                font_name = run.font.name
            if run.font.size and not font_size:
                font_size = run.font.size.pt if hasattr(run.font.size, 'pt') else run.font.size
            if run.bold:
                is_bold = True
            if run.italic:
                is_italic = True
        
        return ParagraphInfo(
            text=text,
            style_name=style_name,
            font_name=font_name,
            font_size=int(font_size) if font_size else None,
            is_bold=is_bold,
            is_italic=is_italic,
            alignment="left",
            is_heading=is_heading,
            level=level
        )
    
    def _is_section_header(self, para_info: ParagraphInfo) -> bool:
        """Detect if paragraph is a section header."""
        common_sections = [
            "experience", "education", "skills", "projects", 
            "certifications", "summary", "objective", "contact"
        ]
        text_lower = para_info.text.strip().lower().rstrip(':')
        return text_lower in common_sections
    
    def get_text_by_section(self, resume_content: ResumeContent, section_name: str) -> str:
        """Get all text from a specific section."""
        section_key = section_name.lower()
        if section_key in resume_content.sections:
            return "\n".join([p.text for p in resume_content.sections[section_key]])
        return ""