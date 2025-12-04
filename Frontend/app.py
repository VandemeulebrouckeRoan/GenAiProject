import os
import sys

import gradio as gr
from gradio_client import utils as gradio_client_utils

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Import your pipeline functions
from Backend.utils.pdf_reader import pdf_to_text
from Backend.utils.bullet_extractor import extract_bullets_with_ollama

# Setup path for RAG but don't import yet (lazy loading)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Rag")))

# Initialize RAG matcher (lazy loading)
_matcher = None
DEFAULT_PORT = int(os.getenv("PORT", "7860"))
DEFAULT_SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")


_original_json_schema_to_python_type = gradio_client_utils._json_schema_to_python_type


def _safe_json_schema_to_python_type(schema, defs=None):
    """Avoid Gradio bug when schema is a bare boolean."""
    if isinstance(schema, bool):
        return "bool" if schema else "null"
    return _original_json_schema_to_python_type(schema, defs)


gradio_client_utils._json_schema_to_python_type = _safe_json_schema_to_python_type

def get_matcher():
    """Lazy load the matcher to avoid startup delays."""
    global _matcher
    if _matcher is None:
        from career_coach_matcher import CareerCoachMatcher
        _matcher = CareerCoachMatcher()
    return _matcher


def process_cv(pdf_file, job_title):
    """
    This function is triggered when the user uploads a PDF in Gradio.
    """
    if pdf_file is None:
        return "❌ Please upload a PDF file first.", None, ""
    
    if not job_title or job_title.strip() == "":
        return "❌ Please enter a job title.", None, ""

    try:
        # Temporary txt path
        txt_path = "cv_output.txt"

        # Step 1 — Read PDF → raw text
        # Gradio returns the file path directly as a string
        pdf_path = pdf_file if isinstance(pdf_file, str) else pdf_file.name
        
        print(f"DEBUG: PDF path = {pdf_path}")
        print(f"DEBUG: Job title = {job_title}")
        
        pdf_to_text(pdf_path, txt_path)

        # Load raw text
        with open(txt_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # Step 2 — Ollama cleanup → bullet points (with job context)
        cleaned_bullets = extract_bullets_with_ollama(raw_text)
        
        # Add job title context to output
        result = f"🎯 Target Job: {job_title}\n\n{'='*60}\n\n{cleaned_bullets}"

        # Save for download
        output_path = "clean_bullets.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Target Job: {job_title}\n\n{cleaned_bullets}")

        # Step 3 — RAG Analysis for improvements
        improvement_analysis = analyze_cv_improvements(cleaned_bullets, job_title)
        
        # Step 4 — Generate interview questions
        interview_questions = generate_interview_questions(cleaned_bullets, job_title)

        return result, output_path, improvement_analysis, interview_questions
        
    except Exception as e:
        error_msg = f"❌ Error processing CV: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return error_msg, None, "", ""


