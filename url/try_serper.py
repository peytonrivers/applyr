"""
pipeline_serper_test.py
Two-pass Serper pipeline: entry-level accounting jobs in North Carolina

Pass 1 — Job Discovery:
  Uses Serper's Google Jobs endpoint (type="jobs") to find listings.
  Each query returns structured job data: title, company, location, snippet.

Pass 2 — URL Resolution:
  For every job that passes filtering, runs a second Serper organic search
  to find the direct ATS apply URL — same logic as serper_find_apply_url
  in the existing pipeline_js.py.

Filtering stack is identical to pipeline_js.py:
  → Role check, senior check, location check, title+company dedup
  → is_valid_url (ATS whitelist + company token match)
  → title_matches_url (slug seniority + mismatch detection)
  → check_url_quality (dead signals, English, apply button, staffing)
"""

import os
import re
import time
import random
import httpx
from urllib.parse import urlparse
from dotenv import load_dotenv
from langdetect import detect, LangDetectException, DetectorFactory

DetectorFactory.seed = 0
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

# ─── Discovery Queries ────────────────────────────────────────────────────────
# Fewer, broader queries than JobSpy — Google Jobs aggregates well enough
# that you don't need 19 variants to get coverage.

QUERIES = [
    "entry level accountant",
    "staff accountant",
    "accounting associate",
    "accounts payable specialist",
    "accounts receivable specialist",
    "bookkeeper",
    "payroll specialist",
    "billing specialist",
    "accounting clerk",
    "budget analyst",
    "cost accountant",
    "accounting intern",
]

LOCATION = "North Carolina"

# ─── Classification Constants (identical to pipeline_js.py) ──────────────────

ACCOUNTING_KEYWORDS = [
    "accountant", "accounting", "bookkeep", "payroll",
    "tax", "billing", "budget", "cpa", "cma",
    "accounts payable", "accounts receivable", "gl ", "general ledger",
    "cost analyst", "fiscal", "ledger", "invoic",
]

NON_ACCOUNTING_TITLES = [
    "account executive", "account manager", "account associate",
    "account representative", "account director", "sales account",
    "quality assurance", "qa auditor", "quality auditor",
    "night auditor", "revenue cycle", "insurance",
    "account operations", "it auditor", "faculty", "adjunct", "key account",
]

SENIOR_TITLE_KEYWORDS = [
    "senior", "sr", "sr ", "sr. ", " sr.", " sr ", "sr.", " sr,", "(sr)", "sr-",
    "principal", "director", "manager", "head of", "vp ", "vice president",
    "chief", "executive", "supervisor", "lead ", " iii", " iv", " v ", " ii",
    " 2", " 3", " 4", " 5", "midlevel", "mid-level", "avp", "suptrs",
    "cfo", "ceo", "coo", "cto", "cpo", "fractional", "controller",
    "seasonal", "part-time", "part time", "parttime", "temporary", "contract",
]

VALID_LOCATION_KEYWORDS = [
    "nc", "north carolina", "charlotte", "raleigh", "durham",
    "greensboro", "cary", "fayetteville", "wilmington", "asheville",
    "high point", "chapel hill",
]

# ─── ATS Domain Whitelist ─────────────────────────────────────────────────────

ATS_DOMAINS = [
    "greenhouse.io", "lever.co", "workday.com", "myworkdayjobs.com",
    "ashbyhq.com", "smartrecruiters.com", "jobvite.com", "icims.com",
    "taleo.net", "successfactors.com", "applytojob.com", "bamboohr.com",
    "paylocity.com", "breezy.hr", "avature.net", "recruitingbypaycor.com",
    "ultipro.com", "oraclecloud.com", "workable.com", "recruitee.com",
    "pinpointhq.com", "dover.com", "careerplug.com", "jazz.co",
    "rippling.com", "kronos.net", "adp.com", "ceridian.com",
    "dayforcehcm.com", "silkroad.com", "cornerstone", "sap.com",
    "eightfold.ai", "isolvedhire.com", "csod.com",
]

