"""
pipeline_js.py
JobSpy pipeline: entry-level accounting jobs in North Carolina

URL Acceptance Architecture (whitelist-first):
  A URL is only kept if it passes the ACCEPTANCE GATE:
    → Known ATS domain, OR company name tokens found in the URL domain

  URLs that pass the gate then go through SECONDARY FILTERS:
    → Blocked extensions, blocked domains, aggregator check,
      generic URL endings, ATS-specific checks, HTTP liveness check

  This means we never store a URL from an unknown domain that has
  no verifiable connection to the hiring company.
"""

import os
import re
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
    "Durham, NC",
    "Greensboro, NC",
    "Winston-Salem, NC",
]

VALID_LOCATION_KEYWORDS = [
    "nc", "north carolina", "sc", "south carolina",
    "charlotte", "mooresville", "concord", "gastonia",
    "huntersville", "matthews", "fort mill", "rock hill",
    "kannapolis", "salisbury", "monroe", "albemarle",
    "hickory", "statesville", "davidson", "cornelius",
    "raleigh", "durham", "greensboro", "winston-salem",
    "cary", "fayetteville", "wilmington", "high point",
    "asheville", "chapel hill", "burlington", "rocky mount",
    "wilson", "goldsboro", "jacksonville", "apex", "morrisville",
    "sanford", "asheboro", "kernersville",
]

# ─── Classification Constants ─────────────────────────────────────────────────

ACCOUNTING_KEYWORDS = [
    "account", "accountant", "accounting", "bookkeep", "payroll",
    "audit", "tax", "billing", "budget", "controller", "cpa", "cma",
    "accounts payable", "accounts receivable", "gl ", "general ledger",
    "cost analyst", "revenue", "treasury", "fiscal", "ledger", "invoic",
]

# Titles that superficially match ACCOUNTING_KEYWORDS but are NOT accounting roles.
# Checked after keyword match — if any appear in the title, the job is dropped.
NON_ACCOUNTING_TITLES = [
    "account executive",        # sales
    "account manager",          # sales / client success
    "account associate",        # sales / insurance
    "account representative",   # sales
    "account director",         # sales
    "sales account",            # sales
    "quality assurance",        # QA / manufacturing
    "qa auditor",               # QA / manufacturing
    "quality auditor",          # QA / manufacturing
    "night auditor",            # hospitality
    "revenue cycle",            # healthcare billing — not pure accounting
    "insurance",                # insurance sales / underwriting
]

SENIOR_TITLE_KEYWORDS = [
    "senior", " sr ", "sr.", " sr,", "(sr)", "sr-", "principal", "director",
    "manager", "head of", "vp ", "vice president", "chief", "executive",
    "supervisor", "lead ", " iii", " iv", " v ", " ii", " 2", " 3", " 4", " 5",
    # C-suite abbreviations — "chief" catches the word but not these abbreviations
    "cfo", "ceo", "coo", "cto", "cpo",
    # Fractional roles are always senior hires
    "fractional",
]

# ─── ATS Domain Whitelist ─────────────────────────────────────────────────────
# These are the only third-party domains we trust unconditionally.
# Any URL NOT on this list must pass the company name check instead.

ATS_DOMAINS = [
    "greenhouse.io", "lever.co", "workday.com", "myworkdayjobs.com",
    "ashbyhq.com", "smartrecruiters.com", "jobvite.com", "icims.com",
    "taleo.net", "successfactors.com", "applytojob.com", "bamboohr.com",
    "paylocity.com", "breezy.hr", "avature.net", "recruitingbypaycor.com",
    "ultipro.com", "oraclecloud.com", "workable.com", "recruitee.com",
    "pinpointhq.com", "dover.com", "careerplug.com", "jazz.co",
    "rippling.com", "kronos.net", "adp.com", "ceridian.com",
    "silkroad.com", "cornerstone", "sap.com", "eightfold.ai",
    "isolvedhire.com", "csod.com",
]

# ─── Aggregators ─────────────────────────────────────────────────────────────
# Checked FIRST inside the acceptance gate — before company name matching —
# so a token collision (e.g. "Graham" → grahamjobs.com) can never smuggle
# a staffing firm or job board through.

