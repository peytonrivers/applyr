"""
pipeline.py
MVP: LinkedIn public URL → entry level filter → Serper.dev search for apply URL
"""

import httpx
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv

load_dotenv()

SERPER_KEY = os.getenv("SERPER_KEY")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

EXCLUDED_SENIORITY = {"mid-senior level", "senior level", "director", "executive"}

SENIOR_TITLE_KEYWORDS = [
    "senior", "sr.", "lead", "principal", "staff",
    "director", "manager", "head of", "vp", "vice president", "architect",
]

ATS_DOMAINS = [
    "greenhouse.io", "lever.co", "workday.com", "myworkdayjobs.com",
    "ashbyhq.com", "smartrecruiters.com", "jobvite.com", "icims.com",
    "taleo.net", "successfactors.com", "applytojob.com", "bamboohr.com",
]

AGGREGATORS = [
    "ziprecruiter.com", "simplyhired.com", "dice.com", "adzuna.com",
    "talentify.io", "jobright.ai", "tealhq.com", "glassdoor.com",
    "indeed.com", "wellfound.com", "angel.co", "angellist.com",
    "monster.com", "careerbuilder.com", "snagajob.com", "ladders.com",
    "builtin.com", "jobgether.com", "jooble.org", "talent.com",
    "careerjet.com", "lensa.com", "linkedin.com", "salary.com",
    "learn4good.com", "wayup.com", "joblist.com",
]

GENERIC_URL_ENDINGS = [
    "/careers", "/careers/", "/jobs", "/jobs/", "/internships",
    "/openings", "/openings/", "/join-us", "/work-with-us",
    "/join-our-team", "/career-opportunities",
]


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

def is_aggregator(url: str) -> bool:
    return any(agg in url for agg in AGGREGATORS)


def is_generic_url(url: str) -> bool:
    """Return True if URL points to a careers homepage rather than a specific job."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/").lower()

    # Ends with a known generic path
    for ending in GENERIC_URL_ENDINGS:
        if path.endswith(ending.rstrip("/")):
            return True

    # Path is too short to be a specific job (e.g. /careers or /jobs/search)
    # Specific jobs always have an ID or slug making the path at least 3 segments
    segments = [s for s in path.split("/") if s]
    if len(segments) <= 1 and not parsed.query:
        return True

    return False


def clean_url(url: str) -> str:
    """Strip tracking params from a URL."""
    tracking_params = [
        "utm_source", "utm_medium", "utm_campaign",
        "src", "source", "sourceType", "gh_src", "trk", "refId",
    ]
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    clean_params = {k: v for k, v in params.items() if k not in tracking_params}
    clean_query = urlencode({k: v[0] for k, v in clean_params.items()})
    return parsed._replace(query=clean_query).geturl()


# ---------------------------------------------------------------------------
# Step 1: Get job IDs from a LinkedIn public search URL
# ---------------------------------------------------------------------------

def get_job_ids(linkedin_search_url: str) -> list[str]:
    """Extract job IDs from a LinkedIn public job search page."""
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=10) as client:
        resp = client.get(linkedin_search_url)

    soup = BeautifulSoup(resp.text, "html.parser")

    job_ids = []
    for tag in soup.find_all("div", attrs={"data-entity-urn": True}):
        urn = tag["data-entity-urn"]
        match = re.search(r":(\d+)$", urn)
        if match:
            job_ids.append(match.group(1))

    print(f"Found {len(job_ids)} jobs")
    return job_ids


# ---------------------------------------------------------------------------
# Step 2: Fetch job detail + entry level filter
# ---------------------------------------------------------------------------

def fetch_job_detail(job_id: str) -> BeautifulSoup | None:
    """Fetch individual job HTML from LinkedIn guest API."""
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    try:
        with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=10) as client:
            resp = client.get(url)
            resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except httpx.HTTPError:
        return None


def is_entry_level(soup: BeautifulSoup, title: str) -> bool:
    """Return True if the job passes the entry level filter."""
    for li in soup.find_all("li", class_=re.compile("description__job-criteria-item")):
        header = li.find("h3")
        value = li.find("span")
        if header and value and "seniority" in header.get_text(strip=True).lower():
            seniority = value.get_text(strip=True).lower()
            if seniority in EXCLUDED_SENIORITY:
                return False

    title_lower = title.lower()
    if any(kw in title_lower for kw in SENIOR_TITLE_KEYWORDS):
        return False

    return True


# ---------------------------------------------------------------------------
# Step 3: Serper.dev search for ATS apply URL
# ---------------------------------------------------------------------------

def find_apply_url(title: str, company: str) -> str | None:
    """Use Serper.dev to find a direct ATS apply URL for this job."""
    query = f"{title} {company} apply"

    try:
        resp = httpx.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": SERPER_KEY,
                "Content-Type": "application/json",
            },
            json={"q": query, "num": 10},
            timeout=10,
        )
        resp.raise_for_status()

        for result in resp.json().get("organic", []):
            link = result.get("link", "")

            # Reject aggregators
            if is_aggregator(link):
                continue

            # Must match a known ATS domain
            if not any(domain in link for domain in ATS_DOMAINS):
                continue

            # Reject generic career homepages
            if is_generic_url(link):
                continue

            return clean_url(link)

    except httpx.HTTPError as e:
        print(f"  [serper] Error: {e}")

    return None


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(linkedin_search_url: str):
    print(f"Scraping: {linkedin_search_url}\n")
    job_ids = get_job_ids(linkedin_search_url)

    found = 0
    skipped = 0
    no_url = 0

    for job_id in job_ids:
        soup = fetch_job_detail(job_id)
        if not soup:
            continue

        title_tag = soup.find("h2", class_=re.compile("top-card-layout__title"))
        company_tag = soup.find("a", class_=re.compile("topcard__org-name-link")) \
                      or soup.find("span", class_=re.compile("topcard__org-name"))

        title = title_tag.get_text(strip=True) if title_tag else "Unknown"
        company = company_tag.get_text(strip=True) if company_tag else "Unknown"

        if not is_entry_level(soup, title):
            print(f"SKIP  {title} @ {company}")
            skipped += 1
            continue

        apply_url = find_apply_url(title, company)

        if apply_url:
            print(f"FOUND {title} @ {company}")
            print(f"      {apply_url}")
            found += 1
        else:
            print(f"NO URL {title} @ {company}")
            no_url += 1

    print(f"\n--- Results ---")
    print(f"URLs found:  {found}")
    print(f"No URL:      {no_url}")
    print(f"Skipped:     {skipped}")
    print(f"Total jobs:  {len(job_ids)}")


if __name__ == "__main__":
    run(
        "https://www.linkedin.com/jobs/search?keywords=entry%20level%20Ai%20Engineer&location=North%20Carolina&geoId=103255397&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"
    )