AGGREGATORS = [
    "indeed.com", "linkedin.com", "ziprecruiter.com", "glassdoor.com",
    "simplyhired.com", "monster.com", "careerbuilder.com", "lensa.com",
    "talent.com", "joblist.com", "builtin.com", "wellfound.com",
    "dice.com", "adzuna.com", "talentify.io", "jobright.ai",
    "tealhq.com", "jooble.org", "snagajob.com", "salary.com",
    "careerjet.com", "whatjobs.com", "wayup.com", "bandana.com",
    "recruit.net", "jobs2careers.com", "learn4good.com",
    "neuvoo.com", "jobrapido.com", "jobs.chronicle.com", "tallo.com",
    "jobleads.com", "entertainmentcareers.net", "jobilize.com",
    "myjobhelper.com", "jobs.accaglobal.com", "higheredjobs.com",
    "joinhandshake.com", "app.joinhandshake.com", "showbizjobs.com",
    "earnbetter.com", "jobs.appcast.io", "jobs.intuit.com",
    "www.hospitalityonline.com", "hospitalityonline.com", "bebee.com",
    "nextgenenergyjobs.com", "jobot.com", "talentbridge.com",
    "accruepartners.com", "insightglobal.com", "element-staffing.com",
    "jobs.vaco.com", "roberthalf.com", "adecco.com", "manpower.com",
    "randstad.com", "kforce.com", "apexgroup.com", "staffmark.com",
    "aerotek.com", "heidrick.com", "michaelpage.com", "spencerstuart.com",
    "astoncarter.com", "addisongroup.com", "getcrg.com", "grahamjobs.com",
    "lhh.com", "talentally.com", "accentuatestaffing.com", "ledgent.com",
    "vaia.com",
]

GENERIC_URL_ENDINGS = [
    "/careers", "/jobs", "/internships", "/career-opportunities",
    "/work-with-us", "/join-us", "/job-search", "/openings",
    "/join-our-team", "/job-opportunities", "/internship-program",
    "/early-career", "/students", "/current-openings",
]

JOB_ID_PATTERNS = [
    re.compile(r'\d{4,}'),
    re.compile(r'[A-Za-z0-9]{6,}[0-9][A-Za-z0-9]*'),
    re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
]

GENERIC_TITLE_WORDS = {
    "analyst", "accountant", "manager", "associate", "specialist",
    "coordinator", "director", "assistant", "officer", "lead",
    "senior", "junior", "staff", "remote", "job", "jobs", "careers",
    "work", "home", "from", "team", "global", "north", "south",
    "east", "west", "united", "states", "americas", "apply", "view",
    "detail", "posting", "opening", "position", "role", "opportunity",
    "clerk", "technician", "representative", "administrator",
}

SENIOR_URL_KEYWORDS = {
    "senior", "sr", "lead", "principal", "director", "vp", "head",
    "chief", "manager", "supervisor", "superintendent", "president",
    "controller",
}

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

APPLY_SIGNALS = [
    "apply now", "apply for this job", "apply for this position",
    "apply for this role", "apply today", "apply online",
    "submit your application", "apply here", "easy apply",
    "apply for this job online", "icims_applyonlinebutton",
    "apply to job", "apply-click", "top-apply",
    "applyonlinebutton", "apply-button", "applybutton", "apply-now",
    "data-apply", "applicationurl", "apply-link",
    "apply for this opportunity", "submit your resume",
    "apply", "apply to this position",
]

STAFFING_PAGE_SIGNALS = [
    "our client", "partnered with a", "partnering with a",
    "on behalf of our client", "representing multiple",
    "search managed by", "virtual recruiter", "jobot pro",
    "consultant careers", "current consultants",
    "staffing firm", "staffing agency", "direct placement firm",
    "recruiting firm", "placement firm", "serves thousands of clients",
    "employee type: contract", "this is a contract",
    "contract-to-hire", "contract to hire", "temp to hire",
    "temporary position", "staffing",
]

