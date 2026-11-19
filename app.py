"""AI Resume Tailor - Main Streamlit Application.
A one-day MVP for AI-powered resume tailoring (Local Mode - No API Keys)."""
import os
import sys
import tempfile
import shutil
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from config import config
from utils.document_parser import DocumentParser
from utils.job_analyzer import JobAnalyzer
from utils.local_optimizer import LocalOptimizer
from utils.docx_formatter import DOCXFormatter
from utils.pdf_generator import PDFGenerator
from utils.ats_validator import ATSValidator
from utils.qa_checks import QualityAssurance

st.set_page_config(page_title="AI Resume Tailor", page_icon="📄", layout="wide")


def initialize_session_state():
    """Initialize session state variables."""
    if "resume_uploaded" not in st.session_state:
        st.session_state.resume_uploaded = False
    if "resume_path" not in st.session_state:
        st.session_state.resume_path = None
    if "resume_content" not in st.session_state:
        st.session_state.resume_content = None
    if "job_analysis" not in st.session_state:
        st.session_state.job_analysis = None
    if "optimized_content" not in st.session_state:
        st.session_state.optimized_content = None
    if "tailored_docx_path" not in st.session_state:
        st.session_state.tailored_docx_path = None
    if "tailored_pdf_path" not in st.session_state:
        st.session_state.tailored_pdf_path = None
    # For scraped data
    if "scraped_title" not in st.session_state:
        st.session_state.scraped_title = ""
    if "scraped_desc" not in st.session_state:
        st.session_state.scraped_desc = ""


def validate_api_key():
    """No API key needed for local optimization."""
    return True


