# AI Resume Optimizer

An AI-powered platform that tailors your resume and generates cover letters for any job application — powered by Google Gemini.

Upload your resume, paste a job description (or URL or document), and get an ATS-optimized resume + cover letter in seconds.

---

## WOW Factors

| # | Feature | What Makes It Special |
|---|---------|----------------------|
| 1 | **Cover Letter Generation** | One click → tailored cover letter alongside the resume. Not a template — AI writes it from scratch using your resume + JD. Refine via chat. |
| 2 | **3 Ways to Input JD** | Paste text, enter a URL (LinkedIn/Indeed/career pages), OR upload a document (PDF/DOCX/TXT). Maximum flexibility. |
| 3 | **Batch Processing** | Upload CSV with 50 job URLs → get 50 resumes + 50 cover letters in company-organized folders. One ZIP download. |
| 4 | **ATS Score with Keyword Gap Analysis** | Circular score ring (87%) + color-coded keyword badges + missing keywords listed individually with fix suggestions. |
| 5 | **Seniority Auto-Detection** | AI detects Entry Level / Graduate / Experienced from the JD and adjusts resume tone automatically. |
| 6 | **AI Chat Refinement** | Natural language editing for both resume AND cover letter — *"add Docker to skills"*, *"make cover letter shorter"*. ATS score updates live. |
| 7 | **Robust JSON Parsing** | Auto-repairs malformed LLM responses — handles trailing commas, truncated JSON, markdown fences. Never crashes on bad AI output. |
| 8 | **Auto Tectonic Install** | PDF generation works on Streamlit Cloud without manual setup — auto-downloads the LaTeX compiler binary. |

---

## Features

### ATS Resume Optimization
AI rewrites your resume to naturally incorporate keywords from the job description. No fake experiences — only truthful rephrasing with strong action verbs and quantified achievements.

### Cover Letter Generation
Auto-generates a tailored, professional cover letter alongside the resume. Refine it via AI chat before downloading.

### 3 Ways to Provide Job Description
- **Paste Text** — Copy-paste the JD directly
- **Enter URL** — Paste a LinkedIn, Indeed, or company career page URL. AI scrapes and cleans the JD automatically.
- **Upload Document** — Upload a JD as PDF, DOCX, DOC, or TXT file. AI extracts the text from any format.

### Keyword Gap Analysis
Visual breakdown of ATS keywords:
- **Green** — Already in your resume
- **Blue** — Newly added by AI
- **Red** — Still missing (with actionable tips like *"add Docker to skills"*)

Includes an ATS match score (percentage) that updates live as you refine.

### Seniority Auto-Detection
AI reads the JD and detects the role level (Entry Level / Graduate / Experienced), then adjusts the resume tone accordingly:
- **Entry Level** — Emphasizes projects, coursework, eagerness
- **Graduate** — Balances academics with early experience
- **Experienced** — Leads with impact, leadership, architecture decisions

### Batch Processing
Upload a CSV of 50 job URLs → get 50 tailored resumes + 50 cover letters, organized in company-named folders. One ZIP download with everything inside.

### AI Chat Refinement
After optimization, refine both resume and cover letter through natural language chat:
- *"make the summary shorter"*
- *"add Kubernetes to skills"*
- *"make the cover letter more enthusiastic"*
- *"incorporate leadership keywords"*

---

## How It Works

### Single Mode

```
  Upload Resume (PDF)
        +
  Job Description via:
    ├── Paste Text
    ├── Enter URL (LinkedIn, Indeed, career pages)
    └── Upload Document (PDF, DOCX, TXT)
                      │
                      ▼
            ┌─────────────────────┐
            │  Extract JD Text    │  (scrape URL / parse doc / use paste)
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │  Extract ATS        │
            │  Keywords from JD   │  (Gemini AI)
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
            │  • Seniority Badge  │
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
│   ├── gemini_client.py            # Lazy Gemini client + robust JSON parser
│   ├── resume_parser.py            # PDF text extraction (pdfplumber)
│   ├── keyword_extractor.py        # JD keyword extraction (Gemini AI)
│   ├── resume_optimizer.py         # Resume optimization + seniority detection (Gemini)
│   ├── keyword_matcher.py          # Before/after keyword comparison
│   ├── cover_letter_generator.py   # Cover letter generation + refinement (Gemini)
│   ├── jd_scraper.py               # URL scraping (requests + BeautifulSoup + Gemini)
│   ├── jd_doc_parser.py            # Document JD extraction (PDF, DOCX, TXT)
│   ├── pdf_generator.py            # Resume PDF generation (LaTeX + Tectonic)
│   └── batch_processor.py          # Batch processing pipeline
│
├── template/
│   ├── resume_template.tex         # LaTeX resume template (Jinja2)
│   └── cover_letter_template.tex   # LaTeX cover letter template (Jinja2)
│
├── uploads/                        # User-uploaded files (gitignored)
└── outputs/                        # Generated files (gitignored)
```

---

## Setup

### Prerequisites

- Python 3.10+
- [Tectonic](https://tectonic-typesetting.github.io/) (for PDF generation — auto-installed on Streamlit Cloud)
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

## Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select repo
3. Add secret: `GOOGLE_API_KEY = "your_key"` in Advanced Settings → Secrets
4. Deploy — Tectonic auto-installs, no manual setup needed

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
| DOCX Parsing | python-docx |
| PDF Generation | LaTeX + Jinja2 + Tectonic |
| Web Scraping | requests + BeautifulSoup |
| Templating | Jinja2 (custom delimiters for LaTeX) |
| JSON Resilience | Custom parser with auto-repair |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Google Gemini API key from [AI Studio](https://aistudio.google.com/apikey) |

---

## License

MIT
