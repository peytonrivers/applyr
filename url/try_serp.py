"""
pipeline_sa.py
SerpAPI Google Jobs pipeline: entry-level accounting jobs in North Carolina
- Discovers jobs via SerpAPI Google Jobs engine
- Filters out senior roles and irrelevant jobs
- Resolves ATS URLs via Serper.dev
"""

import os
import re
import time
import random
import httpx
from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv

load_dotenv()

SERPER_KEY = os.getenv("SERPER_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

QUERIES = [
    "accountant", "accounting analyst", "staff accountant",
    "junior accountant", "accounting associate", "accounts payable",
    "accounts receivable", "bookkeeper", "payroll specialist",
    "audit associate", "tax associate",
    "accounting intern", "accounting coordinator", "cost accountant",
    "general ledger accountant", "accounting clerk", "billing specialist",
    "budget analyst", "controller", "CPA", "accounting graduate",
]

LOCATIONS = [
    "Charlotte, NC", "Raleigh, NC"
]

ACCOUNTING_KEYWORDS = [
    "account", "accountant", "accounting", "bookkeep", "payroll",
    "audit", "tax", "billing", "budget", "controller", "cpa", "cma",
    "accounts payable", "accounts receivable", "gl ", "general ledger",
    "cost analyst", "revenue", "treasury", "fiscal", "ledger", "invoic",
]

SENIOR_TITLE_KEYWORDS = [
    "senior", " sr ", "sr.", " sr,", "(sr)", "sr-", "principal", "director",
    "manager", "head of", "vp ", "vice president", "chief",
    "supervisor", "lead ", " iii", " iv", " v ", " ii", " 2", " 3", " 4", " 5",
]

ATS_DOMAINS = [
    "greenhouse.io", "lever.co", "workday.com", "myworkdayjobs.com",
    "ashbyhq.com", "smartrecruiters.com", "jobvite.com", "icims.com",
    "taleo.net", "successfactors.com", "applytojob.com", "bamboohr.com",
    "paylocity.com", "breezy.hr", "avature.net", "recruitingbypaycor.com",
    "ultipro.com", "oraclecloud.com", "workable.com", "recruitee.com",
    "pinpointhq.com", "dover.com", "careerplug.com", "jazz.co",
    "rippling.com", "kronos.net", "adp.com", "ceridian.com",
    "silkroad.com", "cornerstone", "sap.com",
]

AGGREGATORS = [
    "indeed.com", "linkedin.com", "ziprecruiter.com", "glassdoor.com",
    "simplyhired.com", "monster.com", "careerbuilder.com", "lensa.com",
    "talent.com", "joblist.com", "builtin.com", "wellfound.com",
]

GENERIC_URL_ENDINGS = [
    "/careers", "/careers/", "/jobs", "/jobs/", "/openings",
    "/openings/", "/join-us", "/work-with-us", "/join-our-team",
]


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

def is_accounting_role(title: str) -> bool:
    title_lower = title.lower()
    return any(kw in title_lower for kw in ACCOUNTING_KEYWORDS)


def is_entry_level(title: str) -> bool:
    title_lower = title.lower().strip()
    for kw in SENIOR_TITLE_KEYWORDS:
        if kw in title_lower:
            return False
    if title_lower.startswith("sr ") or title_lower.startswith("sr."):
        return False
    return True


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

def is_aggregator(url: str) -> bool:
    return any(agg in url for agg in AGGREGATORS)


def is_ats_url(url: str) -> bool:
    return any(domain in url for domain in ATS_DOMAINS)


def is_generic_url(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/").lower()
    for ending in GENERIC_URL_ENDINGS:
        if path.endswith(ending.rstrip("/")):
            return True
    segments = [s for s in path.split("/") if s]
    if len(segments) <= 1 and not parsed.query:
        return True
    return False


def clean_url(url: str) -> str:
    tracking_params = [
        "utm_source", "utm_medium", "utm_campaign",
        "src", "source", "sourceType", "gh_src", "trk", "refId",
        "lever-source",
    ]
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    clean_params = {k: v for k, v in params.items() if k not in tracking_params}
    clean_query = urlencode({k: v[0] for k, v in clean_params.items()})
    return parsed._replace(query=clean_query).geturl()


def company_matches_url(company: str, url: str) -> bool:
    if not company or company.lower() == "nan":
        return True
    noise = [
        " inc", " llc", " ltd", " corp", " co.", " co,",
        " group", " services", " solutions", " consulting",
        " partners", " associates", " company", " &", " and",
    ]
    company_clean = company.lower()
    for word in noise:
        company_clean = company_clean.replace(word, "")
    words = [w.strip(".,()-") for w in company_clean.split() if len(w.strip(".,()-")) >= 3]
    if not words:
        return True
    return words[0] in url.lower()


# ---------------------------------------------------------------------------
# Serper URL resolution
# ---------------------------------------------------------------------------

def find_apply_url(name: str) -> str | None:
    """Search Serper for the job by name and return the first non-aggregator result."""
    try:
        resp = httpx.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": SERPER_KEY,
                "Content-Type": "application/json",
            },
            json={"q": name, "num": 5},
            timeout=15,
        )
        resp.raise_for_status()

        for result in resp.json().get("organic", []):
            link = result.get("link", "")
            if not is_aggregator(link):
                return link

    except httpx.HTTPError as e:
        print(f"  [serper] Error: {e}")

    return None


