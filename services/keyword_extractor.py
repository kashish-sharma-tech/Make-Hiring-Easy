from services.gemini_client import get_client, parse_json_response


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

    response = get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return parse_json_response(response.text)
