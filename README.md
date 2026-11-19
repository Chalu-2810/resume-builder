# AI Resume Tailor

A one-day MVP application that uses AI to tailor your resume for specific job applications while preserving the original document formatting.
demo: https://resume-builder-ekcstctmmvwqxuefonmxsc.streamlit.app/

## Features

- **Format Preservation**: Maintains original DOCX template, fonts, styles, and layout
- **AI-Powered Optimization**: Uses Anthropic Claude to optimize content for specific jobs
- **Job Analysis**: Extracts skills, keywords, and requirements from job descriptions
- **Skill Matching**: Compares your resume skills against job requirements
- **ATS Validation**: Checks resume compatibility with Applicant Tracking Systems
- **Dual Export**: Generates both editable DOCX and PDF formats
- **Quality Assurance**: Validates output for factual accuracy and formatting integrity

## Quick Start

### Installation

1. Navigate to ai_resume_tailor directory
2. Create virtual environment: python -m venv venv
3. Activate: source venv/bin/activate (or venv\Scripts\activate on Windows)
4. Install dependencies: pip install -r requirements.txt
5. Copy .env.example to .env and add your ANTHROPIC_API_KEY

### Running the Application

streamlit run app.py

The application will open at http://localhost:8501

## Project Structure

- app.py: Main Streamlit application
- config.py: Configuration management
- utils/: Utility modules for parsing, analysis, and generation
- tests/: Test suite
- temp/: Temporary files

## Usage Workflow

1. Upload Resume (DOCX format)
2. Enter Job Details (title, company, description)
3. Analyze Job Description
4. Review Skill Match
5. Optimize with AI
6. Generate Documents
7. Download tailored resume
8. Run ATS validation

## Important Notes

- Never fabricates information
- Preserves original formatting
- All facts remain unchanged
- API costs apply per optimization

## Testing

Run: pytest tests/ -v

## Known Limitations

1. DOCX-only input
2. Requires LibreOffice for PDF
3. Heuristic section detection
4. Complex layouts may not preserve perfectly
5. No image handling

## Security

- Temporary file storage only
- No data retention
- Environment variables for secrets
- Local processing except Claude API

## License

MIT License

---

Built with: Streamlit, Anthropic Claude, python-docx, PyMuPDF, LibreOffice
