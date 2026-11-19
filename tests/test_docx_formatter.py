"""Tests for DOCX formatter."""
import pytest
from docx import Document
from utils.docx_formatter import DOCXFormatter


@pytest.fixture
def sample_docx(tmp_path):
    """Create a sample DOCX file for testing."""
    doc_path = tmp_path / "test_resume.docx"
    doc = Document()
    
    doc.add_heading("John Doe", 0)
    doc.add_paragraph("Original summary text.")
    doc.add_heading("Skills", level=1)
    doc.add_paragraph("Python, Java")
    
    doc.save(str(doc_path))
    return str(doc_path)


class TestDOCXFormatter:
    def test_create_tailored_docx(self, sample_docx, tmp_path):
        formatter = DOCXFormatter()
        output_path = str(tmp_path / "tailored_resume.docx")
        
        optimized_content = {
            "optimized_summary": "Highly skilled Python developer.",
            "optimized_skills": ["Python", "FastAPI", "PostgreSQL"]
        }
        
        result = formatter.create_tailored_docx(
            original_path=sample_docx,
            optimized_content=optimized_content,
            output_path=output_path
        )
        
        assert result.success is True