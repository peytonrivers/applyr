"""
pipeline_js.py
JobSpy pipeline: entry-level accounting jobs in North Carolina
- Filters out senior roles
- Filters out irrelevant jobs (non-accounting)
- Resolves Indeed/LinkedIn/ZipRecruiter URLs to direct non-aggregator URLs via Serper
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

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

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

ACCOUNTING_KEYWORDS = [
    "account", "accountant", "accounting", "bookkeep", "payroll",
    "audit", "tax", "billing",
    "budget", "controller", "cpa", "cma", "accounts payable",
    "accounts receivable", "gl ", "general ledger", "cost analyst",
    "revenue", "treasury", "fiscal", "ledger", "invoic",
]

SENIOR_TITLE_KEYWORDS = [
    "senior", " sr ", "sr.", " sr,", "(sr)", "sr-", "principal", "director",
    "manager", "head of", "vp ", "vice president", "chief",
    "supervisor", "lead ", " iii", " iv", " v ", " ii", " 2", " 3", " 4", " 5"
]

ATS_DOMAINS = [
    "greenhouse.io", "lever.co", "workday.com", "myworkdayjobs.com",
    "ashbyhq.com", "smartrecruiters.com", "jobvite.com", "icims.com",
    "taleo.net", "successfactors.com", "applytojob.com", "bamboohr.com",
    "paylocity.com", "breezy.hr", "avature.net", "recruitingbypaycor.com",
    "ultipro.com", "oraclecloud.com", "workable.com", "recruitee.com",
    "pinpointhq.com", "dover.com", "careerplug.com", "jazz.co",
    "rippling.com", "jobvite.com", "kronos.net", "adp.com",
    "ceridian.com", "silkroad.com", "cornerstone", "sap.com",
]

AGGREGATORS = [
    "indeed.com", "linkedin.com", "ziprecruiter.com", "glassdoor.com",
    "simplyhired.com", "monster.com", "careerbuilder.com", "lensa.com",
    "talent.com", "joblist.com", "builtin.com", "wellfound.com",
]

GENERIC_URL_ENDINGS = [
    "/careers", "/careers/", "/jobs", "/jobs/", "/internships",
    "/internships/", "/career-opportunities", "/career-opportunities/",
    "/work-with-us", "/work-with-us/", "/join-us", "/join-us/",
    "/job-search", "/openings", "/openings/", "/join-our-team",
    "/join-our-team/", "/about-royal/careers/internships",
    "/about-your-bank/work-with-us/careers/students.html",
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
    if not url:
        return False
    return any(agg in url.lower() for agg in AGGREGATORS)


def is_ats_url(url: str) -> bool:
    if not url:
        return False
    return any(domain in url.lower() for domain in ATS_DOMAINS)


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
# LinkedIn guest API resolver
# ---------------------------------------------------------------------------

def resolve_linkedin_url(title: str, company: str, location: str) -> str | None:
    return find_apply_url(title, company, location)


# ---------------------------------------------------------------------------
# Serper lookup
# ---------------------------------------------------------------------------

def build_search_name(title: str, company: str, location: str) -> str:
    parts = [title.strip()]
    if company and company.lower() != "nan":
        parts.append(company.strip())
    if location and location.lower() != "nan":
        parts.append(f"Jobs in {location.strip()}")
    return " ".join(parts)


def find_apply_url(title: str, company: str, location: str) -> str | None:
    """
    Search Serper using the posting-style name:
        '<title> <company> Jobs in <location>'

    Prints the first 5 results and returns the first non-aggregator link
    from the top 5 results.
    """
    query = build_search_name(title, company, location)

    try:
        resp = httpx.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": SERPER_KEY,
                "Content-Type": "application/json",
            },
            json={"q": query, "num": 5},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("organic", [])

        print(f"\n🔍 FIRST 5 RESULTS FOR: {query}\n" + "-" * 60)
        for i, result in enumerate(results[:5], start=1):
            print(f"{i}. {result.get('title')}")
            print(f"   {result.get('link')}\n")

        for result in results[:5]:
            link = result.get("link", "")
            if not link:
                continue
            if is_aggregator(link):
                continue
            return clean_url(link)

    except httpx.HTTPError as e:
        print(f"  [serper] Error for '{query}': {e}")

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
                title = str(row.get("title", "")).strip()
                company = str(row.get("company", "")).strip()
                job_url = str(row.get("job_url", "")).strip()
                job_loc = str(row.get("location", "")).strip()

                if not title or not job_url or job_url == "nan":
                    continue

                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                if not is_accounting_role(title):
                    skipped_irrelevant += 1
                    continue

                if not is_entry_level(title):
                    skipped_senior += 1
                    continue

                if is_ats_url(job_url) and not is_generic_url(job_url):
                    apply_url = clean_url(job_url)
                    urls_found += 1

                elif any(domain in job_url.lower() for domain in ["linkedin.com", "indeed.com", "ziprecruiter.com"]):
                    apply_url = find_apply_url(title, company, job_loc)
                    if apply_url:
                        urls_found += 1
                    else:
                        urls_not_found += 1

                else:
                    apply_url = find_apply_url(title, company, job_loc)
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