COMPANY_NAME_NOISE = {
    "inc", "llc", "ltd", "corp", "corporation", "company", "companies",
    "group", "usa", "us", "the", "and", "solutions", "services",
    "associates", "partners", "co", "international", "global",
    "holdings", "enterprises", "technologies", "technology",
    "consulting", "management", "resources", "staffing", "systems",
}

TRUSTED_ATS_BYPASS = ["workforcenow.adp.com", "adp.com"]


# ─── Helpers (identical to pipeline_js.py) ───────────────────────────────────

def normalize_company_tokens(company: str) -> list[str]:
    cleaned = re.sub(r"[^\w\s]", "", company.lower())
    tokens = [t for t in cleaned.split() if t not in COMPANY_NAME_NOISE and len(t) > 2]
    if len(tokens) >= 2:
        tokens.append(tokens[0] + tokens[1])
    return tokens


def is_accounting_role(title: str) -> bool:
    title_lower = title.lower()
    if any(kw in title_lower for kw in ACCOUNTING_KEYWORDS):
        if not any(excl in title_lower for excl in NON_ACCOUNTING_TITLES):
            return True
    return False


def is_senior_found(title: str) -> bool:
    title_lower = title.lower()
    return not any(kw in title_lower for kw in SENIOR_TITLE_KEYWORDS)


def is_nc_found(location: str) -> bool:
    if not location or location.lower() == "nan":
        return False
    return any(kw in location.lower() for kw in VALID_LOCATION_KEYWORDS)


def has_job_identifier(url: str) -> bool:
    parsed = urlparse(url)
    searchable = parsed.path + "?" + parsed.query
    return any(p.search(searchable) for p in JOB_ID_PATTERNS)


def is_generic_ending(url: str) -> bool:
    path = urlparse(url).path.rstrip("/").lower()
    return any(path.endswith(e.rstrip("/")) for e in GENERIC_URL_ENDINGS)


def is_specific_listing(url: str) -> bool:
    parsed = urlparse(url)
    segments = [s for s in parsed.path.split("/") if s]
    if len(segments) <= 1:
        return False
    if not has_job_identifier(url):
        return False
    if is_generic_ending(url):
        return False
    return True


def is_valid_url(url: str, company: str) -> bool:
    if any(agg in url.lower() for agg in AGGREGATORS):
        return False
    if not is_specific_listing(url):
        return False
    if any(domain in url.lower() for domain in ATS_DOMAINS):
        return True
    domain = urlparse(url).netloc.lower().replace("www.", "")
    tokens = normalize_company_tokens(company)
    return any(token in domain for token in tokens)


def _extract_slug_words(url: str) -> set[str]:
    path = urlparse(url).path.lower()
    segments = [s for s in path.split("/") if s]
    if not segments:
        return set()
    for segment in reversed(segments):
        segment = re.sub(r"\.\w{2,4}$", "", segment)
        words = re.split(r"[-_]", segment)
        alpha_words = [w for w in words if re.search(r"[a-z]{3,}", w)]
        if len(alpha_words) >= 2:
            return set(alpha_words)
    return set()


def title_matches_url(title: str, url: str) -> bool:
    slug_words = _extract_slug_words(url)
    if not slug_words:
        return True
    if slug_words & SENIOR_URL_KEYWORDS:
        print(f"  ⚠️  URL slug seniority: {slug_words & SENIOR_URL_KEYWORDS}")
        return False
    title_words = set(re.split(r"[\s\-_,]", title.lower()))
    slug_specific  = slug_words  - GENERIC_TITLE_WORDS
    title_specific = title_words - GENERIC_TITLE_WORDS
    if not slug_specific:
        return True
    if not (slug_specific & title_specific):
        print(f"  ⚠️  Mismatch — slug: {slug_specific} | title: {title_specific}")
        return False
    return True


def is_english_content(text: str, min_length: int = 50) -> bool:
    if not text or len(text.strip()) < min_length:
        return True
    try:
        return detect(text) == "en"
    except LangDetectException:
        return True


