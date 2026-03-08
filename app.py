import streamlit as st
import os
import json

from services.resume_parser import extract_resume_text
from services.keyword_extractor import extract_jd_keywords
from services.resume_optimizer import optimize_resume, refine_resume
from services.keyword_matcher import compare_keywords
from services.pdf_generator import generate_pdf
from services.cover_letter_generator import (
    generate_cover_letter, refine_cover_letter, generate_cover_letter_pdf,
)
from services.jd_scraper import scrape_jd_from_url
from services.jd_doc_parser import extract_jd_from_document
# from services.batch_processor import process_batch  # Batch mode disabled for now


st.set_page_config(page_title="AI Resume Optimizer", page_icon="📄", layout="wide")

# ===== CUSTOM CSS =====
st.markdown("""
<style>
    /* ── Global ── */
    .block-container { padding-top: 1rem; }

    /* ── Header ── */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.2rem 2rem 1.8rem;
        border-radius: 16px;
        margin-bottom: 1.8rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(102,126,234,0.25);
    }
    .main-header h1 { color: white; font-size: 2.4rem; margin: 0; letter-spacing: -0.5px; }
    .main-header p  { color: rgba(255,255,255,0.9); font-size: 1.05rem; margin: 0.6rem 0 0 0; }

    /* ── Feature cards on landing ── */
    .feature-grid { display: flex; gap: 1rem; margin: 1.5rem 0; flex-wrap: wrap; }
    .feature-card {
        flex: 1; min-width: 200px;
        background: #f8f9ff; border: 1px solid #e4e7f5;
        border-radius: 12px; padding: 1.2rem; text-align: center;
        transition: transform 0.15s;
    }
    .feature-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
    .feature-icon { font-size: 2rem; margin-bottom: 0.4rem; }
    .feature-title { font-weight: 700; color: #4a4a8a; font-size: 0.95rem; }
    .feature-desc  { font-size: 0.8rem; color: #6c757d; margin-top: 0.3rem; }

    /* ── Keyword badges ── */
    .keyword-badge {
        display: inline-block; padding: 5px 12px; margin: 3px;
        border-radius: 20px; font-size: 0.82rem; font-weight: 500;
        transition: transform 0.1s;
    }
    .keyword-badge:hover { transform: scale(1.05); }
    .badge-green { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .badge-blue  { background: #cce5ff; color: #004085; border: 1px solid #b8daff; }
    .badge-red   { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .badge-skill { background: #e8eaf6; color: #3949ab; border: 1px solid #c5cae9; }

    /* ── ATS Score Ring ── */
    .ats-score-container { text-align: center; margin: 1rem 0; }
    .ats-score-ring {
        width: 120px; height: 120px; border-radius: 50%;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 2.2rem; font-weight: 800; color: white;
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    .ats-excellent { background: linear-gradient(135deg, #28a745, #20c997); }
    .ats-good      { background: linear-gradient(135deg, #17a2b8, #667eea); }
    .ats-fair      { background: linear-gradient(135deg, #ffc107, #fd7e14); }
    .ats-poor      { background: linear-gradient(135deg, #dc3545, #e83e8c); }
    .ats-label { font-size: 0.85rem; color: #6c757d; margin-top: 0.5rem; font-weight: 600; }

    /* ── Preview card ── */
    .preview-card {
        background: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px;
        padding: 1.5rem; margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }
    .preview-card h3 {
        color: #4a4a8a; border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem; margin-top: 0; font-size: 1.1rem;
    }

    /* ── Stage progress ── */
    .stage-bar { display: flex; align-items: center; gap: 0; margin-bottom: 1.5rem; }
    .stage-step {
        display: flex; align-items: center; gap: 8px;
        padding: 8px 20px; border-radius: 25px;
        font-weight: 600; font-size: 0.85rem;
    }
    .stage-connector { width: 40px; height: 2px; background: #e0e0e0; }
    .stage-connector-done { background: #28a745; }
    .stage-active   { background: #667eea; color: white; box-shadow: 0 2px 8px rgba(102,126,234,0.3); }
    .stage-done     { background: #d4edda; color: #155724; }
    .stage-inactive { background: #f0f0f0; color: #aaa; }

    /* ── Seniority ── */
    .seniority-badge {
        display: inline-block; padding: 6px 16px; border-radius: 20px;
        font-weight: 600; font-size: 0.85rem; margin: 0.3rem 0;
    }
    .seniority-entry       { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
    .seniority-graduate    { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    .seniority-experienced { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }

    /* ── Stat cards ── */
    .stat-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px; padding: 1.2rem; text-align: center;
        border: 1px solid #e0e4ef;
    }
    .stat-card .stat-number { font-size: 2rem; font-weight: 800; color: #4a4a8a; }
    .stat-card .stat-label  { font-size: 0.82rem; color: #6c757d; margin-top: 0.2rem; font-weight: 500; }

    /* ── Keyword gap section ── */
    .keyword-gap-section {
        background: #fff8f8; border: 1px solid #f5c6cb; border-radius: 12px;
        padding: 1.2rem; margin: 1rem 0;
    }
    .keyword-gap-section h4 { color: #721c24; margin: 0 0 0.8rem 0; font-size: 1rem; }
    .gap-item {
        display: flex; align-items: center; gap: 8px;
        padding: 6px 0; border-bottom: 1px solid #fce4e4;
    }
    .gap-item:last-child { border-bottom: none; }
    .gap-icon { color: #dc3545; font-size: 1.1rem; }
    .gap-keyword { font-weight: 600; color: #721c24; }
    .gap-tip { font-size: 0.78rem; color: #999; font-style: italic; }

    /* ── Cover letter preview ── */
    .cl-preview {
        background: #fffdf7; border: 1px solid #f0e6c8; border-radius: 12px;
        padding: 2rem; margin: 1rem 0; font-family: Georgia, serif;
        line-height: 1.7; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .cl-preview .cl-date { text-align: right; color: #888; font-size: 0.9rem; margin-bottom: 1.5rem; }
    .cl-preview .cl-greeting { font-weight: 600; margin-bottom: 1rem; }
    .cl-preview .cl-body p { margin: 0.8rem 0; text-align: justify; }
    .cl-preview .cl-sign { margin-top: 2rem; }

    /* ── Batch ── */
    .batch-result {
        border: 1px solid #e0e0e0; border-radius: 10px;
        padding: 0.8rem 1.2rem; margin: 0.5rem 0;
        transition: transform 0.1s;
    }
    .batch-result:hover { transform: translateX(3px); }
    .batch-success { border-left: 4px solid #28a745; background: #f8fff8; }
    .batch-fail    { border-left: 4px solid #dc3545; background: #fff8f8; }

    /* ── Upload area ── */
    .upload-section {
        background: #f8f9ff; border: 2px dashed #c5cae9; border-radius: 12px;
        padding: 1.5rem; margin-bottom: 1rem; text-align: center;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] { background: #f8f9ff; }
    [data-testid="stSidebar"] .stRadio > label { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown("""
<div class="main-header">
    <h1>📄 AI Resume Optimizer</h1>
    <p>Upload your resume & paste the job description — get an ATS-optimized resume + cover letter in seconds</p>
</div>
""", unsafe_allow_html=True)

# ===== SESSION STATE INIT =====
defaults = {
    "optimized_data": None, "comparison": None, "resume_text": None,
    "stage": "input", "chat_history": [], "pdf_generated": None,
    "pdf_path": None, "jd_keywords": None, "cover_letter": None,
    "cover_letter_pdf_path": None, "job_description": None,
    "company_name": None, "active_tab": "resume",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# =============================================
# HELPER FUNCTIONS
# =============================================

def calc_ats_score(comparison):
    """Calculate ATS match score as a percentage."""
    total = (len(comparison["already_present"])
             + len(comparison["added"])
             + len(comparison["not_added"]))
    if total == 0:
        return 100
    matched = len(comparison["already_present"]) + len(comparison["added"])
    return round((matched / total) * 100)


def render_ats_score(comparison):
    """Render the circular ATS match score."""
    score = calc_ats_score(comparison)
    if score >= 85:
        css, label = "ats-excellent", "Excellent Match"
    elif score >= 70:
        css, label = "ats-good", "Good Match"
    elif score >= 50:
        css, label = "ats-fair", "Fair Match"
    else:
        css, label = "ats-poor", "Needs Work"

    st.markdown(f"""
    <div class="ats-score-container">
        <div class="ats-score-ring {css}">{score}%</div>
        <div class="ats-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_stage_bar(current):
    stages = [
        ("input", "1", "Upload"),
        ("review", "2", "Review"),
        ("chat", "3", "Refine"),
    ]
    html_parts = []
    past_current = False
    for i, (sid, num, label) in enumerate(stages):
        if sid == current:
            css = "stage-active"
            icon = "✏️"
            past_current = True
        elif not past_current:
            css = "stage-done"
            icon = "✅"
        else:
            css = "stage-inactive"
            icon = ""
        html_parts.append(f'<div class="stage-step {css}">{icon} {label}</div>')
        if i < len(stages) - 1:
            conn_css = "stage-connector-done" if not past_current else ""
            html_parts.append(f'<div class="stage-connector {conn_css}"></div>')

    st.markdown(f'<div class="stage-bar">{"".join(html_parts)}</div>', unsafe_allow_html=True)


def render_seniority_badge(data):
    level = data.get("seniority_level", "")
    if not level:
        return
    css_class = {
        "Entry Level": "seniority-entry",
        "Graduate": "seniority-graduate",
        "Experienced": "seniority-experienced",
    }.get(level, "seniority-graduate")
    icon = {"Entry Level": "🌱", "Graduate": "🎓", "Experienced": "🚀"}.get(level, "🎯")
    st.markdown(
        f'<span class="seniority-badge {css_class}">{icon} {level}</span>',
        unsafe_allow_html=True
    )


def render_keyword_analysis(comparison):
    """Full keyword analysis with stats, badges, and gap detail."""
    score = calc_ats_score(comparison)

    # Top row: ATS score + stat cards
    col_score, col_s1, col_s2, col_s3 = st.columns([1.2, 1, 1, 1])

    with col_score:
        render_ats_score(comparison)

    with col_s1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color:#155724;">✅ {len(comparison["already_present"])}</div>
            <div class="stat-label">Already In Resume</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color:#004085;">➕ {len(comparison["added"])}</div>
            <div class="stat-label">Newly Added by AI</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color:#721c24;">⚠️ {len(comparison["not_added"])}</div>
            <div class="stat-label">Still Missing</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # Keyword badges in expandable sections
    with st.expander("✅ Keywords Already in Your Resume", expanded=False):
        if comparison["already_present"]:
            badges = "".join(
                f'<span class="keyword-badge badge-green">{kw}</span>'
                for kw in comparison["already_present"]
            )
            st.markdown(badges, unsafe_allow_html=True)
        else:
            st.caption("None found")

    with st.expander("➕ Keywords Added by AI Optimization", expanded=True):
        if comparison["added"]:
            badges = "".join(
                f'<span class="keyword-badge badge-blue">{kw}</span>'
                for kw in comparison["added"]
            )
            st.markdown(badges, unsafe_allow_html=True)
        else:
            st.caption("No new keywords were added")

    # Missing keywords with detailed gap analysis
    if comparison["not_added"]:
        with st.expander(f"⚠️ Missing Keywords — {len(comparison['not_added'])} gaps to address", expanded=True):
            st.markdown("""
            <div class="keyword-gap-section">
                <h4>🔴 These keywords from the JD are NOT in your resume yet</h4>
            """, unsafe_allow_html=True)

            gap_html = ""
            for kw in comparison["not_added"]:
                gap_html += f"""
                <div class="gap-item">
                    <span class="gap-icon">✗</span>
                    <span class="gap-keyword">{kw}</span>
                    <span class="gap-tip">→ Try adding via chat: "add {kw} to my skills"</span>
                </div>
                """

            st.markdown(gap_html + "</div>", unsafe_allow_html=True)
            st.info("💡 **Tip:** Use the AI chat to add these missing keywords naturally — e.g. *\"incorporate Docker into my experience\"*")


def render_preview(data):
    """Render a polished resume preview."""
    name = data.get("name", "")
    contact_parts = []
    for k in ("email", "phone", "location"):
        v = data.get(k)
        if v:
            contact_parts.append(v)
    contact_line = " &nbsp;|&nbsp; ".join(contact_parts)

    # Links
    links = []
    if data.get("linkedin"):
        links.append(f'<a href="{data["linkedin"]}" style="color:#667eea;">LinkedIn</a>')
    if data.get("github"):
        links.append(f'<a href="{data["github"]}" style="color:#667eea;">GitHub</a>')
    links_html = " &nbsp;|&nbsp; ".join(links) if links else ""

    st.markdown(f"""
    <div class="preview-card" style="text-align:center; border-top: 3px solid #667eea;">
        <h2 style="margin:0; color:#333; font-size:1.6rem;">{name}</h2>
        <p style="color:#666; margin:0.3rem 0 0 0; font-size:0.92rem;">{contact_line}</p>
        {"<p style='margin:0.3rem 0 0 0;'>" + links_html + "</p>" if links_html else ""}
    </div>
    """, unsafe_allow_html=True)

    # Summary
    if data.get("summary"):
        st.markdown(f"""
        <div class="preview-card">
            <h3>📝 Professional Summary</h3>
            <p style="line-height:1.6; color:#444;">{data["summary"]}</p>
        </div>
        """, unsafe_allow_html=True)

    # Experience
    if data.get("experience"):
        st.markdown('<div class="preview-card"><h3>💼 Experience</h3>', unsafe_allow_html=True)
        for i, job in enumerate(data["experience"]):
            st.markdown(
                f"**{job['title']}** at *{job['company']}* &nbsp; `{job['duration']}`"
            )
            for bullet in job.get("bullets", []):
                st.markdown(f"- {bullet}")
            if i < len(data["experience"]) - 1:
                st.divider()
        st.markdown('</div>', unsafe_allow_html=True)

    # Projects
    if data.get("projects"):
        st.markdown('<div class="preview-card"><h3>🛠️ Projects</h3>', unsafe_allow_html=True)
        for i, proj in enumerate(data["projects"]):
            tech = f" | *{proj['tech']}*" if proj.get("tech") else ""
            dur = f" &nbsp; `{proj['duration']}`" if proj.get("duration") else ""
            st.markdown(f"**{proj['name']}**{tech}{dur}")
            for bullet in proj.get("bullets", []):
                st.markdown(f"- {bullet}")
            if i < len(data["projects"]) - 1:
                st.divider()
        st.markdown('</div>', unsafe_allow_html=True)

    # Skills
    if data.get("skills"):
        skills_html = "".join(
            f'<span class="keyword-badge badge-skill">{s}</span>'
            for s in data["skills"]
        )
        st.markdown(f"""
        <div class="preview-card">
            <h3>🧠 Skills</h3>
            {skills_html}
        </div>
        """, unsafe_allow_html=True)

    # Education
    if data.get("education"):
        st.markdown('<div class="preview-card"><h3>🎓 Education</h3>', unsafe_allow_html=True)
        for edu in data["education"]:
            st.markdown(f"**{edu['degree']}** — {edu['institution']} &nbsp; `{edu['year']}`")
        st.markdown('</div>', unsafe_allow_html=True)

    # Certifications
    if data.get("certifications"):
        st.markdown('<div class="preview-card"><h3>🏅 Certifications</h3>', unsafe_allow_html=True)
        for cert in data["certifications"]:
            st.markdown(f"- {cert}")
        st.markdown('</div>', unsafe_allow_html=True)


def render_cover_letter_preview(cl):
    if not cl:
        st.info("No cover letter generated yet.")
        return
    st.markdown(f"""
    <div class="cl-preview">
        <div class="cl-date">Today's Date</div>
        <div class="cl-greeting">Dear {cl.get('recipient', 'Hiring Manager')},</div>
        <div class="cl-body">
            <p>{cl.get('opening', '')}</p>
            <p>{cl.get('body', '')}</p>
            <p>{cl.get('closing', '')}</p>
        </div>
        <div class="cl-sign">
            <p>Sincerely,</p>
            <p><strong>{cl.get('candidate_name', '')}</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ===========================================================================
# MODE SELECTION
# ===========================================================================
st.sidebar.markdown("### ⚙️ Mode")
# Batch mode disabled for now — only single application mode
mode = "🎯 Single Application"
# mode = st.sidebar.radio(
#     "Choose mode",
#     ["🎯 Single Application", "📦 Batch Processing"],
#     index=0,
#     label_visibility="collapsed",
# )

st.sidebar.markdown("---")
st.sidebar.markdown("""
**How it works:**
1. Upload your resume PDF
2. Paste JD, enter URL, or upload JD doc
3. AI optimizes for ATS + generates cover letter
4. Review ATS score + keyword gaps
5. Refine with chat → download PDFs
""")


# ===========================================================================
# SINGLE APPLICATION MODE
# ===========================================================================
if mode == "🎯 Single Application":

    # ───── STAGE 1: INPUT ─────
    if st.session_state.stage == "input":
        render_stage_bar("input")

        # Feature cards
        st.markdown("""
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">ATS Optimization</div>
                <div class="feature-desc">AI rewrites your resume with target keywords</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">✉️</div>
                <div class="feature-title">Cover Letter</div>
                <div class="feature-desc">Auto-generated, tailored to the role</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Keyword Gap Analysis</div>
                <div class="feature-desc">See exactly which keywords are missing</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎓</div>
                <div class="feature-title">Seniority Detection</div>
                <div class="feature-desc">Auto-adjusts tone for your level</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("##### 📎 Your Resume")
            resume_file = st.file_uploader(
                "Upload Resume PDF",
                type=["pdf"],
                help="Upload your current resume in PDF format",
            )

        with col_right:
            st.markdown("##### 📋 Job Description")
            jd_input_method = st.radio(
                "How do you want to provide the JD?",
                ["✍️ Paste Text", "🔗 Enter URL", "📄 Upload Document"],
                horizontal=True,
                label_visibility="collapsed",
            )

            job_description = None
            job_url = None
            jd_file = None

            if jd_input_method == "✍️ Paste Text":
                job_description = st.text_area(
                    "Paste Job Description",
                    height=220,
                    placeholder="Paste the full job description here...",
                )
            elif jd_input_method == "🔗 Enter URL":
                job_url = st.text_input(
                    "Job Posting URL",
                    placeholder="https://linkedin.com/jobs/view/123456 or any career page",
                )
                st.caption("Works with LinkedIn, Indeed, company career pages, and most job boards")
            else:
                jd_file = st.file_uploader(
                    "Upload JD Document",
                    type=["pdf", "docx", "doc", "txt"],
                    help="Upload a job description in PDF, DOCX, or TXT format",
                    key="jd_doc",
                )

        st.markdown("")
        if st.button("🚀 Optimize Resume + Generate Cover Letter", type="primary", use_container_width=True):
            if resume_file is None:
                st.error("Please upload a resume.")
                st.stop()
            has_jd = job_description and job_description.strip()
            has_url = job_url and job_url.strip()
            has_doc = jd_file is not None
            if not has_jd and not has_url and not has_doc:
                st.error("Please paste a job description, enter a URL, or upload a document.")
                st.stop()

            os.makedirs("uploads", exist_ok=True)
            os.makedirs("outputs", exist_ok=True)

            resume_path = os.path.join("uploads", resume_file.name)
            with open(resume_path, "wb") as f:
                f.write(resume_file.read())

            progress = st.progress(0, text="Starting...")

            # Step 1: Extract resume
            progress.progress(10, text="📄 Extracting resume text...")
            st.session_state.resume_text = extract_resume_text(resume_path)

            # Step 2: Extract JD from document or scrape URL
            company_name = ""
            if jd_file is not None:
                progress.progress(20, text="📄 Extracting JD from uploaded document...")
                try:
                    jd_doc_path = os.path.join("uploads", jd_file.name)
                    with open(jd_doc_path, "wb") as f:
                        f.write(jd_file.read())
                    job_description = extract_jd_from_document(jd_doc_path)
                except Exception as e:
                    st.error(f"Failed to extract JD from document: {e}")
                    st.stop()

            elif job_url and job_url.strip():
                progress.progress(20, text="🌐 Scraping job description from URL...")
                try:
                    scraped = scrape_jd_from_url(job_url.strip())
                    job_description = scraped["job_description"]
                    company_name = scraped.get("company_name", "")
                except Exception as e:
                    st.error(f"Failed to scrape URL: {e}")
                    st.stop()

            st.session_state.job_description = job_description
            st.session_state.company_name = company_name

            # Step 3: Keywords
            progress.progress(35, text="🔍 Extracting ATS keywords from job description...")
            jd_keywords = extract_jd_keywords(job_description)
            st.session_state.jd_keywords = jd_keywords

            # Step 4: Optimize
            progress.progress(55, text="🤖 AI is optimizing your resume (with seniority detection)...")
            st.session_state.optimized_data = optimize_resume(
                st.session_state.resume_text, job_description, jd_keywords
            )

            # Step 5: Cover letter
            progress.progress(80, text="✉️ Generating tailored cover letter...")
            st.session_state.cover_letter = generate_cover_letter(
                st.session_state.optimized_data, job_description, company_name
            )

            # Save outputs
            with open("outputs/optimized_resume.json", "w") as f:
                json.dump(st.session_state.optimized_data, f, indent=2)
            with open("outputs/cover_letter.json", "w") as f:
                json.dump(st.session_state.cover_letter, f, indent=2)

            st.session_state.comparison = compare_keywords(
                jd_keywords, st.session_state.resume_text, st.session_state.optimized_data
            )

            progress.progress(100, text="✅ Done!")

            st.session_state.stage = "review"
            st.session_state.chat_history = []
            st.session_state.pdf_generated = None
            st.session_state.pdf_path = None
            st.session_state.cover_letter_pdf_path = None
            st.rerun()


    # ───── STAGE 2: REVIEW ─────
    if st.session_state.stage == "review":
        render_stage_bar("review")

        # Top bar: success + seniority
        col_msg, col_sen = st.columns([3, 1])
        with col_msg:
            score = calc_ats_score(st.session_state.comparison)
            if score >= 85:
                st.success(f"🎉 Excellent! Your resume scores **{score}%** ATS match. Cover letter is ready too!")
            elif score >= 70:
                st.success(f"👍 Good match — **{score}%** ATS score. Review the gaps below to improve further.")
            else:
                st.warning(f"⚠️ Your ATS match is **{score}%**. Check the missing keywords below.")
        with col_sen:
            render_seniority_badge(st.session_state.optimized_data)

        # Keyword Analysis
        st.markdown("### 🔍 ATS Keyword Analysis")
        render_keyword_analysis(st.session_state.comparison)

        # Resume + Cover Letter tabs
        st.markdown("")
        st.markdown("### 📄 Preview")
        tab_resume, tab_cover = st.tabs(["📋 Optimized Resume", "✉️ Cover Letter"])

        with tab_resume:
            render_preview(st.session_state.optimized_data)

        with tab_cover:
            render_cover_letter_preview(st.session_state.cover_letter)

        # Action buttons
        st.markdown("")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ Accept & Refine with AI Chat", type="primary", use_container_width=True):
                st.session_state.stage = "chat"
                st.rerun()
        with col_b:
            if st.button("🔄 Start Over", use_container_width=True):
                for key, val in defaults.items():
                    st.session_state[key] = val
                st.rerun()


    # ───── STAGE 3: CHAT REFINEMENT ─────
    if st.session_state.stage == "chat":
        render_stage_bar("chat")

        col_preview, col_chat = st.columns([3, 2])

        with col_preview:
            # Compact top info
            info_col1, info_col2 = st.columns([1, 1])
            with info_col1:
                render_ats_score(st.session_state.comparison)
            with info_col2:
                render_seniority_badge(st.session_state.optimized_data)
                if st.session_state.comparison["not_added"]:
                    missing = st.session_state.comparison["not_added"]
                    st.markdown(f"**{len(missing)} keyword{'s' if len(missing) != 1 else ''} still missing:**")
                    badges = "".join(
                        f'<span class="keyword-badge badge-red">{kw}</span>'
                        for kw in missing[:8]
                    )
                    more = f' <span style="color:#999;">+{len(missing)-8} more</span>' if len(missing) > 8 else ""
                    st.markdown(badges + more, unsafe_allow_html=True)

            st.markdown("")
            preview_tab = st.radio(
                "Preview",
                ["📋 Resume", "✉️ Cover Letter"],
                horizontal=True,
                label_visibility="collapsed",
            )
            if preview_tab == "📋 Resume":
                render_preview(st.session_state.optimized_data)
            else:
                render_cover_letter_preview(st.session_state.cover_letter)

        with col_chat:
            st.markdown("### 💬 AI Chat")
            st.caption(
                "Refine your **resume** or **cover letter** — e.g.\n\n"
                "- *\"make the summary shorter\"*\n"
                "- *\"add Docker to skills\"*\n"
                "- *\"make the cover letter more enthusiastic\"*\n"
                "- *\"incorporate leadership keywords\"*"
            )

            chat_container = st.container(height=400)
            with chat_container:
                if not st.session_state.chat_history:
                    st.markdown(
                        '<p style="color:#bbb; text-align:center; margin-top:3rem; font-size:0.95rem;">'
                        '💬 No messages yet — type below to start refining!</p>',
                        unsafe_allow_html=True,
                    )
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

            user_input = st.chat_input("Tell AI what to change...")

            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})

                cl_keywords = ["cover letter", "cover-letter", "coverletter", "letter"]
                is_cover_letter_edit = any(kw in user_input.lower() for kw in cl_keywords)

                try:
                    if is_cover_letter_edit and st.session_state.cover_letter:
                        updated_cl = refine_cover_letter(st.session_state.cover_letter, user_input)
                        st.session_state.cover_letter = updated_cl
                        with open("outputs/cover_letter.json", "w") as f:
                            json.dump(updated_cl, f, indent=2)
                        reply = "✅ Cover letter updated! Check the preview."
                    else:
                        updated_data = refine_resume(st.session_state.optimized_data, user_input)
                        st.session_state.optimized_data = updated_data

                        if st.session_state.jd_keywords and st.session_state.resume_text:
                            st.session_state.comparison = compare_keywords(
                                st.session_state.jd_keywords,
                                st.session_state.resume_text,
                                updated_data,
                            )

                        with open("outputs/optimized_resume.json", "w") as f:
                            json.dump(updated_data, f, indent=2)

                        new_score = calc_ats_score(st.session_state.comparison)
                        reply = f"✅ Resume updated! ATS score: **{new_score}%**. Check the preview."

                    st.session_state.pdf_generated = None
                except Exception as e:
                    reply = f"❌ Couldn't apply that change: {e}"

                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

            # Action buttons
            st.markdown("")
            if st.button("📄 Finalize & Generate PDFs", type="primary", use_container_width=True):
                with st.spinner("Generating Resume PDF..."):
                    try:
                        pdf_path = generate_pdf(st.session_state.optimized_data)
                        st.session_state.pdf_path = pdf_path
                    except Exception as e:
                        st.error(f"Resume PDF failed: {e}")

                with st.spinner("Generating Cover Letter PDF..."):
                    try:
                        cl_pdf_path = generate_cover_letter_pdf(st.session_state.cover_letter)
                        st.session_state.cover_letter_pdf_path = cl_pdf_path
                    except Exception as e:
                        st.error(f"Cover letter PDF failed: {e}")

                st.session_state.pdf_generated = True
                st.rerun()

            if st.session_state.pdf_generated:
                dl1, dl2 = st.columns(2)
                if st.session_state.pdf_path:
                    with dl1:
                        with open(st.session_state.pdf_path, "rb") as f:
                            st.download_button(
                                "⬇️ Resume PDF", f.read(),
                                "optimized_resume.pdf", "application/pdf",
                                type="primary", use_container_width=True,
                            )
                if st.session_state.cover_letter_pdf_path:
                    with dl2:
                        with open(st.session_state.cover_letter_pdf_path, "rb") as f:
                            st.download_button(
                                "⬇️ Cover Letter PDF", f.read(),
                                "cover_letter.pdf", "application/pdf",
                                type="primary", use_container_width=True,
                            )

            if st.button("🔄 Start Over", use_container_width=True):
                for key, val in defaults.items():
                    st.session_state[key] = val
                st.rerun()


# ===========================================================================
# BATCH PROCESSING MODE (disabled for now)
# ===========================================================================
# elif mode == "📦 Batch Processing":
#     # Batch processing is temporarily disabled.
#     # To re-enable: uncomment this block and the mode radio above,
#     # and uncomment the process_batch import at the top.
#     pass
