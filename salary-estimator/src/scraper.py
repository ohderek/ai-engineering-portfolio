"""
URL scraping for job postings and LinkedIn profiles.

  - Job postings  : httpx + BeautifulSoup (works for most public boards)
  - LinkedIn URLs : Playwright with cookie-based session persistence
                    Requires LINKEDIN_EMAIL + LINKEDIN_PASSWORD in .env on first run;
                    subsequent runs reuse the saved session cookie.
"""

import json
import os
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

_COOKIES_FILE = Path(__file__).parent.parent / ".linkedin_session.json"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Ordered list of CSS selectors tried for job posting text extraction
_JOB_SELECTORS = [
    # Greenhouse
    "#content", ".content-intro",
    # Lever
    ".posting-content", ".content",
    # Workday
    "[data-automation-id='jobPostingDescription']",
    # Indeed
    "#jobDescriptionText", ".jobsearch-jobDescriptionText",
    # Ashby
    ".ashby-job-posting-brief-description",
    # LinkedIn Jobs (public view)
    ".description__text", ".show-more-less-html__markup",
    # Generic fallbacks
    "[class*='job-description']", "[class*='jobDescription']",
    "[id*='job-description']", "[id*='jobDescription']",
    "main article", "article", "main",
]


def is_linkedin_url(url: str) -> bool:
    return "linkedin.com" in urlparse(url).netloc


def fetch_url(url: str) -> str:
    """Main entry point — routes to the appropriate fetcher."""
    if is_linkedin_url(url):
        return _fetch_with_playwright(url)
    return _fetch_html(url)


# ── Plain HTTP fetcher ─────────────────────────────────────────────────────────

def _fetch_html(url: str) -> str:
    with httpx.Client(follow_redirects=True, timeout=20, headers=_HEADERS) as client:
        response = client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "nav", "header", "footer", "iframe", "aside"]):
        tag.decompose()

    # Try specific job board selectors first
    for selector in _JOB_SELECTORS:
        element = soup.select_one(selector)
        if element:
            text = element.get_text(separator="\n", strip=True)
            if len(text) > 300:
                return text

    # Fallback to full body text
    body = soup.find("body")
    return (body or soup).get_text(separator="\n", strip=True)


# ── Playwright fetcher (LinkedIn) ──────────────────────────────────────────────

def _fetch_with_playwright(url: str) -> str:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        raise ImportError(
            "Playwright is not installed. Run: pip install playwright && playwright install chromium"
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=_HEADERS["User-Agent"],
            viewport={"width": 1280, "height": 900},
        )

        # Restore saved session if available
        if _COOKIES_FILE.exists():
            with open(_COOKIES_FILE) as f:
                context.add_cookies(json.load(f))

        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        except PWTimeout:
            pass  # Partial load is often enough

        # Detect login wall and authenticate if needed
        if _needs_login(page.url):
            _linkedin_login(page, context)
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)

        # Scroll to trigger lazy-loaded sections
        for _ in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1_200)

        text = _extract_linkedin_text(page, url)
        browser.close()

    return text


def _needs_login(current_url: str) -> bool:
    return any(x in current_url for x in ("login", "authwall", "checkpoint"))


def _linkedin_login(page, context) -> None:
    email = os.getenv("LINKEDIN_EMAIL", "").strip()
    password = os.getenv("LINKEDIN_PASSWORD", "").strip()

    if not email or not password:
        raise ValueError(
            "LinkedIn requires authentication.\n"
            "Add LINKEDIN_EMAIL and LINKEDIN_PASSWORD to your .env file and try again."
        )

    page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
    page.fill("#username", email)
    page.fill("#password", password)
    page.click("button[type='submit']")

    try:
        page.wait_for_url("**/feed**", timeout=15_000)
    except Exception:
        raise RuntimeError(
            "LinkedIn login failed — check your credentials or complete any security challenge manually."
        )

    # Persist cookies for future runs
    cookies = context.cookies()
    with open(_COOKIES_FILE, "w") as f:
        json.dump(cookies, f)


def _extract_linkedin_text(page, url: str) -> str:
    is_profile = "/in/" in url

    if is_profile:
        # Try structured profile sections first
        selectors = [
            ".pv-top-card",
            ".experience-section",
            ".education-section",
            ".pv-about-section",
            "main",
        ]
        parts = []
        for sel in selectors:
            el = page.query_selector(sel)
            if el:
                t = el.inner_text().strip()
                if t:
                    parts.append(t)
        if parts:
            return "\n\n".join(parts)
    else:
        # Job posting
        for sel in [".description__text", ".show-more-less-html__markup", "main"]:
            el = page.query_selector(sel)
            if el:
                t = el.inner_text().strip()
                if len(t) > 300:
                    return t

    # Final fallback
    return page.inner_text("body")
