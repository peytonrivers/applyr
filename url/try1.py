"""
pipeline_js.py
JobSpy pipeline: entry-level accounting jobs in North Carolina
- Filters out senior roles
- Filters out irrelevant jobs (non-accounting)
- Resolves Indeed/LinkedIn URLs to direct ATS URLs via Serper
"""

import os
import time
import random
import httpx
from jobspy import scrape_jobs
from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv

load_dotenv()

SERPER_KEY = os.getenv("SERPER_KEY")

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
    "Charlotte, NC"
]

# Title must contain at least one of these to be considered accounting-related
ACCOUNTING_KEYWORDS = [
    "account", "accountant", "accounting", "bookkeep", "payroll",
    "audit", "tax", "billing",
    "budget", "controller", "cpa", "cma", "accounts payable",
    "accounts receivable", "gl ", "general ledger", "cost analyst",
    "revenue", "treasury", "fiscal", "ledger", "invoic",
]

# Any title containing these is filtered out regardless
SENIOR_TITLE_KEYWORDS = [
    "senior", " sr ", "sr.", " sr,", "(sr)", "sr-", "principal", "director",
    "manager", "head of", "vp ", "vice president", "chief",
    "supervisor", "lead ", " iii", " iv", " v ", " ii", " 2", " 3", " 4"
    " 5"
]

ATS_DOMAINS = [
    "greenhouse.io", "lever.co", "workday.com", "myworkdayjobs.com",
    "ashbyhq.com", "smartrecruiters.com", "jobvite.com", "icims.com",
    "taleo.net", "successfactors.com", "applytojob.com", "bamboohr.com",
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
    """Return True only if the title is actually accounting/finance related."""
    title_lower = title.lower()
    return any(kw in title_lower for kw in ACCOUNTING_KEYWORDS)


def is_entry_level(title: str) -> bool:
    """Return True if no senior-level keywords found in title."""
    title_lower = title.lower().strip()
    for kw in SENIOR_TITLE_KEYWORDS:
        if kw in title_lower:
            return False
    # Catch "Sr " at the very start of the title
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


# ---------------------------------------------------------------------------
# Serper ATS URL lookup
# ---------------------------------------------------------------------------

def company_matches_url(company: str, url: str) -> bool:
    """
    Check if the company name is reasonably reflected in the ATS URL.
    Checks the full URL (domain + path) to handle both cases:
      - Company in subdomain: barings.wd1.myworkdayjobs.com
      - Company in path: job-boards.greenhouse.io/creditkarma/jobs/123
    """
    if not company or company.lower() == "nan":
        return True  # no company to check against, allow it through

    # Strip common suffixes that won't appear in URLs
    noise = [
        " inc", " llc", " ltd", " corp", " co.", " co,",
        " group", " services", " solutions", " consulting",
        " partners", " associates", " company", " &", " and",
    ]
    company_clean = company.lower()
    for word in noise:
        company_clean = company_clean.replace(word, "")

    # Take first significant word (at least 3 chars)
    words = [w.strip(".,()-") for w in company_clean.split() if len(w.strip(".,()-")) >= 3]
    if not words:
        return True

    first_word = words[0]

    # Check full URL (domain + path) — catches both subdomain and path-based ATS platforms
    # e.g. greenhouse.io/creditkarma, smartrecruiters.com/CreditKarma
    full_url_lower = url.lower()

    return first_word in full_url_lower


def find_apply_url(title: str, company: str) -> str | None:
    """Use Serper.dev to find a direct ATS apply URL."""
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
            if is_aggregator(link):
                continue
            if not is_ats_url(link):
                continue
            if is_generic_url(link):
                continue
            if not company_matches_url(company, link):
                continue
            return clean_url(link)

    except httpx.HTTPError as e:
        print(f"  [serper] Error: {e}")

    return None


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run():
    seen_urls = set()
    all_jobs = []
    total_raw = 0
    skipped_senior = 0
    skipped_irrelevant = 0
    urls_found = 0
    urls_not_found = 0

    print(f"Scraping {len(QUERIES)} titles × {len(LOCATIONS)} cities...\n")

    for location in LOCATIONS:
        for query in QUERIES:
            try:
                df = scrape_jobs(
                    site_name=["indeed", "zip_recruiter", "linkedin", "google"],
                    search_term=query,
                    location=location,
                    results_wanted=20,
                    hours_old=72,
                    country_indeed="USA",
                )
            except Exception as e:
                print(f"  ERROR {query} @ {location}: {e}")
                continue

            if df is None or df.empty:
                continue

            total_raw += len(df)

            for _, row in df.iterrows():
                title   = str(row.get("title", "")).strip()
                company = str(row.get("company", "")).strip()
                job_url = str(row.get("job_url", "")).strip()
                job_loc = str(row.get("location", "")).strip()

                if not title or not job_url or job_url == "nan":
                    continue

                # Dedup by source URL
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                # Filter: must be accounting related
                if not is_accounting_role(title):
                    skipped_irrelevant += 1
                    continue

                # Filter: no senior roles
                if not is_entry_level(title):
                    skipped_senior += 1
                    continue

                # Resolve ATS URL
                if is_ats_url(job_url) and not is_generic_url(job_url):
                    apply_url = clean_url(job_url)
                    urls_found += 1
                else:
                    apply_url = find_apply_url(title, company)
                    if apply_url:
                        urls_found += 1
                    else:
                        urls_not_found += 1

                all_jobs.append({
                    "title": title,
                    "company": company,
                    "location": job_loc,
                    "url": apply_url or job_url,
                    "has_ats_url": apply_url is not None,
                })

            print(f"  [{location}] {query} → {len(df)} raw")
            time.sleep(random.uniform(1, 3))

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
        print(f"    {job['url']}")
        print("-" * 40)


if __name__ == "__main__":
    run()