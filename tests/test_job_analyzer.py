"""Tests for job analyzer."""
import pytest
from utils.job_analyzer import JobAnalyzer, JobAnalysis


class TestJobAnalyzer:
    def test_analyze_job_description(self):
        analyzer = JobAnalyzer()
        result = analyzer.analyze(
            "Senior Python Developer",
            "Tech Corp",
            "Looking for Python developer with SQL and Docker experience. 5+ years required."
        )
        
        assert isinstance(result, JobAnalysis)
        assert result.job_title == "Senior Python Developer"
        assert "python" in [s.lower() for s in result.required_skills]
    
    def test_empty_job_description(self):
        analyzer = JobAnalyzer()
        with pytest.raises(ValueError):
            analyzer.analyze("Title", "Company", "")