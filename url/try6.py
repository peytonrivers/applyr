"""
pipeline_js.py
JobSpy pipeline: entry-level accounting jobs in North Carolina
- Filters out senior roles
- Filters out irrelevant jobs (non-accounting)
- Resolves Indeed/LinkedIn/ZipRecruiter URLs to direct ATS URLs via Serper
- Validates every URL for liveness, specificity, and quality before storing
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

# ─── Classification Constants ─────────────────────────────────────────────────

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
    "rippling.com", "kronos.net", "adp.com",
    "ceridian.com", "silkroad.com", "cornerstone", "sap.com",
]

AGGREGATORS = [
    "indeed.com", "linkedin.com", "ziprecruiter.com", "glassdoor.com",
    "simplyhired.com", "monster.com", "careerbuilder.com", "lensa.com",
    "talent.com", "joblist.com", "builtin.com", "wellfound.com",
    "dice.com", "adzuna.com", "talentify.io", "jobright.ai",
    "tealhq.com", "jooble.org", "snagajob.com", "salary.com",
    "careerjet.com", "whatjobs.com", "wayup.com", "bandana.com",
    "recruit.net", "jobs2careers.com", "learn4good.com",
    "neuvoo.com", "jobrapido.com"
]

GENERIC_URL_ENDINGS = [
    "/careers", "/careers/", "/jobs", "/jobs/", "/internships",
    "/internships/", "/career-opportunities", "/career-opportunities/",
    "/work-with-us", "/work-with-us/", "/join-us", "/join-us/",
    "/job-search", "/openings", "/openings/", "/join-our-team",
    "/join-our-team/", "/about-royal/careers/internships",
    "/about-your-bank/work-with-us/careers/students.html",
]

# ─── URL Quality Signal Lists ─────────────────────────────────────────────────

DEAD_SIGNALS = [
    "job not found", "position not found", "no longer available",
    "position has been filled", "job expired", "no longer accepting",
    "posting has closed", "job has been removed", "this job has expired",
    "this position has been filled", "this posting has expired",
    "job listing has expired", "no longer accepting applications",
    "this job is closed", "this role has been filled",
    "this position is no longer", "application closed",
    "recruitment closed", "vacancy closed",
    "this opportunity has closed", "job is no longer available",
    "page not found", "404 not found", "job not available", "position closed",
]

LIVE_SIGNALS = [
    "apply now", "submit application", "apply for this job",
    "apply for this position", "apply for this role", "start application",
    "begin application", "apply today", "apply online",
    "submit your application", "apply here",
]

GENERIC_PAGE_SIGNALS = [
    "search jobs", "filter jobs", "all open positions", "browse jobs",
    "view all jobs", "see all openings", "explore careers",
    "find your next role", "job search results",
]


# ─── Filters ──────────────────────────────────────────────────────────────────

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


# ─── URL Helpers ──────────────────────────────────────────────────────────────

def is_aggregator(url: str) -> bool:
    if not url:
        return False
    return any(agg in url.lower() for agg in AGGREGATORS)


def is_ats_url(url: str) -> bool:
    if not url:
        return False
    return any(domain in url.lower() for domain in ATS_DOMAINS)


def is_generic_url(url: str) -> bool:
    """Returns True if the URL looks like a careers homepage, not a specific listing."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/").lower()
    for ending in GENERIC_URL_ENDINGS:
        if path.endswith(ending.rstrip("/")):
            return True
    # Specific jobs almost always have an ID, slug, or longer path
    segments = [s for s in path.split("/") if s]
    if len(segments) <= 1 and not parsed.query:
        return True
    return False


def clean_url(url: str) -> str:
    """Strip tracking parameters from a URL."""
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


# ─── URL Quality Checker ──────────────────────────────────────────────────────

def check_url_quality(url: str) -> dict:
    """
    Returns {"is_active": bool, "reason": str}.

    Steps:
      1. Reject generic career homepages immediately (no HTTP call).
      2. Fast HEAD check — drop 4xx responses early.
      3. GET the page — scan for dead/generic/live signals in page content.
    """
    if is_generic_url(url):
        return {"is_active": False, "reason": "Generic career page — not a specific listing"}

    # Step 1: HEAD check
    try:
        head = httpx.head(url, follow_redirects=True, timeout=10, headers=HEADERS)
        if head.status_code in (400, 403, 404, 410):
            return {"is_active": False, "reason": f"HTTP {head.status_code}"}
    except httpx.HTTPError as e:
        return {"is_active": False, "reason": f"HEAD request failed: {e}"}

    # Step 2: GET + content scan
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=15, headers=HEADERS)
        content = resp.text.lower()

        for signal in DEAD_SIGNALS:
            if signal in content:
                return {"is_active": False, "reason": f"Dead signal: '{signal}'"}

        generic_count = sum(1 for s in GENERIC_PAGE_SIGNALS if s in content)
        if generic_count >= 2:
            return {"is_active": False, "reason": f"Generic listing page ({generic_count} signals)"}

        if any(s in content for s in LIVE_SIGNALS):
            return {"is_active": True, "reason": "Live signal confirmed"}

        # No dead signals, but no live signal either — cautiously accept for review
        return {"is_active": True, "reason": "No dead signals (unconfirmed — review recommended)"}

    except httpx.HTTPError as e:
        return {"is_active": False, "reason": f"GET request failed: {e}"}


