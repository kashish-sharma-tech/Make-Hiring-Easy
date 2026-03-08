import re
import requests
from bs4 import BeautifulSoup
from services.gemini_client import generate, parse_json_response

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_jd_from_url(url):
    """Scrape job description from a URL and extract clean JD text.

    Supports LinkedIn, company career pages, and general job boards.
    Uses a three-tier approach:
      1. HTTP request with BeautifulSoup
      2. If content is too thin, use crawl4ai (if installed)
      3. Send raw text to Gemini to extract clean JD

    Returns:
        dict with 'job_description' (clean text) and 'company_name' (if detected)
    """
    raw_text = _fetch_page_text(url)

    if not raw_text or len(raw_text.strip()) < 100:
        raise ValueError(
            "Could not extract enough content from this URL. "
            "The page may require JavaScript or login. "
            "Please paste the job description manually."
        )

    # Use Gemini to extract clean JD from raw page text
    return _extract_jd_with_llm(raw_text, url)


def _fetch_page_text(url):
    """Fetch page content using requests + BeautifulSoup."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        response.raise_for_status()
    except requests.RequestException as e:
        # Try crawl4ai as fallback
        return _try_crawl4ai(url) or ""

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script, style, nav, footer elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Try to find job description containers (common patterns)
    jd_selectors = [
        {"class_": re.compile(r"job.?(description|details|content|body)", re.I)},
        {"class_": re.compile(r"posting.?(body|content|description)", re.I)},
        {"id": re.compile(r"job.?(description|details|content)", re.I)},
        {"class_": re.compile(r"description", re.I)},
    ]

    for selector in jd_selectors:
        container = soup.find("div", **selector) or soup.find("section", **selector)
        if container and len(container.get_text(strip=True)) > 200:
            return container.get_text(separator="\n", strip=True)

    # Fallback: get all body text
    body = soup.find("body")
    if body:
        text = body.get_text(separator="\n", strip=True)
        # If page text is too short, try crawl4ai
        if len(text) < 100:
            crawl_text = _try_crawl4ai(url)
            if crawl_text:
                return crawl_text
        return text

    return ""


def _try_crawl4ai(url):
    """Try using crawl4ai for JavaScript-heavy pages."""
    try:
        from crawl4ai import WebCrawler
        crawler = WebCrawler()
        crawler.warmup()
        result = crawler.run(url=url)
        if result and result.markdown:
            return result.markdown
    except (ImportError, Exception):
        pass
    return None


def _extract_jd_with_llm(raw_text, url=""):
    """Use Gemini to extract a clean job description from raw page text."""
    # Truncate if too long (keep first 8000 chars)
    if len(raw_text) > 8000:
        raw_text = raw_text[:8000]

    prompt = f"""You are an expert at extracting job descriptions from web pages.

Given the raw text content scraped from a job posting page, extract ONLY the clean job description.

RULES:
1. Remove navigation menus, footers, ads, cookie notices, "similar jobs", and any non-JD content.
2. Keep the full job description including: title, company name, location, responsibilities, requirements, qualifications, benefits.
3. Preserve the structure (sections, bullet points) but remove HTML artifacts.
4. If you can identify the company name, include it.

URL: {url}

RAW PAGE TEXT:
{raw_text}

Return ONLY valid JSON with this structure (no markdown, no explanation):
{{
    "job_description": "The clean, complete job description text",
    "company_name": "Company name if found, otherwise empty string",
    "job_title": "Job title if found, otherwise empty string"
}}
"""

    response = generate(prompt)

    return parse_json_response(response.text)
