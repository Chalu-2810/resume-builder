"""Tests for PDF generator."""
from utils.pdf_generator import PDFGenerator


class TestPDFGenerator:
    def test_convert_nonexistent_file(self, tmp_path):
        generator = PDFGenerator()
        result = generator.convert_to_pdf(str(tmp_path / "nonexistent.docx"))
        
        assert result.success is False
        assert len(result.warnings) > 0