AGGREGATORS = [
    # Major job boards
    "indeed.com", "linkedin.com", "ziprecruiter.com", "glassdoor.com",
    "simplyhired.com", "monster.com", "careerbuilder.com", "lensa.com",
    "talent.com", "joblist.com", "builtin.com", "wellfound.com",
    "dice.com", "adzuna.com", "talentify.io", "jobright.ai",
    "tealhq.com", "jooble.org", "snagajob.com", "salary.com",
    "careerjet.com", "whatjobs.com", "wayup.com", "bandana.com",
    "recruit.net", "jobs2careers.com", "learn4good.com",
    "neuvoo.com", "jobrapido.com",
    # Caught across runs
    "jobs.chronicle.com", "tallo.com", "jobleads.com",
    "entertainmentcareers.net", "jobilize.com", "myjobhelper.com",
    "jobs.accaglobal.com", "higheredjobs.com",
    "joinhandshake.com", "app.joinhandshake.com",
    "showbizjobs.com", "earnbetter.com",
    "jobs.appcast.io",
    "careers.insidehighered.com",   # niche job board caught in run 1
    # Staffing firms
    "talentbridge.com", "accruepartners.com", "insightglobal.com",
    "element-staffing.com",
    "jobs.vaco.com", "roberthalf.com", "adecco.com", "manpower.com",
    "randstad.com", "kforce.com", "apexgroup.com", "staffmark.com",
    "aerotek.com", "heidrick.com", "michaelpage.com", "spencerstuart.com",
    "jobot.com",                    # staffing firm caught in run 1
    "jobs.grahamjobs.com",          # staffing firm caught in run 1
    "grahamjobs.com",
]

# ─── Secondary Filter: Blocked Extensions ────────────────────────────────────

BLOCKED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg", ".xls", ".xlsx",
    ".ppt", ".pptx", ".csv", ".zip",
}

# ─── Secondary Filter: Blocked Domains ───────────────────────────────────────

BLOCKED_DOMAINS = {
    # Document hosting
    "issuu.com", "scribd.com", "docs.google.com", "drive.google.com",
    "dropbox.com",
    # Social / video / blogs
    "facebook.com", "twitter.com", "x.com", "instagram.com",
    "youtube.com", "reddit.com", "medium.com", "substack.com",
    # Encyclopedia / reference
    "wikipedia.org",
    # Government archives / non-employer sites caught in runs
    "ijglobal.com", "jamaicabobsleigh.org", "townofdavidson.org",
    "docs.daviecountync.gov",
}

# ─── Secondary Filter: Generic URL Endings ───────────────────────────────────

GENERIC_URL_ENDINGS = [
    "/careers", "/jobs", "/internships", "/career-opportunities",
    "/work-with-us", "/join-us", "/job-search", "/openings",
    "/join-our-team", "/job-opportunities", "/internship-program",
    "/early-career", "/students", "/apply",
    "/about-royal/careers/internships",
    "/about-your-bank/work-with-us/careers/students.html",
    "/current-openings",
]

# ─── Content Signal Lists ─────────────────────────────────────────────────────

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

# ─── Company Name Normalization ───────────────────────────────────────────────

# Words that appear in company names but never in domain names
COMPANY_NAME_NOISE = {
    "inc", "llc", "ltd", "corp", "corporation", "company", "companies",
    "group", "usa", "us", "the", "and", "solutions", "services",
    "associates", "partners", "co", "international", "global",
    "holdings", "enterprises", "technologies", "technology",
    "consulting", "management", "resources", "staffing", "systems",
}


def normalize_company_tokens(company: str) -> list[str]:
    """
    Break a company name into domain-matchable tokens.

    Examples:
      "A. O. Smith Corporation"         → ["smith", "ao", "aosmith"]
      "Lowe's Companies, Inc."          → ["lowes"]
      "Compass Group USA"               → ["compass"]
      "Johnson C. Smith University"     → ["johnson", "smith", "university"]
      "UNC Charlotte"                   → ["unc", "charlotte", "unccharlotte"]
    """
    # Remove punctuation, lowercase
    cleaned = re.sub(r"[^\w\s]", "", company.lower())
    # Split and filter noise + very short tokens
    tokens = [t for t in cleaned.split() if t not in COMPANY_NAME_NOISE and len(t) > 2]
    # Add a joined version of the first two tokens for "aosmith" style domains
    if len(tokens) >= 2:
        tokens.append(tokens[0] + tokens[1])
    return tokens


# ─── Role Filters ─────────────────────────────────────────────────────────────

def is_accounting_role(title: str) -> bool:
    title_lower = title.lower()
    # Must match at least one accounting keyword
    if not any(kw in title_lower for kw in ACCOUNTING_KEYWORDS):
        return False
    # Must NOT match any known non-accounting title pattern
    if any(excl in title_lower for excl in NON_ACCOUNTING_TITLES):
        return False
    return True


def is_entry_level(title: str) -> bool:
    title_lower = title.lower().strip()
    for kw in SENIOR_TITLE_KEYWORDS:
        if kw in title_lower:
            return False
    if title_lower.startswith("sr ") or title_lower.startswith("sr."):
        return False
    return True


