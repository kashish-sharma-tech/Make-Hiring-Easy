import os
import json
import subprocess
import tempfile
import shutil
from jinja2 import Environment, FileSystemLoader
from services.gemini_client import get_client, parse_json_response
from services.pdf_generator import _ensure_tectonic


def generate_cover_letter(optimized_data, job_description, company_name=""):
    """Generate a tailored cover letter using the optimized resume and job description."""

    prompt = f"""You are an expert cover letter writer. Write a professional, tailored cover letter based on the candidate's resume and the job description.

RULES:
1. Address it to "Hiring Manager" unless a specific name is found in the JD.
2. Keep it to 3-4 paragraphs: opening, body (1-2 paragraphs highlighting relevant experience), and closing.
3. Reference specific skills and achievements from the resume that match the JD.
4. Sound enthusiastic but professional — not generic or robotic.
5. Do NOT copy-paste resume bullets. Weave them into a narrative.
6. Keep it under 350 words.

CANDIDATE RESUME:
{json.dumps(optimized_data, indent=2)}

JOB DESCRIPTION:
{job_description}

{f"COMPANY NAME: {company_name}" if company_name else ""}

Return ONLY valid JSON with this structure (no markdown, no explanation):
{{
    "recipient": "Hiring Manager or specific name",
    "company": "{company_name or 'the company'}",
    "opening": "First paragraph — why you're writing and what role",
    "body": "Middle paragraph(s) — your relevant experience and achievements tied to the JD",
    "closing": "Final paragraph — enthusiasm, call to action, availability",
    "candidate_name": "{optimized_data.get('name', 'Candidate')}"
}}
"""

    response = get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return parse_json_response(response.text)


def refine_cover_letter(cover_letter_data, user_instruction):
    """Refine the cover letter based on user's chat instruction."""

    prompt = f"""You are an expert cover letter editor. The user has a cover letter (as JSON) and wants to make a specific change.

Apply the user's instruction and return the FULL updated JSON.

RULES:
1. Only modify what the user asks for. Keep everything else exactly the same.
2. Maintain the same JSON structure.
3. Keep it professional and compelling.

CURRENT COVER LETTER JSON:
{json.dumps(cover_letter_data, indent=2)}

USER INSTRUCTION:
{user_instruction}

Return ONLY the complete updated JSON (no markdown, no explanation). Same structure as input."""

    response = get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return parse_json_response(response.text)


def _escape_latex(text):
    """Escape special LaTeX characters."""
    if not isinstance(text, str):
        return text
    chars = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
        '_': r'\_', '{': r'\{', '}': r'\}',
        '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
    }
    for char, replacement in chars.items():
        text = text.replace(char, replacement)
    return text


def generate_cover_letter_pdf(cover_letter_data, output_dir="outputs"):
    """Generate a PDF cover letter from structured data."""
    os.makedirs(output_dir, exist_ok=True)

    template_dir = os.path.join(os.path.dirname(__file__), "..", "template")
    template_dir = os.path.abspath(template_dir)

    env = Environment(
        loader=FileSystemLoader(template_dir),
        block_start_string=r'\BLOCK{',
        block_end_string='}',
        variable_start_string=r'\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )

    template = env.get_template("cover_letter_template.tex")

    # Escape all text fields
    escaped = {k: _escape_latex(v) if isinstance(v, str) else v
               for k, v in cover_letter_data.items()}

    rendered_tex = template.render(**escaped)

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "cover_letter.tex")
        with open(tex_path, "w") as f:
            f.write(rendered_tex)

        tectonic_bin = _ensure_tectonic()
        result = subprocess.run(
            [tectonic_bin, "cover_letter.tex"],
            cwd=tmpdir, capture_output=True, text=True, timeout=60,
        )

        pdf_src = os.path.join(tmpdir, "cover_letter.pdf")
        if not os.path.exists(pdf_src):
            raise RuntimeError(
                f"tectonic failed.\nSTDOUT: {result.stdout[-1000:]}\nSTDERR: {result.stderr[-500:]}"
            )

        pdf_dest = os.path.join(output_dir, "cover_letter.pdf")
        shutil.copy2(pdf_src, pdf_dest)

    return os.path.abspath(pdf_dest)