def handle_resume_upload():
    """Handle resume file upload and parsing."""
    st.subheader("📤 Upload Your Resume")
    
    uploaded_file = st.file_uploader("Upload resume (DOCX format)", type=["docx"])
    
    if uploaded_file is not None:
        temp_dir = tempfile.mkdtemp(prefix="resume_")
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        parser = DocumentParser()
        valid, message = parser.validate_file(temp_path)
        
        if not valid:
            st.error(f"❌ Invalid file: {message}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None
        
        try:
            with st.spinner("Parsing resume..."):
                resume_content = parser.parse_docx(temp_path)
            
            st.session_state.resume_uploaded = True
            st.session_state.resume_path = temp_path
            st.session_state.resume_content = resume_content
            
            st.success("✅ Resume uploaded successfully!")
            st.info(f"Found {len(resume_content.paragraphs)} paragraphs, {resume_content.table_count} tables")
            
            return resume_content
        except Exception as e:
            st.error(f"❌ Error parsing resume: {str(e)}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None
    
    return None


def display_resume_preview(resume_content):
    """Display resume content preview."""
    if resume_content is None:
        return
    
    st.subheader("👁️ Resume Preview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Sections Detected:**")
        if resume_content.sections:
            for section_name in resume_content.sections.keys():
                st.write(f"• {section_name.title()}")
        else:
            st.write("No standard sections detected")
    
    with col2:
        st.metric("Paragraphs", len(resume_content.paragraphs))
        st.metric("Tables", resume_content.table_count)


def handle_job_input():
    """Handle job description input via URL or manual paste."""
    st.subheader("💼 Job Details")
    
    # Option 1: Paste Link
    job_url = st.text_input("🔗 Paste Job Post Link (LinkedIn, Naukri, etc.)", placeholder="https://...")
    
    # Option 2: Manual Input (Fallback)
    with st.expander("Or enter details manually"):
        col1, col2 = st.columns(2)
        with col1:
            # Use scraped title if available, otherwise empty
            manual_title = st.text_input("Job Title *", value=st.session_state.scraped_title, placeholder="e.g., Senior Python Developer")
        with col2:
            company_name = st.text_input("Company Name (Optional)", placeholder="e.g., Tech Corp")
        # Use scraped desc if available, otherwise empty
        manual_desc = st.text_area("Job Description *", value=st.session_state.scraped_desc, height=200, placeholder="Paste the complete job description here...")
    
    # Logic to handle URL scraping
    if job_url:
        if st.button("🌐 Fetch Job Details from Link", type="primary"):
            with st.spinner("Scraping job details..."):
                try:
                    from utils.job_scraper import JobScraper
                    scraper = JobScraper()
                    details = scraper.extract_job_details(job_url)
                    
                    if details:
                        st.session_state.scraped_title = details['title']
                        st.session_state.scraped_desc = details['description']
                        st.success("✅ Job details fetched! Please review below.")
                        # Trigger a rerun to update the input fields
                        st.rerun()
                    else:
                        st.warning("⚠️ Could not automatically extract details. Please use the manual section.")
                        
                except Exception as e:
                    st.error(f"❌ Scraping error: {str(e)}")
    
    # Determine final values for analysis
    final_title = manual_title if manual_title else st.session_state.scraped_title
    final_desc = manual_desc if manual_desc else st.session_state.scraped_desc
    
    if final_title and final_desc:
        if st.button("🔍 Analyze Job Description", type="secondary"):
            with st.spinner("Analyzing job description..."):
                try:
                    analyzer = JobAnalyzer()
                    job_analysis = analyzer.analyze(final_title, company_name or "Not specified", final_desc)
                    
                    st.session_state.job_analysis = job_analysis
                    st.success("✅ Job analysis complete!")
                    return job_analysis
                except Exception as e:
                    st.error(f"❌ Error analyzing job: {str(e)}")
                    return None
    
    return None


def display_job_analysis(job_analysis):
    """Display job analysis results."""
    if job_analysis is None:
        return
    
    st.subheader("📊 Job Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Required Skills", len(job_analysis.required_skills))
    with col2:
        st.metric("Experience Level", job_analysis.experience_level.title())
    with col3:
        st.metric("Responsibilities", len(job_analysis.responsibilities))
    
    with st.expander("View Required Skills"):
        if job_analysis.required_skills:
            for skill in job_analysis.required_skills:
                st.write(f"✓ {skill}")
        else:
            st.write("No specific required skills detected")


def calculate_skill_match():
    """Calculate and display skill match between resume and job."""
    if not st.session_state.resume_content or not st.session_state.job_analysis:
        return None
    
    resume_text = st.session_state.resume_content.raw_text.lower()
    
    # Expanded list to catch more of Chalukya's specific skills
    common_skills = [
        "python", "sql", "machine learning", "power bi", "fastapi", "flask", 
        "docker", "git", "postgresql", "mysql", "pandas", "numpy", "scikit-learn",
        "xgboost", "lightgbm", "streamlit", "plotly", "excel", "aws", "etl",
        "shap", "pydantic", "rest apis", "github actions"
    ]
    
    resume_skills = set()
    for skill in common_skills:
        if skill in resume_text:
            resume_skills.add(skill)
    
    analyzer = JobAnalyzer()
    match_result = analyzer.calculate_skill_match(resume_skills, st.session_state.job_analysis)
    
    return match_result


def display_skill_match(match_result):
    """Display skill match analysis."""
    if match_result is None:
        return
    
    st.subheader("🎯 Skill Match Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Match Score", f"{match_result['match_percentage']}%")
    
    with col2:
        status = "✓ Good Match" if match_result["match_percentage"] >= 60 else "⚠ Needs Improvement"
        st.info(status)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.write("**Matched Skills:**")
        for skill in match_result.get("matched_required", []):
            st.success(f"• {skill}")
    
    with col4:
        st.write("**Missing Skills:**")
        for skill in match_result.get("missing_required", []):
            st.warning(f"• {skill}")


def optimize_resume_with_claude():
    """Optimize resume using Local Rule-Based Engine (No API Key)."""
    if not st.session_state.resume_content or not st.session_state.job_analysis:
        st.error("Please upload resume and analyze job first")
        return None
    
    st.subheader("🤖 AI Optimization (Local Mode)")
    
    st.info("""
    **How this works:**
    - Uses smart keyword matching to prioritize your skills.
    - Rewrites your summary to match the job title.
    - 100% Offline: No data is sent to any external server.
    - All your project metrics (e.g., 10,000 records, 88% accuracy) are preserved exactly.
    """)
    
    if st.button("✨ Optimize Resume", type="primary"):
        with st.spinner("Optimizing locally..."):
            try:
                resume_text = st.session_state.resume_content.raw_text
                
                job_analysis_dict = {
                    "required_skills": st.session_state.job_analysis.required_skills,
                    "keywords": st.session_state.job_analysis.keywords
                }
                
                # Use Local Optimizer
                optimizer = LocalOptimizer()
                
                optimized = optimizer.optimize_resume(
                    resume_text=resume_text,
                    job_analysis=job_analysis_dict,
                    job_title=st.session_state.job_analysis.job_title,
                    company_name=st.session_state.job_analysis.company_name
                )
                
                st.session_state.optimized_content = optimized
                st.success("✅ Resume optimization complete!")
                return optimized
                
            except Exception as e:
                st.error(f"❌ Optimization error: {str(e)}")
                return None
    
    return None


def display_optimization_results(optimized):
    """Display optimization results."""
    if optimized is None:
        return
    
    st.subheader("📝 Optimization Results")
    
    with st.expander("Optimized Professional Summary", expanded=True):
        st.write(optimized.optimized_summary)
    
    with st.expander("Optimized Skills List"):
        if optimized.optimized_skills:
            for skill in optimized.optimized_skills:
                st.write(f"• {skill}")
    
    if optimized.changes_made:
        with st.expander("Changes Made"):
            for change in optimized.changes_made:
                st.write(f"✓ {change}")
    
    if optimized.warnings:
        with st.expander("⚠️ Warnings"):
            for warning in optimized.warnings:
                st.warning(warning)


def generate_tailored_documents():
    """Generate tailored DOCX and PDF documents."""
    if not st.session_state.resume_path or not st.session_state.optimized_content:
        st.error("Please complete previous steps first")
        return False
    
    st.subheader("📄 Generate Documents")
    
    if st.button("🚀 Generate Tailored Resume", type="primary"):
        with st.spinner("Generating tailored resume..."):
            try:
                output_dir = tempfile.mkdtemp(prefix="tailored_")
                
                formatter = DOCXFormatter()
                docx_output = os.path.join(output_dir, "tailored_resume.docx")
                
                optimized_dict = {
                    "optimized_summary": st.session_state.optimized_content.optimized_summary,
                    "optimized_skills": st.session_state.optimized_content.optimized_skills
                }
                
                docx_result = formatter.create_tailored_docx(
                    original_path=st.session_state.resume_path,
                    optimized_content=optimized_dict,
                    output_path=docx_output
                )
                
                if not docx_result.success:
                    st.error(f"❌ DOCX generation failed: {docx_result.warnings}")
                    return False
                
                st.session_state.tailored_docx_path = docx_output
                
                pdf_generator = PDFGenerator(libreoffice_path=config.libreoffice_path)
                pdf_result = pdf_generator.convert_to_pdf(docx_output, output_dir)
                
                if pdf_result.success:
                    st.session_state.tailored_pdf_path = pdf_result.pdf_path
                    st.success("✅ PDF generated successfully!")
                else:
                    st.warning(f"⚠️ PDF generation had issues: {pdf_result.warnings}")
                    st.info("DOCX file is ready. Install LibreOffice for PDF conversion.")
                
                qa = QualityAssurance()
                qa_result = qa.run_all_checks(
                    original_text=st.session_state.resume_content.raw_text,
                    optimized_text=st.session_state.optimized_content.optimized_summary,
                    docx_path=docx_output,
                    pdf_path=pdf_result.pdf_path if pdf_result.success else None
                )
                
                if qa_result.passed:
                    st.success("✅ All quality checks passed!")
                else:
                    st.warning(f"⚠️ {qa_result.checks_failed} quality check(s) failed")
                    for issue in qa_result.issues:
                        st.warning(f"• {issue}")
                
                return True
                
            except Exception as e:
                st.error(f"❌ Document generation error: {str(e)}")
                return False
    
    return False


def display_download_section():
    """Display download buttons for generated documents."""
    if not st.session_state.tailored_docx_path:
        return
    
    st.subheader("⬇️ Download Your Tailored Resume")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if os.path.exists(st.session_state.tailored_docx_path):
            with open(st.session_state.tailored_docx_path, "rb") as f:
                st.download_button(
                    label="📄 Download DOCX",
                    data=f.read(),
                    file_name="tailored_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary"
                )
    
    with col2:
        if st.session_state.tailored_pdf_path and os.path.exists(st.session_state.tailored_pdf_path):
            with open(st.session_state.tailored_pdf_path, "rb") as f:
                st.download_button(
                    label="📑 Download PDF",
                    data=f.read(),
                    file_name="tailored_resume.pdf",
                    mime="application/pdf"
                )
        else:
            st.info("PDF not available. Install LibreOffice for PDF conversion.")


def run_ats_validation():
    """Run ATS validation on the tailored resume."""
    if not st.session_state.tailored_docx_path:
        return
    
    st.subheader("✓ ATS Validation")
    
    if st.button("🔍 Run ATS Check"):
        with st.spinner("Validating ATS compatibility..."):
            try:
                parser = DocumentParser()
                tailored_content = parser.parse_docx(st.session_state.tailored_docx_path)
                
                validator = ATSValidator()
                ats_result = validator.validate(
                    docx_path=st.session_state.tailored_docx_path,
                    text_content=tailored_content.raw_text
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("ATS Score", f"{ats_result.score}/100")
                
                with col2:
                    status = "✅ ATS Friendly" if ats_result.passed else "❌ Needs Work"
                    st.info(status)
                
                if ats_result.issues:
                    with st.expander("Issues Found"):
                        for issue in ats_result.issues:
                            st.error(f"• {issue}")
                
                if ats_result.recommendations:
                    with st.expander("Recommendations"):
                        for rec in ats_result.recommendations:
                            st.info(f"• {rec}")
                
            except Exception as e:
                st.error(f"❌ ATS validation error: {str(e)}")


def main():
    """Main application flow."""
    st.title("📄 AI Resume Tailor")
    st.markdown("Transform your resume for any job application with AI-powered optimization")
    
    initialize_session_state()
    
    with st.sidebar:
        st.header("How It Works")
        st.markdown("""
        1. 📤 Upload your base resume (DOCX)
        2. 💼 Paste Job Link or Enter Details
        3. 🔍 Analyze job requirements
        4. 🤖 Optimize with AI
        5. 📄 Generate tailored resume
        6. ⬇️ Download DOCX and PDF
        """)
        
        st.divider()
        
        st.header("Status")
        if st.session_state.resume_uploaded:
            st.success("✓ Resume uploaded")
        else:
            st.info("○ Resume not uploaded")
        
        if st.session_state.job_analysis:
            st.success("✓ Job analyzed")
        else:
            st.info("○ Job not analyzed")
        
        if st.session_state.optimized_content:
            st.success("✓ Resume optimized")
        else:
            st.info("○ Not optimized")
        
        if st.session_state.tailored_docx_path:
            st.success("✓ Documents generated")
        else:
            st.info("○ Not generated")
        
        st.divider()
        st.caption("Built with Streamlit, Local Optimizer, and python-docx")
    
    st.markdown("---")
    
    # Step 1: Upload Resume
    resume_content = handle_resume_upload()
    
    if resume_content:
        display_resume_preview(resume_content)
        st.markdown("---")
        
        # Step 2: Job Input (Link or Manual)
        job_analysis = handle_job_input()
        
        if job_analysis or st.session_state.job_analysis:
            display_job_analysis(job_analysis or st.session_state.job_analysis)
            
            match_result = calculate_skill_match()
            display_skill_match(match_result)
            
            st.markdown("---")
            
            # Step 3: AI Optimization
            optimized = optimize_resume_with_claude()
            
            if optimized or st.session_state.optimized_content:
                display_optimization_results(optimized or st.session_state.optimized_content)
                
                st.markdown("---")
                
                # Step 4: Generate Documents
                generate_tailored_documents()
                
                if st.session_state.tailored_docx_path:
                    display_download_section()
                    st.markdown("---")
                    run_ats_validation()


if __name__ == "__main__":
    main()