# ─── Acceptance Gate ──────────────────────────────────────────────────────────

def is_ats_url(url: str) -> bool:
    if not url:
        return False
    return any(domain in url.lower() for domain in ATS_DOMAINS)


def is_aggregator(url: str) -> bool:
    if not url:
        return False
    return any(agg in url.lower() for agg in AGGREGATORS)


def company_name_in_domain(url: str, company: str) -> bool:
    """
    Returns True if any normalized token from the company name
    appears in the URL's domain.

    e.g. company="Lowe's Companies Inc", url="talent.lowes.com/..."
         tokens=["lowes"] → "lowes" in "talent.lowes.com" → True
    """
    if not company or company.lower() == "nan":
        return False
    domain = urlparse(url).netloc.lower().replace("www.", "")
    tokens = normalize_company_tokens(company)
    return any(token in domain for token in tokens)


def passes_acceptance_gate(url: str, company: str) -> tuple[bool, str]:
    """
    PRIMARY GATE — a URL must pass this before any secondary filters run.
    Returns (True, reason) if accepted, (False, reason) if rejected.

    Order of checks:
      1. Aggregators are rejected unconditionally — BEFORE company name matching
         so a token collision (e.g. "Graham" → grahamjobs.com) can never
         smuggle a staffing firm or job board through the gate.
      2. Known ATS domain → accepted
      3. Company name token found in domain → accepted
      4. Everything else → rejected
    """
    if not url:
        return False, "Empty URL"

    # Check aggregators FIRST — before company name matching
    if is_aggregator(url):
        return False, "Aggregator/staffing firm domain"

    if is_ats_url(url):
        return True, "Known ATS domain"

    if company_name_in_domain(url, company):
        tokens = normalize_company_tokens(company)
        domain = urlparse(url).netloc.lower()
        matched = [t for t in tokens if t in domain]
        return True, f"Company token(s) {matched} found in domain"

    return False, "Domain is neither a known ATS nor matches company name"


# ─── Secondary Filters ────────────────────────────────────────────────────────

def has_blocked_extension(url: str) -> bool:
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in BLOCKED_EXTENSIONS)


def is_blocked_domain(url: str) -> bool:
    domain = urlparse(url).netloc.lower().replace("www.", "")
    return domain in BLOCKED_DOMAINS


def is_generic_url(url: str) -> bool:
    """
    Returns True if the URL looks like a careers homepage, not a specific listing.

    Rule (validated against all clean URLs across runs):
      A real job listing always has EITHER:
        - 2+ path segments  (e.g. /jobs/16277, /landdesign/jobs/4567383006)
        - OR a query string containing a job identifier (e.g. ?job=744000093554715)

      Special case: Lever URLs need 3+ segments because the 2-segment form
      (jobs.lever.co/company) is just a company page with no specific listing.

      Generic search param: URLs with ?search= and no job identifier param
      are search results pages, not specific listings.
    """
    parsed = urlparse(url)
    path = parsed.path.rstrip("/").lower()
    params = parse_qs(parsed.query)

    # Check known generic path endings first
    for ending in GENERIC_URL_ENDINGS:
        if path.endswith(ending.rstrip("/")):
            return True

    # ?search= with no job identifier → generic search results page
    JOB_ID_PARAMS = {"jobId", "job", "gh_jid", "id", "jobid", "job_id", "currentJobId"}
    if "search" in params and not any(k in params for k in JOB_ID_PARAMS):
        return True

    segments = [s for s in path.split("/") if s]

    # No segments and no query → bare domain or careers root
    if len(segments) <= 1 and not parsed.query:
        return True

    # Lever: /company is a company page, /company/job-uuid is a real listing
    if len(segments) == 2 and "lever.co" in parsed.netloc and not parsed.query:
        return True

    return False


def is_adp_generic_url(url: str) -> bool:
    """
    ADP's workforcenow platform puts everything in query params instead of
    the path, so the standard segment check can't distinguish a real listing
    from a career center homepage.

    Real listing:  ?cid=UUID&jobId=526729              ← jobId present
    Career center: ?cid=UUID&selectedMenuKey=CareerCenter  ← no jobId

    jobId is only appended by ADP when the user is on a specific job page —
    it is never present on search results, homepages, or career centers.
    """
    if "workforcenow.adp.com" not in url.lower():
        return False  # not an ADP URL — not our concern
    params = parse_qs(urlparse(url).query)
    return "jobId" not in params


