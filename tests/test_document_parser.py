"""Tests for document parser."""
import pytest
from docx import Document
from utils.document_parser import DocumentParser, ResumeContent


@pytest.fixture
def sample_docx(tmp_path):
    """Create a sample DOCX file for testing."""
    doc_path = tmp_path / "test_resume.docx"
    doc = Document()
    
    doc.add_heading("John Doe", 0)
    doc.add_paragraph("john.doe@email.com")
    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph("Experienced software engineer with 5 years of experience.")
    doc.add_heading("Experience", level=1)
    doc.add_paragraph("Software Engineer at Tech Corp (2020-2023)")
    doc.add_heading("Skills", level=1)
    doc.add_paragraph("Python, JavaScript, SQL")
    doc.add_heading("Education", level=1)
    doc.add_paragraph("B.S. Computer Science, University Name (2016-2020)")
    
    doc.save(str(doc_path))
    return str(doc_path)


class TestDocumentParser:
    def test_validate_file_exists(self, sample_docx):
        parser = DocumentParser()
        valid, message = parser.validate_file(sample_docx)
        assert valid is True
        assert message == "Valid"
    
    def test_validate_file_not_exists(self):
        parser = DocumentParser()
        valid, message = parser.validate_file("/nonexistent/file.docx")
        assert valid is False
    
    def test_parse_docx(self, sample_docx):
        parser = DocumentParser()
        content = parser.parse_docx(sample_docx)
        
        assert isinstance(content, ResumeContent)
        assert len(content.paragraphs) > 0
        assert "John Doe" in content.raw_text