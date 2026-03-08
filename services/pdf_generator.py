import os
import subprocess
import tempfile
import shutil
from jinja2 import Environment, FileSystemLoader


def _escape_latex(text):
    """Escape special LaTeX characters in text."""
    if not isinstance(text, str):
        return text
    chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for char, replacement in chars.items():
        text = text.replace(char, replacement)
    return text


def _escape_data(data):
    """Recursively escape all string values in a nested dict/list."""
    if isinstance(data, str):
        return _escape_latex(data)
    if isinstance(data, list):
        return [_escape_data(item) for item in data]
    if isinstance(data, dict):
        return {k: _escape_data(v) for k, v in data.items()}
    return data


def generate_pdf(optimized_data, output_dir="outputs"):
    """Generate a PDF resume from structured data using LaTeX template.

    Args:
        optimized_data: dict with resume sections (name, experience, skills, etc.)
        output_dir: directory to save the generated PDF

    Returns:
        Path to the generated PDF file.
    """
    os.makedirs(output_dir, exist_ok=True)

    template_dir = os.path.join(os.path.dirname(__file__), "..", "template")
    template_dir = os.path.abspath(template_dir)

    # Jinja2 env with LaTeX-friendly delimiters
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

    template = env.get_template("resume_template.tex")

    # Escape special characters in all data
    escaped_data = _escape_data(optimized_data)

    rendered_tex = template.render(**escaped_data)

    # Compile in a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        with open(tex_path, "w") as f:
            f.write(rendered_tex)

        # Run tectonic (handles multiple passes automatically)
        result = subprocess.run(
            ["tectonic", "resume.tex"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=60,
        )

        pdf_src = os.path.join(tmpdir, "resume.pdf")
        if not os.path.exists(pdf_src):
            raise RuntimeError(
                f"tectonic failed to generate PDF.\n"
                f"STDOUT: {result.stdout[-1000:]}\n"
                f"STDERR: {result.stderr[-500:]}"
            )

        pdf_dest = os.path.join(output_dir, "optimized_resume.pdf")
        shutil.copy2(pdf_src, pdf_dest)

    return os.path.abspath(pdf_dest)