def passes_secondary_filters(url: str) -> tuple[bool, str]:
    """
    SECONDARY FILTERS — run only on URLs that already passed the acceptance gate.
    Returns (True, "") if all pass, (False, reason) on first failure.
    """
    if has_blocked_extension(url):
        return False, "Blocked file extension"

    if is_blocked_domain(url):
        return False, "Blocked domain"

    if is_aggregator(url):
        return False, "Aggregator domain"

    if is_generic_url(url):
        return False, "Generic careers page — not a specific listing"

    if is_adp_generic_url(url):
        return False, "ADP URL missing jobId — career center page, not a specific listing"

    return True, ""


# ─── URL Helpers ──────────────────────────────────────────────────────────────

def clean_url(url: str) -> str:
    """Strip tracking parameters from a URL."""
    tracking_params = {
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "src", "source", "sourceType", "gh_src", "trk", "refId", "lever-source",
        # ATS locale/display params that don't affect the job being shown
        "c", "lang", "lang[0]", "lang[1]", "locale", "ccId",
    }
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    clean_params = {k: v for k, v in params.items() if k not in tracking_params}
    clean_query = urlencode({k: v[0] for k, v in clean_params.items()})
    return parsed._replace(query=clean_query).geturl()


def is_valid_location(loc: str) -> bool:
    """Returns True if the location string is within the target area."""
    if not loc or loc.lower() == "nan":
        return False
    loc_lower = loc.lower()
    return any(kw in loc_lower for kw in VALID_LOCATION_KEYWORDS)


# ─── HTTP Quality Check ───────────────────────────────────────────────────────

def check_url_liveness(url: str) -> dict:
    """
    Returns {"is_active": bool, "reason": str}.
    Runs only after a URL has passed both the acceptance gate
    and all secondary filters — so this is purely about liveness.

    Steps:
      1. HEAD check — drop 4xx early
      2. GET + content scan for dead/generic/live signals
    """
    # Step 1: HEAD
    try:
        head = httpx.head(url, follow_redirects=True, timeout=10, headers=HEADERS)
        if head.status_code in (400, 403, 404, 410):
            return {"is_active": False, "reason": f"HTTP {head.status_code}"}
    except httpx.HTTPError as e:
        return {"is_active": False, "reason": f"HEAD request failed: {e}"}

    # Step 2: GET + signal scan
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

        return {"is_active": True, "reason": "No dead signals (unconfirmed — review recommended)"}

    except httpx.HTTPError as e:
        return {"is_active": False, "reason": f"GET request failed: {e}"}


def full_url_check(url: str, company: str, label: str) -> str | None:
    """
    Runs the complete validation pipeline on a single URL:
      1. Clean tracking params
      2. Acceptance gate  (aggregator check → ATS domain → company name in domain)
      3. Secondary filters (extensions, blocked domains, aggregators,
         generic endings, ATS-specific checks)
      4. HTTP liveness check

    Returns the cleaned URL if it passes everything, None otherwise.
    """
    if not url:
        return None

    cleaned = clean_url(url)

    # Gate 1: Acceptance
    accepted, reason = passes_acceptance_gate(cleaned, company)
    if not accepted:
        print(f"  🚫 [{label}] GATE REJECTED — {reason}")
        return None

    # Gate 2: Secondary filters
    passed, reason = passes_secondary_filters(cleaned)
    if not passed:
        print(f"  ⚠️  [{label}] FILTER REJECTED — {reason}")
        return None

    # Gate 3: Liveness
    result = check_url_liveness(cleaned)
    if result["is_active"]:
        print(f"  ✅ [{label}] {cleaned}  ({result['reason']})")
        return cleaned
    else:
        print(f"  ⚠️  [{label}] DEAD — {result['reason']}")
        return None


# ─── Serper Lookup ────────────────────────────────────────────────────────────

def build_search_query(title: str, company: str, location: str) -> str:
    """
    Build a Serper query biased toward application pages.
    Adding "apply" pushes results toward ATS pages over news/archives.
    """
    parts = [title.strip()]
    if company and company.lower() != "nan":
        parts.append(company.strip())
    parts.append("apply")
    if location and location.lower() != "nan":
        parts.append(location.strip())
    return " ".join(parts)


