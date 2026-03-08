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


def optimize_resume(resume_text, job_description, jd_keywords):
    """Optimize resume to be ATS-friendly and return structured JSON."""

    keywords_str = ", ".join(jd_keywords)

    prompt = f"""You are an expert resume optimizer specializing in ATS (Applicant Tracking System) optimization.

Given the original resume text and a job description, rewrite and structure the resume to maximize ATS compatibility.

RULES:
1. Do NOT invent new job roles, companies, or experiences that don't exist in the original resume.
2. Rephrase existing experience bullets to naturally incorporate relevant keywords from the job description.
3. The rephrased bullets must remain truthful and clearly related to the original experience.
4. Add missing keywords to the skills section ONLY if the person plausibly has them based on their experience.
5. Write a concise professional summary tailored to the job description.
6. Use strong action verbs and quantify achievements where possible.

SENIORITY DETECTION:
Analyze the job description and determine the seniority level:
- "Entry Level" → less than 1 year experience required, junior roles, internships
- "Graduate" → 1-2 years experience required, associate roles
- "Experienced" → 3+ years experience required, senior/lead/principal roles

Adjust the resume tone accordingly:
- Entry Level: Emphasize learning ability, projects, coursework, eagerness
- Graduate: Balance academics with early professional experience
- Experienced: Lead with impact, leadership, architecture decisions, mentoring

TARGET KEYWORDS TO INCORPORATE:
{keywords_str}

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON with this exact structure (no markdown, no explanation):
{{
    "seniority_level": "Entry Level, Graduate, or Experienced",
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "phone number",
    "linkedin": "linkedin URL or empty string",
    "github": "github URL or empty string",
    "location": "city, state or empty string",
    "summary": "2-3 sentence professional summary tailored to the job",
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "duration": "Start - End",
            "bullets": [
                "Achievement/responsibility with keywords incorporated",
                "Another bullet point"
            ]
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "tech": "Technologies used",
            "duration": "time period or empty string",
            "bullets": [
                "Project description with relevant keywords"
            ]
        }}
    ],
    "skills": ["skill1", "skill2"],
    "education": [
        {{
            "degree": "Degree Name",
            "institution": "University Name",
            "year": "Year or range"
        }}
    ],
    "certifications": ["cert1", "cert2"]
}}

If a section has no data in the original resume, use an empty array [] for lists or empty string "" for text fields.
Projects section: include only if the original resume has projects. Otherwise use empty array [].
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


def refine_resume(optimized_data, user_instruction):
    """Refine the optimized resume based on user's chat instruction."""

    prompt = f"""You are an expert resume editor. The user has an optimized resume (as JSON) and wants to make a specific change.

Apply the user's instruction to the resume data and return the FULL updated JSON.

RULES:
1. Only modify what the user asks for. Keep everything else exactly the same.
2. Maintain the same JSON structure.
3. Keep it professional and ATS-friendly.

CURRENT RESUME JSON:
{json.dumps(optimized_data, indent=2)}

USER INSTRUCTION:
{user_instruction}

Return ONLY the complete updated JSON (no markdown, no explanation). Same structure as input."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0].strip()

    return json.loads(text)