def check_url_quality(url: str) -> dict:
    try:
        head = httpx.head(url, follow_redirects=True, timeout=10, headers=HEADERS)
        if head.status_code in (400, 403, 404, 410):
            return {"is_active": False, "reason": f"HTTP {head.status_code}"}
    except httpx.HTTPError as e:
        return {"is_active": False, "reason": f"HEAD failed: {e}"}

    try:
        resp = httpx.get(url, follow_redirects=True, timeout=15, headers=HEADERS)
        content = resp.text.lower()

        for signal in DEAD_SIGNALS:
            if signal in content:
                return {"is_active": False, "reason": f"Dead signal: '{signal}'"}

        if not is_english_content(resp.text):
            detected = detect(resp.text) if resp.text.strip() else "unknown"
            return {"is_active": False, "reason": f"Non-English: '{detected}'"}

        is_trusted_ats = any(domain in url.lower() for domain in TRUSTED_ATS_BYPASS)
        if not is_trusted_ats and not any(s in content for s in APPLY_SIGNALS):
            return {"is_active": False, "reason": "No apply button found"}

        staffing_hits = [s for s in STAFFING_PAGE_SIGNALS if s in content]
        if len(staffing_hits) >= 2:
            return {"is_active": False, "reason": f"Staffing firm: {staffing_hits[:3]}"}

        return {"is_active": True, "reason": "Active listing confirmed"}

    except httpx.HTTPError as e:
        return {"is_active": False, "reason": f"GET failed: {e}"}


# ─── Pass 1: Serper Google Jobs Discovery ────────────────────────────────────

def serper_discover_jobs(query: str, location: str) -> list[dict]:
    """
    Hits Serper's regular Google Search endpoint to find job listings.

    Searches: "<query> jobs <location>" and pulls the top 10 organic results.
    Each result is a candidate job listing — title, link, and snippet are
    all available. We extract company/location from the snippet as best we
    can, then Pass 2 handles URL resolution.

    Returns a list of dicts with: title, company, location, url, snippet.
    """
    search_query = f"{query} jobs {location}"

    try:
        resp = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
            json={"q": search_query, "num": 10},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []

        # Pull from organic results
        for r in data.get("organic", []):
            title   = r.get("title", "").strip()
            link    = r.get("link", "").strip()
            snippet = r.get("snippet", "").strip()

            # Strip trailing site attribution from title (e.g. "Staff Accountant - Indeed")
            title = re.split(r"\s+[-|–]\s+", title)[0].strip()

            results.append({
                "title":    title,
                "company":  "",      # not reliably in organic results — Pass 2 resolves
                "location": location,
                "url":      link,
                "snippet":  snippet,
            })

        print(f"  Found {len(results)} organic results")
        return results

    except httpx.HTTPError as e:
        print(f"  [Serper Discovery] Error: {e}")
        return []


# ─── Pass 2: Serper URL Resolution ───────────────────────────────────────────

def serper_find_apply_url(title: str, company: str, location: str) -> str | None:
    """
    Runs a second Serper organic search to find the direct ATS apply URL.
    Identical logic to pipeline_js.py's serper_find_apply_url.
    """
    query = f"{title} {company} apply {location}"

    try:
        resp = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": 5},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("organic", [])

        print(f"  🔍 URL search: {query}")
        for i, r in enumerate(results[:5], 1):
            print(f"     {i}. {r.get('title')}")
            print(f"        {r.get('link')}")

        for result in results[:5]:
            link = result.get("link", "")
            if not link:
                continue
            if is_valid_url(link, company):
                return link
            print(f"     ⛔ rejected — {link}")

    except httpx.HTTPError as e:
        print(f"  [Serper URL] Error: {e}")

    return None


# ─── Main Pipeline ────────────────────────────────────────────────────────────

