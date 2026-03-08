import os
import subprocess
import tempfile
import shutil
import platform
import stat
from jinja2 import Environment, FileSystemLoader


def _ensure_tectonic():
    """Ensure tectonic is available. Auto-install on Linux (Streamlit Cloud) if missing."""
    # Check if already available
    if shutil.which("tectonic"):
        return "tectonic"

    # Check local install
    local_bin = os.path.expanduser("~/.local/bin/tectonic")
    if os.path.exists(local_bin):
        return local_bin

    # Auto-install on Linux (Streamlit Cloud)
    if platform.system() == "Linux":
        os.makedirs(os.path.expanduser("~/.local/bin"), exist_ok=True)
        try:
            # Install required shared libraries if missing
            subprocess.run(
                ["apt-get", "install", "-y", "-qq",
                 "libgraphite2-3", "libharfbuzz0b", "libfontconfig1", "libfreetype6"],
                capture_output=True, timeout=60,
            )
        except Exception:
            pass  # packages.txt should handle this, but try anyway

        try:
            subprocess.run(
                ["curl", "-fsSL",
                 "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.15.0/tectonic-0.15.0-x86_64-unknown-linux-gnu.tar.gz",
                 "-o", "/tmp/tectonic.tar.gz"],
                check=True, timeout=60,
            )
            subprocess.run(
                ["tar", "xzf", "/tmp/tectonic.tar.gz", "-C",
                 os.path.expanduser("~/.local/bin")],
                check=True, timeout=30,
            )
            os.chmod(local_bin, os.stat(local_bin).st_mode | stat.S_IEXEC)
            return local_bin
        except Exception as e:
            raise RuntimeError(
                f"Tectonic not found and auto-install failed: {e}\n"
                "Install manually: https://tectonic-typesetting.github.io/"
            )

    raise RuntimeError(
        "Tectonic not found. Install it:\n"
        "  macOS: brew install tectonic\n"
        "  Linux: curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh"
    )


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
        tectonic_bin = _ensure_tectonic()
        result = subprocess.run(
            [tectonic_bin, "resume.tex"],
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
