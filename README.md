# AI Resume Optimizer

An AI-powered platform that tailors your resume and generates cover letters for any job application — powered by Google Gemini.

Upload your resume, paste a job description (or URL), and get an ATS-optimized resume + cover letter in seconds.

---

## Features

### ATS Resume Optimization
AI rewrites your resume to naturally incorporate keywords from the job description. No fake experiences — only truthful rephrasing with strong action verbs and quantified achievements.

### Cover Letter Generation
Auto-generates a tailored, professional cover letter alongside the resume. Refine it via AI chat before downloading.

### Auto JD Scraping from URL
Paste a job URL (LinkedIn, Indeed, company career pages) instead of manually copying the JD. The system scrapes and cleans the content automatically.

### Keyword Gap Analysis
Visual breakdown of ATS keywords:
- **Green** — Already in your resume
- **Blue** — Newly added by AI
- **Red** — Still missing (with actionable tips to fix)

Includes an ATS match score (percentage) that updates live as you refine.

### Seniority Auto-Detection
AI reads the JD and detects the role level (Entry Level / Graduate / Experienced), then adjusts the resume tone accordingly.

### Batch Processing
Upload a CSV of 50 job URLs → get 50 tailored resumes + 50 cover letters, organized in company-named folders. One ZIP download.

### AI Chat Refinement
After optimization, refine both resume and cover letter through natural language chat:
- *"make the summary shorter"*
- *"add Kubernetes to skills"*
- *"make the cover letter more enthusiastic"*

---

## Workflow

### Single Mode

```
  Upload Resume (PDF) + Paste JD / Enter Job URL
                      │
                      ▼
            ┌─────────────────────┐
            │  Scrape & Clean JD  │  (if URL provided)
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │  Extract ATS        │
            │  Keywords from JD   │
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │  Optimize Resume    │
            │  + Detect Seniority │  (Gemini AI)
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │  Generate Cover     │
            │  Letter             │  (Gemini AI)
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │  REVIEW STAGE       │
            │                     │
            │  • ATS Score (87%)  │
            │  • Keyword Analysis │
            │    ✅ Already present│
            │    ➕ Newly added    │
            │    ⚠️ Still missing  │
            │  • Resume Preview   │
            │  • Cover Letter     │
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │  AI CHAT REFINEMENT │
            │                     │
            │  Left: Live Preview │
            │  Right: Chat Panel  │
            │                     │
            │  Edit resume or     │
            │  cover letter via   │
            │  natural language   │
            │                     │
            │  ATS score updates  │
            │  in real-time       │
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │  DOWNLOAD           │
            │  • Resume PDF       │
            │  • Cover Letter PDF │
            └─────────────────────┘
```

### Batch Mode

```
  Upload Resume (PDF) + Upload CSV (job_url, company_name)
                      │
                      ▼
            For each job URL:
              ├── Scrape JD from URL
              ├── Extract ATS keywords
              ├── Optimize resume + detect seniority
              ├── Generate cover letter
              ├── Generate PDFs
              └── Save to outputs/batch/CompanyName/
                      │
                      ▼
            Download all_applications.zip
              └── CompanyName/
                    ├── CompanyName_Resume.pdf
                    ├── CompanyName_CoverLetter.pdf
                    ├── resume.json
                    ├── cover_letter.json
                    └── metadata.json
```

---

## Project Structure

```
Make-Hiring-Easy/
├── app.py                          # Main Streamlit app (UI + workflow)
├── requirements.txt                # Python dependencies
├── .env                            # API keys (not committed)
├── .gitignore
│
├── services/
│   ├── resume_parser.py            # PDF text extraction (pdfplumber)
│   ├── keyword_extractor.py        # JD keyword extraction (Gemini AI)
│   ├── resume_optimizer.py         # Resume optimization + seniority detection (Gemini)
│   ├── keyword_matcher.py          # Before/after keyword comparison
│   ├── cover_letter_generator.py   # Cover letter generation + refinement (Gemini)
│   ├── jd_scraper.py               # URL scraping (requests + BeautifulSoup + Gemini)
│   ├── pdf_generator.py            # Resume PDF generation (LaTeX + Tectonic)
│   └── batch_processor.py          # Batch processing pipeline
│
├── template/
│   ├── resume_template.tex         # LaTeX resume template (Jinja2)
│   └── cover_letter_template.tex   # LaTeX cover letter template (Jinja2)
│
├── uploads/                        # User-uploaded PDFs (gitignored)
└── outputs/                        # Generated files (gitignored)
```

---

## Setup

### Prerequisites

- Python 3.10+
- [Tectonic](https://tectonic-typesetting.github.io/) (for PDF generation)
- Google Gemini API key

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/Make-Hiring-Easy.git
cd Make-Hiring-Easy

# Create virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Install Tectonic (macOS)
brew install tectonic

# Install Tectonic (Linux)
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh

# Add your API key
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## CSV Format for Batch Mode

```csv
job_url,company_name
https://linkedin.com/jobs/view/123456,Google
https://careers.microsoft.com/job/789,Microsoft
https://boards.greenhouse.io/stripe/jobs/456,Stripe
```

`company_name` is optional — the system auto-detects it from the page.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| AI / LLM | Google Gemini 2.5 Flash |
| PDF Parsing | pdfplumber |
| PDF Generation | LaTeX + Jinja2 + Tectonic |
| Web Scraping | requests + BeautifulSoup |
| Templating | Jinja2 (custom delimiters for LaTeX) |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Google Gemini API key from [AI Studio](https://aistudio.google.com/apikey) |

---

## License

MIT