def generate_interview_questions(cv_text, job_title):
    """
    Generate interview questions based on job title using RAG.
    """
    if not job_title or job_title.strip() == "":
        job_title = "Software Engineer"
    
    try:
        # Get matcher
        matcher = get_matcher()
        
        # Find relevant job descriptions
        relevant_jobs = matcher.find_jobs_for_resume(cv_text, n_results=3, min_score=0.5)
        
        if not relevant_jobs:
            return "⚠️ No relevant jobs found to generate questions."
        
        # Build interview questions report
        report = f"# 🎤 INTERVIEW PREPARATION QUESTIONS\n\n"
        report += f"**Target Job:** {job_title}\n\n"
        report += "---\n\n"
        
        # General questions based on job
        report += "## 📋 Common Interview Questions\n\n"
        report += f"### For {job_title} Position:\n\n"
        report += "1. **Tell me about yourself and your background**\n"
        report += f"   - *Focus on: Your experience relevant to {job_title} role*\n\n"
        
        report += "2. **Why are you interested in this position?**\n"
        report += f"   - *Highlight: Your passion for {job_title} work and company alignment*\n\n"
        
        report += "3. **What are your greatest strengths?**\n"
        report += "   - *Use STAR method: Situation, Task, Action, Result*\n\n"
        
        report += "4. **Describe a challenging project you worked on**\n"
        report += "   - *Emphasize: Problem-solving skills and technical expertise*\n\n"
        
        report += "5. **Where do you see yourself in 5 years?**\n"
        report += f"   - *Connect: Your growth with {job_title} career path*\n\n"
        
        # Technical/role-specific questions based on job description
        report += "---\n\n"
        report += "## 🔧 Role-Specific Questions\n\n"
        report += "*Based on similar job descriptions in our database:*\n\n"
        
        for i, job in enumerate(relevant_jobs[:2], 1):
            job_desc = job.text[:300]
            report += f"### Scenario {i}:\n"
            report += f"*Related to: {job.metadata.get('job_title', 'Unknown')}*\n\n"
            
            # Extract key skills/topics from job description
            keywords = ['experience', 'skills', 'requirements', 'responsibilities']
            for keyword in keywords:
                if keyword.lower() in job_desc.lower():
                    report += f"- **Question:** Describe your {keyword} related to this role\n"
                    break
            report += "\n"
        
        report += "---\n\n"
        report += "## 💡 PREPARATION TIPS\n\n"
        report += "### Before the Interview:\n"
        report += "- ✅ Research the company thoroughly\n"
        report += "- ✅ Prepare 3-4 STAR method examples\n"
        report += "- ✅ Review your CV and be ready to explain gaps\n"
        report += "- ✅ Prepare questions to ask the interviewer\n\n"
        
        report += "### During the Interview:\n"
        report += "- ✅ Listen carefully to questions before answering\n"
        report += "- ✅ Use specific examples from your experience\n"
        report += "- ✅ Be honest about what you don't know\n"
        report += "- ✅ Show enthusiasm for the role and company\n\n"
        
        report += "### Questions to Ask Them:\n"
        report += "- What does success look like in this role?\n"
        report += "- What are the team dynamics like?\n"
        report += "- What are the biggest challenges facing the team?\n"
        report += "- What opportunities for growth are available?\n"
        
        return report
        
    except Exception as e:
        return f"❌ Error generating questions: {str(e)}"


def analyze_cv_improvements(cv_text, job_title):
    """
    Analyze CV and provide improvement suggestions using RAG.
    """
    if not cv_text or cv_text.strip() == "":
        return "❌ Please provide CV text to analyze."
    
    if not job_title or job_title.strip() == "":
        job_title = "Software Engineer"  # Default
    
    try:
        from collections import Counter
        
        # Get matcher (this loads RAG on first use)
        matcher = get_matcher()
        
        # Find similar CVs
        similar_cvs = matcher.find_resumes_for_job(
            job_title=job_title,
            job_description=cv_text,
            n_results=5,
            min_score=0.5
        )
        
        if not similar_cvs:
            return "⚠️ No similar CVs found in database. Try a different job title."
        
        # Build analysis report
        report = f"# 📊 CV IMPROVEMENT ANALYSIS\n\n"
        report += f"**Target Job:** {job_title}\n\n"
        report += f"**Similar CVs Found:** {len(similar_cvs)}\n\n"
        report += "---\n\n"
        
        # Show top similar CVs
        report += "## 🎯 Top Matching CVs\n\n"
        for i, cv in enumerate(similar_cvs[:3], 1):
            category = cv.metadata.get('category', 'Unknown')
            similarity = cv.similarity_score * 100
            report += f"**{i}. {category}** - Match: {similarity:.1f}%\n"
            report += f"   *Preview:* {cv.text[:150]}...\n\n"
        
        # Extract keywords
        all_keywords = []
        for cv in similar_cvs:
            words = cv.text.lower().split()
            all_keywords.extend(words)
        
        keyword_freq = Counter(all_keywords)
        user_words = set(cv_text.lower().split())
        
        # Find missing keywords
        common_keywords = [word for word, count in keyword_freq.most_common(30) 
                          if count >= 3 and len(word) > 4 and word not in user_words]
        
        report += "---\n\n"
        report += "## 💡 IMPROVEMENT SUGGESTIONS\n\n"
        
        report += "### 1️⃣ Keywords You Might Be Missing\n"
        report += "*(These appear frequently in similar successful CVs)*\n\n"
        for keyword in common_keywords[:10]:
            report += f"- {keyword}\n"
        
        report += f"\n### 2️⃣ Best Matching Category\n"
        if similar_cvs:
            best_category = similar_cvs[0].metadata.get('category', 'Unknown')
            report += f"Your CV is most similar to: **{best_category}**\n\n"
        
        report += "### 3️⃣ Quick Tips\n"
        report += "- ✅ Add specific project examples with measurable results\n"
        report += "- ✅ Use action verbs (developed, implemented, managed)\n"
        report += "- ✅ Quantify achievements (increased by X%, reduced by Y%)\n"
        report += "- ✅ Include relevant certifications and technical skills\n"
        
        return report
        
    except Exception as e:
        return f"❌ Error analyzing CV: {str(e)}"