# ---------------------------------------------------------------------------
# SerpAPI Google Jobs discovery
# ---------------------------------------------------------------------------

def fetch_google_jobs(query: str, location: str) -> list:
    """Fetch jobs from Google Jobs via SerpAPI."""
    try:
        resp = httpx.get(
            "https://serpapi.com/search",
            params={
                "engine": "google_jobs",
                "q": f"{query} {location}",
                "location": location,
                "hl": "en",
                "api_key": SERPAPI_KEY,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        if "error" in data:
            print(f"  [serpapi] Error: {data['error']}")
            return []

        return data.get("jobs_results", [])

    except httpx.HTTPError as e:
        print(f"  [serpapi] HTTP error: {e}")
        return []


def extract_ats_from_apply_options(apply_options: list) -> str | None:
    """
    Google Jobs results often include apply_options with direct ATS URLs.
    Check those before falling back to Serper.
    """
    for option in apply_options:
        link = option.get("link", "")
        if not link:
            continue
        if is_aggregator(link):
            continue
        if is_ats_url(link) and not is_generic_url(link):
            return clean_url(link)
    return None


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run():
    seen = set()
    all_jobs = []
    total_raw = 0
    skipped_irrelevant = 0
    skipped_senior = 0
    urls_found = 0
    urls_not_found = 0

    print(f"Scraping {len(QUERIES)} titles × {len(LOCATIONS)} cities via SerpAPI Google Jobs...\n")

    for location in LOCATIONS:
        for query in QUERIES:
            jobs = fetch_google_jobs(query, location)

            if not jobs:
                print(f"  [{location}] {query} → 0 results")
                time.sleep(random.uniform(1, 2))
                continue

            total_raw += len(jobs)
            print(f"  [{location}] {query} → {len(jobs)} raw")

            for job in jobs:
                title   = str(job.get("title", "")).strip()
                company = str(job.get("company_name", "")).strip()
                location_str = str(job.get("location", "")).strip()

                if not title or not company:
                    continue

                # Dedup by title + company
                key = f"{title.lower()}|{company.lower()}"
                if key in seen:
                    continue
                seen.add(key)

                # Filter: must be accounting related
                if not is_accounting_role(title):
                    skipped_irrelevant += 1
                    continue

                # Filter: no senior roles
                if not is_entry_level(title):
                    skipped_senior += 1
                    continue

                # Try apply_options from Google Jobs first
                apply_options = job.get("apply_options", [])
                apply_url = extract_ats_from_apply_options(apply_options)

                # Fall back to Serper
                # Build the name exactly as Google Jobs formats it
                if not apply_url:
                    name = f"{title} @ {company}"
                    apply_url = find_apply_url(name)

                if apply_url:
                    urls_found += 1
                else:
                    urls_not_found += 1

                all_jobs.append({
                    "title": title,
                    "company": company,
                    "location": location_str,
                    "url": apply_url,
                    "has_ats_url": apply_url is not None,
                })

            time.sleep(random.uniform(1, 2))

    # Summary
    print(f"\n{'='*60}")
    print(f"Raw jobs scraped:      {total_raw}")
    print(f"Skipped (irrelevant):  {skipped_irrelevant}")
    print(f"Skipped (senior):      {skipped_senior}")
    print(f"Jobs after filters:    {len(all_jobs)}")
    print(f"ATS URLs found:        {urls_found}")
    print(f"ATS URLs not found:    {urls_not_found}")
    print(f"{'='*60}\n")

    for job in all_jobs:
        status = "✓" if job["has_ats_url"] else "?"
        print(f"[{status}] {job['title']} @ {job['company']}")
        print(f"    {job['location']}")
        print(f"    {job['url'] or 'No ATS URL found'}")
        print("-" * 40)


if __name__ == "__main__":
    run()