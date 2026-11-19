"""PDF generation module.
Converts DOCX to PDF using LibreOffice."""
import os
import subprocess
from typing import Optional
from pydantic import BaseModel


class PDFGenerationResult(BaseModel):
    """Result of PDF generation."""
    success: bool
    pdf_path: str = ""
    warnings: list = []


class PDFGenerator:
    """Generates PDF from DOCX using LibreOffice."""
    
    def __init__(self, libreoffice_path: Optional[str] = None):
        self.libreoffice_path = libreoffice_path or self._find_libreoffice()
    
    def _find_libreoffice(self) -> Optional[str]:
        """Find LibreOffice installation."""
        common_paths = [
            "/usr/bin/libreoffice",
            "/usr/bin/soffice",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        try:
            result = subprocess.run(["which", "libreoffice"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def convert_to_pdf(self, docx_path: str, output_dir: Optional[str] = None) -> PDFGenerationResult:
        """Convert DOCX to PDF using LibreOffice."""
        if not os.path.exists(docx_path):
            return PDFGenerationResult(success=False, warnings=["File does not exist"])
        
        if not self.libreoffice_path:
            return PDFGenerationResult(success=False, warnings=["LibreOffice not found"])
        
        if output_dir is None:
            output_dir = os.path.dirname(docx_path)
        
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            cmd = [self.libreoffice_path, "--headless", "--convert-to", "pdf", "--outdir", output_dir, docx_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return PDFGenerationResult(success=False, warnings=[f"Error: {result.stderr}"])
            
            base_name = os.path.splitext(os.path.basename(docx_path))[0]
            pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
            
            if os.path.exists(pdf_path):
                return PDFGenerationResult(success=True, pdf_path=pdf_path)
            else:
                return PDFGenerationResult(success=False, warnings=["PDF not generated"])
                
        except Exception as e:
            return PDFGenerationResult(success=False, warnings=[str(e)])
    
    def validate_pdf(self, pdf_path: str) -> dict:
        """Validate PDF file."""
        result = {"valid": False, "pages": 0, "warnings": []}
        
        try:
            if not os.path.exists(pdf_path):
                result["warnings"].append("File does not exist")
                return result
            
            import fitz
            doc = fitz.open(pdf_path)
            result["pages"] = len(doc)
            result["valid"] = len(doc) > 0
            doc.close()
        except Exception as e:
            result["warnings"].append(str(e))
        
        return result