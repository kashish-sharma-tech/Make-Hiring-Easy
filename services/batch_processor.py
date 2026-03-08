import os
import csv
import json
import zipfile
import io
import re
from services.jd_scraper import scrape_jd_from_url
from services.keyword_extractor import extract_jd_keywords
from services.resume_optimizer import optimize_resume
from services.cover_letter_generator import generate_cover_letter, generate_cover_letter_pdf
from services.pdf_generator import generate_pdf


def _sanitize_folder_name(name):
    """Create a safe folder name from company name."""
    name = re.sub(r'[^\w\s-]', '', name).strip()
    name = re.sub(r'[\s]+', '_', name)
    return name or "Unknown_Company"


def process_batch(resume_text, csv_file, progress_callback=None):
    """Process a batch of job URLs from a CSV file.

    CSV format: job_url, company_name (optional)

    Args:
        resume_text: Extracted text from the user's resume
        csv_file: File-like object or path to CSV
        progress_callback: Function(current, total, company, status) for progress updates

    Returns:
        dict with 'results' list, 'output_dir', and 'zip_path'
    """
    # Parse CSV
    jobs = _parse_csv(csv_file)
    if not jobs:
        raise ValueError("No valid job entries found in CSV. Expected columns: job_url, company_name (optional)")

    total = len(jobs)
    results = []
    base_output_dir = os.path.abspath("outputs/batch")
    os.makedirs(base_output_dir, exist_ok=True)

    for i, job in enumerate(jobs):
        url = job["url"]
        company = job.get("company", "")
        status = {"step": "", "success": False, "error": None}

        try:
            if progress_callback:
                progress_callback(i, total, company or url, "Scraping job description...")

            # Step 1: Scrape JD
            status["step"] = "scraping"
            scraped = scrape_jd_from_url(url)
            jd_text = scraped["job_description"]
            if not company:
                company = scraped.get("company_name", "") or f"Job_{i+1}"
            job_title = scraped.get("job_title", "")

            if progress_callback:
                progress_callback(i, total, company, "Extracting keywords...")

            # Step 2: Extract keywords
            status["step"] = "keywords"
            jd_keywords = extract_jd_keywords(jd_text)

            if progress_callback:
                progress_callback(i, total, company, "Optimizing resume...")

            # Step 3: Optimize resume
            status["step"] = "optimizing"
            optimized = optimize_resume(resume_text, jd_text, jd_keywords)

            if progress_callback:
                progress_callback(i, total, company, "Generating cover letter...")

            # Step 4: Generate cover letter
            status["step"] = "cover_letter"
            cover_letter = generate_cover_letter(optimized, jd_text, company)

            # Step 5: Save outputs in company folder
            folder_name = _sanitize_folder_name(company)
            company_dir = os.path.join(base_output_dir, folder_name)
            os.makedirs(company_dir, exist_ok=True)

            if progress_callback:
                progress_callback(i, total, company, "Generating PDFs...")

            # Save JSON metadata
            metadata = {
                "company": company,
                "job_title": job_title,
                "url": url,
                "seniority_level": optimized.get("seniority_level", "Unknown"),
                "keywords": jd_keywords,
            }
            with open(os.path.join(company_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)

            # Save resume JSON
            with open(os.path.join(company_dir, "resume.json"), "w") as f:
                json.dump(optimized, f, indent=2)

            # Save cover letter JSON
            with open(os.path.join(company_dir, "cover_letter.json"), "w") as f:
                json.dump(cover_letter, f, indent=2)

            # Generate PDFs
            status["step"] = "pdf_generation"
            try:
                generate_pdf(optimized, output_dir=company_dir)
                os.rename(
                    os.path.join(company_dir, "optimized_resume.pdf"),
                    os.path.join(company_dir, f"{folder_name}_Resume.pdf")
                )
            except Exception as pdf_err:
                status["error"] = f"Resume PDF failed: {pdf_err}"

            try:
                generate_cover_letter_pdf(cover_letter, output_dir=company_dir)
                os.rename(
                    os.path.join(company_dir, "cover_letter.pdf"),
                    os.path.join(company_dir, f"{folder_name}_CoverLetter.pdf")
                )
            except Exception as pdf_err:
                if status["error"]:
                    status["error"] += f"; Cover letter PDF failed: {pdf_err}"
                else:
                    status["error"] = f"Cover letter PDF failed: {pdf_err}"

            status["success"] = True
            results.append({
                "company": company,
                "job_title": job_title,
                "url": url,
                "seniority": optimized.get("seniority_level", "Unknown"),
                "folder": company_dir,
                "success": True,
                "error": status.get("error"),
            })

        except Exception as e:
            results.append({
                "company": company or url,
                "job_title": "",
                "url": url,
                "seniority": "",
                "folder": "",
                "success": False,
                "error": f"Failed at {status['step']}: {str(e)}",
            })

        if progress_callback:
            progress_callback(i + 1, total, company or url, "Done" if status["success"] else "Failed")

    # Create ZIP of all outputs
    zip_path = os.path.join(base_output_dir, "all_applications.zip")
    _create_zip(base_output_dir, zip_path)

    return {
        "results": results,
        "output_dir": base_output_dir,
        "zip_path": zip_path,
        "total": total,
        "successful": sum(1 for r in results if r["success"]),
    }


def _parse_csv(csv_file):
    """Parse CSV file with job URLs and optional company names."""
    jobs = []

    if isinstance(csv_file, str):
        with open(csv_file, "r") as f:
            content = f.read()
    else:
        content = csv_file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")

    reader = csv.reader(io.StringIO(content))

    for row_num, row in enumerate(reader):
        if not row:
            continue
        # Skip header row
        if row_num == 0 and any(h.lower().strip() in ("url", "job_url", "link", "company", "company_name") for h in row):
            continue

        url = row[0].strip()
        if not url or not url.startswith("http"):
            continue

        company = row[1].strip() if len(row) > 1 else ""
        jobs.append({"url": url, "company": company})

    return jobs


def _create_zip(source_dir, zip_path):
    """Create a ZIP file from all company folders."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            # Skip the zip file itself
            for file in files:
                if file == "all_applications.zip":
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zf.write(file_path, arcname)