# Gradio UI with custom CSS
custom_css = """
.gradio-container {
    max-width: 1200px !important;
}
.output-markdown {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}
"""

with gr.Blocks(title="AI Career Coach", css=custom_css, theme=gr.themes.Soft()) as app:
    # Header
    gr.Markdown("""
    # 🧠 AI Career Coach
    ### Transform your CV and ace your interview with AI-powered insights
    Upload your CV, specify your target job, and get personalized feedback powered by RAG (Retrieval-Augmented Generation)
    """)
    
    gr.Markdown("---")
    
    # Input Section
    with gr.Row():
        with gr.Column(scale=1):
            pdf_input = gr.File(
                label="📄 Upload Your CV", 
                file_types=[".pdf"],
                file_count="single"
            )
            job_input = gr.Textbox(
                label="🎯 Target Job Title",
                placeholder="e.g., Software Engineer, Data Scientist, Product Manager...",
                lines=1
            )
            submit_btn = gr.Button("🚀 Analyze My CV", variant="primary", size="lg")
        
        with gr.Column(scale=1):
            gr.Markdown("""
            ### 📝 What You'll Get:
            - ✨ **Cleaned CV bullets** - Professional, concise format
            - 💡 **Improvement tips** - Based on 1000+ successful CVs
            - 🎤 **Interview questions** - Tailored to your target role
            - 📊 **Skills analysis** - What you're missing vs. top candidates
            """)
    
    gr.Markdown("---")
    
    # Output Section - Cleaned CV
    with gr.Column():
        gr.Markdown("## ✨ Your Cleaned CV")
        output_text = gr.Textbox(
            label="Cleaned Bullet Points",
            lines=15,
            interactive=False,
            show_label=False
        )
        download_btn = gr.File(
            label="⬇️ Download",
            interactive=False
        )
    
    gr.Markdown("---")
    
    # Output Section - Improvements and Questions in Tabs
    with gr.Tabs():
        with gr.Tab("💡 CV Improvements"):
            improvement_output = gr.Markdown(
                value="*Upload your CV and click 'Analyze My CV' to see personalized improvement suggestions...*",
                elem_classes="output-markdown"
            )
        
        with gr.Tab("🎤 Interview Prep"):
            interview_output = gr.Markdown(
                value="*Upload your CV and click 'Analyze My CV' to get interview questions and preparation tips...*",
                elem_classes="output-markdown"
            )
    
    # Footer
    gr.Markdown("""
    ---
    <center>
    <small>Powered by RAG, Ollama, and ChromaDB | Analyzing 1000+ CVs and 2000+ job descriptions</small>
    </center>
    """)

    # Button logic
    submit_btn.click(
        process_cv,
        inputs=[pdf_input, job_input],
        outputs=[output_text, download_btn, improvement_output, interview_output]
    )


if __name__ == "__main__":
    # Launch Gradio (disable API docs to avoid Gradio bug)
    app.launch(
        server_name=DEFAULT_SERVER_NAME,
        server_port=DEFAULT_PORT,
        show_api=False
    )
