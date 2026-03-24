"""
Web Scraper for Job Posting URLs
Supports LinkedIn, Internshala, Indeed, Naukri, and generic pages.
"""

import re
import time
from urllib.parse import urlparse
from typing import Optional


def scrape_job_url(url: str) -> dict:
    """
    Scrape a job posting URL and return structured data.
    
    Returns:
        dict with text, domain, has_ssl, source_platform, domain_age_days, etc.
        OR dict with 'error' key on failure.
    """
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # ── Remove non-content elements ──
        for tag in soup(["script", "style", "nav", "footer",
                          "header", "aside", "iframe", "noscript"]):
            tag.decompose()

        # ── Try platform-specific selectors first ──
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        platform = detect_platform(domain)

        text = _extract_by_platform(soup, platform)

        # Fallback: get all visible text
        if not text or len(text.strip()) < 100:
            text = soup.get_text(separator=" ", strip=True)

        # Clean up extracted text
        text = re.sub(r"\s+", " ", text).strip()
        text = text[:8000]  # cap at 8000 chars

        # ── Extract emails from page ──
        page_text = response.text
        emails = list(set(re.findall(
            r'\b[\w.\-+]+@[\w.\-]+\.\w{2,}\b', page_text, re.I
        )))

        # ── Domain age (optional, needs python-whois) ──
        domain_age = get_domain_age(domain)

        return {
            "text": text,
            "domain": domain,
            "source_platform": platform,
            "has_ssl": url.startswith("https://"),
            "domain_age_days": domain_age,
            "emails_found": emails[:5],  # limit to 5
            "url": url,
        }

    except ImportError:
        return {"error": "requests or beautifulsoup4 not installed. Run: pip install requests beautifulsoup4"}
    except Exception as e:
        return {"error": str(e)}


def _extract_by_platform(soup, platform: str) -> str:
    """Use platform-specific CSS selectors for better extraction."""

    selectors_map = {
        "LinkedIn": [
            ".job-view-layout",
            ".description__text",
            ".show-more-less-html__markup",
            "article.job-view-layout",
        ],
        "Internshala": [
            ".internship_details",
            ".about_company_text_container",
            "#about_internship",
            ".other_detail_item",
        ],
        "Indeed": [
            "#jobDescriptionText",
            ".jobsearch-jobDescriptionText",
            "[data-testid='jobsearch-JobComponent-description']",
        ],
        "Naukri": [
            ".job-desc",
            ".dang-inner-html",
            "#job_description",
        ],
        "Glassdoor": [
            "[data-test='jobDescription']",
            ".jobDescriptionContent",
        ],
    }

    selectors = selectors_map.get(platform, [])
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return element.get_text(separator=" ", strip=True)

    return ""


def detect_platform(domain: str) -> str:
    """Identify the job platform from the domain."""
    platform_map = {
        "linkedin.com": "LinkedIn",
        "internshala.com": "Internshala",
        "indeed.com": "Indeed",
        "naukri.com": "Naukri",
        "glassdoor.com": "Glassdoor",
        "shine.com": "Shine",
        "monster.com": "Monster",
        "timesjobs.com": "TimesJobs",
        "unstop.com": "Unstop",
        "wellfound.com": "Wellfound",
        "freshersworld.com": "FreshersWorld",
    }
    for key, name in platform_map.items():
        if key in domain:
            return name
    return "Unknown"


def get_domain_age(domain: str) -> int:
    """
    Get domain age in days using WHOIS lookup.
    Returns 365 as default if lookup fails or python-whois not installed.
    """
    try:
        import whois
        from datetime import datetime, timezone

        w = whois.whois(domain)
        created = w.creation_date

        # Handle list of dates
        if isinstance(created, list):
            created = created[0]

        if created is None:
            return 365

        # Make timezone-aware comparison
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        age_days = (now - created).days
        return max(0, age_days)

    except Exception:
        return 365  # default: assume established domain
