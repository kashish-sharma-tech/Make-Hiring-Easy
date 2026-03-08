import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

try:
    import streamlit as st
    api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
except Exception:
    api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)


def extract_jd_keywords(job_description):
    """Extract important keywords and phrases from a job description."""

    prompt = f"""You are an expert ATS (Applicant Tracking System) analyst.

Extract all important keywords and phrases from this job description that a resume should contain to pass ATS screening.

Include:
- Technical skills (languages, frameworks, tools)
- Soft skills mentioned explicitly
- Certifications or qualifications
- Industry-specific terms
- Action verbs used in requirements

Job Description:
{job_description}

Return ONLY a valid JSON array of strings. No explanation, no markdown.
Example: ["Python", "AWS", "CI/CD", "team leadership", "agile methodology"]
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0].strip()

    return json.loads(text)