def find_apply_url(title: str, company: str, location: str) -> str | None:
    """
    Search Serper and return the first result that passes the acceptance gate.
    Secondary filters and liveness are handled by full_url_check — not here.
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
            if not link:
                continue

            # Pre-screen each Serper result through the acceptance gate
            # before spending an HTTP call on it
            accepted, reason = passes_acceptance_gate(link, company)
            if not accepted:
                print(f"     ⛔ {reason} — {link}")
                continue

            return link

    except httpx.HTTPError as e:
        print(f"  [Serper] Error for '{query}': {e}")

    return None


# ─── Main Pipeline ────────────────────────────────────────────────────────────

def run():
    seen_urls: set[str] = set()
    seen_jobs: set[tuple[str, str]] = set()  # (normalized_title, normalized_company)
    all_jobs: list[dict] = []

    total_raw          = 0
    skipped_dup        = 0
    skipped_irrelevant = 0
    skipped_senior     = 0
    skipped_location   = 0
    skipped_no_url     = 0
    urls_found         = 0
    urls_rejected      = 0

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
                title   = str(row.get("title",    "")).strip()
                company = str(row.get("company",  "")).strip()
                job_url = str(row.get("job_url",  "")).strip()
                job_loc = str(row.get("location", "")).strip()

                # ── Basic sanity ──────────────────────────────────────────────
                if not title or not job_url or job_url == "nan":
                    continue

                # ── Company nan guard ─────────────────────────────────────────
                # pandas fills missing company fields with NaN which becomes
                # the string "nan" after str(). A job with no company name
                # cannot be verified and should never be stored.
                if not company or company.lower() == "nan":
                    print(f"  ⏭️  Skipped — no company name")
                    skipped_irrelevant += 1
                    continue

                # ── Source URL dedup ──────────────────────────────────────────
                if job_url in seen_urls:
                    skipped_dup += 1
                    continue
                seen_urls.add(job_url)

                print(f"\n  [{title}] @ {company} ({job_loc})")

                # ── Location guard ────────────────────────────────────────────
                if not is_valid_location(job_loc):
                    print(f"  ⏭️  Skipped — location out of target area: '{job_loc}'")
                    skipped_location += 1
                    continue

                # ── Role filters ──────────────────────────────────────────────
                if not is_accounting_role(title):
                    print(f"  ⏭️  Skipped — not an accounting role")
                    skipped_irrelevant += 1
                    continue

                if not is_entry_level(title):
                    print(f"  ⏭️  Skipped — senior/lead title")
                    skipped_senior += 1
                    continue

                # ── Title + company dedup (catches same job from two sources) ─
                job_key = (title.lower().strip(), company.lower().strip())
                if job_key in seen_jobs:
                    print(f"  ⏭️  Skipped — same title+company already stored")
                    skipped_dup += 1
                    continue
                seen_jobs.add(job_key)

                # ── URL resolution ────────────────────────────────────────────
                # If it's already an ATS or company URL, use it directly.
                # Otherwise send to Serper to find the real apply URL.
                raw_url: str | None = None

                accepted, _ = passes_acceptance_gate(job_url, company)
                if accepted:
                    raw_url = job_url
                else:
                    # Aggregator or unknown domain — look up via Serper
                    raw_url = find_apply_url(title, company, job_loc)

                # ── Full validation pipeline ──────────────────────────────────
                label = "direct" if raw_url == job_url else "Serper"
                apply_url = full_url_check(raw_url, company, label) if raw_url else None

                # ── Resolved URL dedup ────────────────────────────────────────
                if apply_url:
                    if apply_url in seen_urls:
                        print(f"  ⏭️  Skipped — resolved URL already stored")
                        skipped_dup += 1
                        continue
                    seen_urls.add(apply_url)
                    urls_found += 1
                    all_jobs.append({
                        "title":    title,
                        "company":  company,
                        "location": job_loc,
                        "url":      apply_url,
                    })
                else:
                    print(f"  ❌ Skipping — no usable apply URL found")
                    urls_rejected += 1
                    skipped_no_url += 1

            time.sleep(random.uniform(1, 3))

    # ─── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"  Raw jobs scraped:            {total_raw}")
    print(f"  Skipped (duplicate):         {skipped_dup}")
    print(f"  Skipped (not accounting):    {skipped_irrelevant}")
    print(f"  Skipped (senior title):      {skipped_senior}")
    print(f"  Skipped (location):          {skipped_location}")
    print(f"  Skipped (no valid URL):      {skipped_no_url}")
    print(f"  ─────────────────────────────")
    print(f"  Jobs stored (clean URLs):    {urls_found}")
    print(f"  URLs rejected by checker:    {urls_rejected}")
    print(f"{'=' * 60}\n")

    # ─── Final Output ─────────────────────────────────────────────────────────
    print("FINAL RESULTS\n" + "=" * 60)
    for job in all_jobs:
        print(f"  {job['title']} @ {job['company']}")
        print(f"  {job['location']}")
        print(f"  {job['url']}")
        print(f"  {'-' * 40}")


if __name__ == "__main__":
    run()