def run():
    seen_jobs: set[tuple[str, str]] = set()
    seen_urls: set[str] = set()
    all_jobs:  list[dict] = []

    total_discovered   = 0
    skipped_dup        = 0
    skipped_role       = 0
    skipped_senior     = 0
    skipped_location   = 0
    skipped_no_url     = 0
    skipped_url_title  = 0
    skipped_quality    = 0
    serper_calls       = 0   # track total API calls for cost visibility

    for query in QUERIES:
        print(f"\n{'─' * 60}")
        print(f"  PASS 1 — Discovery: {query!r} in {LOCATION}")
        print(f"{'─' * 60}")

        jobs = serper_discover_jobs(query, LOCATION)
        serper_calls += 1  # one call per discovery query

        if not jobs:
            print(f"  No results.")
            continue

        total_discovered += len(jobs)
        print(f"  Found {len(jobs)} listings from Google Jobs")

        for job in jobs:
            title    = job["title"]
            location = job["location"]
            raw_url  = job["url"]

            if not title:
                continue

            # Derive a best-guess company from the URL domain for token matching
            domain  = urlparse(raw_url).netloc.lower().replace("www.", "")
            company = domain.split(".")[0]  # rough — good enough for is_valid_url

            print(f"\n  {title!r} ({location})")
            print(f"  {raw_url}")

            # ── Role check ────────────────────────────────────────────────────
            if not is_accounting_role(title):
                print(f"  ⏭️  Not an accounting role")
                skipped_role += 1
                continue

            # ── Senior check ──────────────────────────────────────────────────
            if not is_senior_found(title):
                print(f"  ⏭️  Senior title")
                skipped_senior += 1
                continue

            # ── Title dedup (no company available, use title+url) ─────────────
            job_key = (title.lower(), raw_url.lower())
            if job_key in seen_jobs:
                print(f"  ⏭️  Already seen")
                skipped_dup += 1
                continue
            seen_jobs.add(job_key)

            # ── URL check: use raw if valid, else Pass 2 resolution ───────────
            if is_valid_url(raw_url, company):
                apply_url = raw_url
                print(f"  ✅ Direct URL accepted")
            else:
                print(f"  ⛔ Raw URL not valid — running Pass 2 resolution...")
                apply_url = serper_find_apply_url(title, company, location)
                serper_calls += 1
                if not apply_url:
                    print(f"  ❌ No valid URL found")
                    skipped_no_url += 1
                    continue

            # ── Title/URL match check ─────────────────────────────────────────
            if not title_matches_url(title, apply_url):
                print(f"  ❌ Title/URL mismatch")
                skipped_url_title += 1
                continue

            # ── Resolved URL dedup ────────────────────────────────────────────
            if apply_url in seen_urls:
                print(f"  ⏭️  URL already stored")
                skipped_dup += 1
                continue

            # ── Quality check ─────────────────────────────────────────────────
            quality = check_url_quality(apply_url)
            if not quality["is_active"]:
                print(f"  ❌ Quality check failed — {quality['reason']}")
                skipped_quality += 1
                continue

            print(f"  ✅ {quality['reason']}")
            seen_urls.add(apply_url)

            all_jobs.append({
                "title":    title,
                "company":  company,
                "location": location,
                "url":      apply_url,
            })
            print(f"  ✅ {apply_url}")

        time.sleep(random.uniform(0.5, 1.5))

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"  Total Serper API calls:       {serper_calls}")
    print(f"  Estimated cost:               ${serper_calls * 0.001:.4f}")
    print(f"  ─────────────────────────────────────")
    print(f"  Raw jobs discovered:          {total_discovered}")
    print(f"  Skipped (duplicate):          {skipped_dup}")
    print(f"  Skipped (role):               {skipped_role}")
    print(f"  Skipped (senior):             {skipped_senior}")
    print(f"  Skipped (location):           {skipped_location}")
    print(f"  Skipped (no valid URL):       {skipped_no_url}")
    print(f"  Skipped (title/URL mismatch): {skipped_url_title}")
    print(f"  Skipped (quality check):      {skipped_quality}")
    print(f"  {'─' * 35}")
    print(f"  Jobs stored (clean URLs):     {len(all_jobs)}")
    print(f"{'=' * 60}\n")

    print("FINAL RESULTS\n" + "=" * 60)
    for job in all_jobs:
        print(f"  {job['title']} @ {job['company']}")
        print(f"  {job['location']}")
        print(f"  {job['url']}")
        print(f"  {'-' * 40}")


if __name__ == "__main__":
    run()