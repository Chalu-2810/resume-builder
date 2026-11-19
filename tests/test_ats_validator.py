"""Tests for ATS validator."""
from utils.ats_validator import ATSValidator


class TestATSValidator:
    def test_validate_good_resume(self):
        validator = ATSValidator()
        
        good_resume = """
        John Doe
        john.doe@email.com
        
        Professional Summary
        Experienced software engineer.
        
        Experience
        Software Engineer at Tech Corp
        - Developed web applications
        
        Education
        B.S. Computer Science
        
        Skills
        Python, JavaScript, SQL
        """
        
        result = validator.validate("test.docx", good_resume)
        
        assert result.score > 50
    
    def test_get_ats_tips(self):
        validator = ATSValidator()
        tips = validator.get_ats_tips()
        
        assert isinstance(tips, list)
        assert len(tips) > 0