def resolve_and_validate(url: str, label: str) -> str | None:
    """
    Clean the URL, run the full quality check, and return it if alive.
    Returns None if it fails any check so the job is skipped entirely.
    """
    if not url:
        return None
    cleaned = clean_url(url)
    result = check_url_quality(cleaned)
    if result["is_active"]:
        print(f"  ✅ [{label}] {cleaned}  ({result['reason']})")
        return cleaned
    else:
        print(f"  ⚠️  [{label}] REJECTED — {result['reason']}")
        return None


# ─── Serper Lookup ────────────────────────────────────────────────────────────

def build_search_query(title: str, company: str, location: str) -> str:
    parts = [title.strip()]
    if company and company.lower() != "nan":
        parts.append(company.strip())
    if location and location.lower() != "nan":
        parts.append(f"Jobs in {location.strip()}")
    return " ".join(parts)


def find_apply_url(title: str, company: str, location: str) -> str | None:
    """
    Search Serper for '<title> <company> Jobs in <location>'.
    Returns the first non-aggregator result from the top 5, or None.
    Does NOT validate quality here — let resolve_and_validate handle that.
    """
    query = build_search_query(title, company, location)

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
        data = resp.json()
        results = data.get("organic", [])

        print(f"\n  🔍 Serper: {query}")
        for i, r in enumerate(results[:10], 1):
            print(f"     {i}. {r.get('title')}")
            print(f"        {r.get('link')}")

        for result in results[:10]:
            link = result.get("link", "")
            if not link or is_aggregator(link):
                continue
            # Return the raw URL — validation happens in resolve_and_validate
            return link

    except httpx.HTTPError as e:
        print(f"  [Serper] Error for '{query}': {e}")

    return None


# ─── Main Pipeline ────────────────────────────────────────────────────────────

def run():
    seen_urls: set[str] = set()
    all_jobs: list[dict] = []

    total_raw = 0
    skipped_senior = 0
    skipped_irrelevant = 0
    skipped_duplicate = 0
    skipped_no_url = 0
    urls_found = 0
    urls_rejected = 0

    print(f"Scraping {len(QUERIES)} titles × {len(LOCATIONS)} locations...\n")

    for location in LOCATIONS:
        for query in QUERIES:
            print(f"\n{'─' * 60}")
            print(f"  Scraping: '{query}' in {location}")
            print(f"{'─' * 60}")

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
                print(f"  ERROR scraping '{query}' @ {location}: {e}")
                continue

            if df is None or df.empty:
                print(f"  No results returned.")
                continue

            total_raw += len(df)

            for _, row in df.iterrows():
                title    = str(row.get("title",    "")).strip()
                company  = str(row.get("company",  "")).strip()
                job_url  = str(row.get("job_url",  "")).strip()
                job_loc  = str(row.get("location", "")).strip()

                # ── Basic sanity ──────────────────────────────────────────────
                if not title or not job_url or job_url == "nan":
                    continue

                # ── Dedup by source URL ───────────────────────────────────────
                if job_url in seen_urls:
                    skipped_duplicate += 1
                    continue
                seen_urls.add(job_url)

                print(f"\n  [{title}] @ {company} ({job_loc})")

                # ── Role filters ──────────────────────────────────────────────
                if not is_accounting_role(title):
                    print(f"  ⏭️  Skipped — not an accounting role")
                    skipped_irrelevant += 1
                    continue

                if not is_entry_level(title):
                    print(f"  ⏭️  Skipped — senior/lead title")
                    skipped_senior += 1
                    continue

                # ── URL resolution + validation ───────────────────────────────
                apply_url: str | None = None

                if is_ats_url(job_url) and not is_generic_url(job_url):
                    # Already a direct ATS link — still validate it
                    apply_url = resolve_and_validate(job_url, "direct ATS")

                elif any(agg in job_url.lower() for agg in ["linkedin.com", "indeed.com", "ziprecruiter.com"]):
                    # Aggregator link — look up a real ATS URL via Serper
                    raw = find_apply_url(title, company, job_loc)
                    apply_url = resolve_and_validate(raw, "Serper → aggregator") if raw else None

                else:
                    # Unknown domain — try Serper first, then validate
                    raw = find_apply_url(title, company, job_loc)
                    apply_url = resolve_and_validate(raw, "Serper fallback") if raw else None

                # ── Only store jobs with a clean, validated URL ───────────────
                if apply_url:
                    urls_found += 1
                    all_jobs.append({
                        "title":   title,
                        "company": company,
                        "location": job_loc,
                        "url":     apply_url,
                    })
                else:
                    print(f"  ❌ Skipping — no usable apply URL found")
                    urls_rejected += 1
                    skipped_no_url += 1

            time.sleep(random.uniform(1, 3))

    # ─── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"  Raw jobs scraped:          {total_raw}")
    print(f"  Skipped (duplicate):       {skipped_duplicate}")
    print(f"  Skipped (not accounting):  {skipped_irrelevant}")
    print(f"  Skipped (senior title):    {skipped_senior}")
    print(f"  Skipped (no valid URL):    {skipped_no_url}")
    print(f"  ─────────────────────────────")
    print(f"  Jobs stored (clean URLs):  {urls_found}")
    print(f"  URLs rejected by checker:  {urls_rejected}")
    print(f"{'=' * 60}\n")

    # ─── Final Output ──────────────────────────────────────────────────────────
    print("FINAL RESULTS\n" + "=" * 60)
    for job in all_jobs:
        print(f"  {job['title']} @ {job['company']}")
        print(f"  {job['location']}")
        print(f"  {job['url']}")
        print(f"  {'-' * 40}")


if __name__ == "__main__":
    run()