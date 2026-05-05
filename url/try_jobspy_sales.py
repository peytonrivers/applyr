"""
pipeline_sales.py
JobSpy pipeline: entry-level sales jobs in North Carolina

URL Acceptance Architecture (whitelist-first):
  A URL is only kept if it passes the ACCEPTANCE GATE:
    → Known ATS domain, OR company name tokens found in the URL domain

  URLs that pass the gate then go through SECONDARY FILTERS:
    → Aggregator check, generic URL endings, job identifier check

  After a valid URL is found, the URL TITLE VALIDATOR runs:
    → Extracts the job-title slug from the URL path
    → Compares non-generic words against the scraped title
    → Rejects if there is zero specific-word overlap (mismatch)
    → Also rejects if the URL slug contains seniority keywords

  Finally, the URL QUALITY CHECK opens the page and verifies:
    → The listing is still active (no dead signals)
    → An apply button is present
    → The page shows no staffing firm signals

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
    # -------------------------
    # SALES CORE
    # -------------------------
    "sales associate",
    "entry level sales associate",
    "junior sales associate",
    "sales coordinator",
    "entry level sales coordinator",
    "junior sales coordinator",
    "sales analyst",
    "entry level sales analyst",
    "junior sales analyst",
    "sales intern",
    "sales assistant",
    "entry level sales assistant",
    "sales representative",
    "entry level sales representative",
    "junior sales representative",
    "sales graduate",
    "new grad sales",

    # -------------------------
    # ACCOUNT MANAGEMENT
    # -------------------------
    "account executive",
    "entry level account executive",
    "junior account executive",
    "account associate",
    "entry level account associate",
    "account coordinator",
    "entry level account coordinator",
    "account manager",
    "entry level account manager",
    "junior account manager",
    "account development representative",
    "entry level account development representative",

    # -------------------------
    # BUSINESS DEVELOPMENT
    # -------------------------
    "business development representative",
    "entry level business development representative",
    "junior business development representative",
    "bdr",
    "entry level bdr",
    "business development associate",
    "entry level business development associate",
    "business development analyst",
    "entry level business development analyst",
    "business development intern",
    "new business development",
    "entry level new business development",

    # -------------------------
    # SALES DEVELOPMENT
    # -------------------------
    "sales development representative",
    "entry level sales development representative",
    "junior sales development representative",
    "sdr",
    "entry level sdr",
    "inside sales representative",
    "entry level inside sales representative",
    "junior inside sales representative",
    "inside sales associate",
    "entry level inside sales associate",

    # -------------------------
    # RETAIL / B2C SALES
    # -------------------------
    "retail sales associate",
    "entry level retail sales associate",
    "retail sales coordinator",
    "entry level retail sales coordinator",
    "consumer sales representative",
    "entry level consumer sales representative",
    "direct sales representative",
    "entry level direct sales representative",

    # -------------------------
    # B2B / ENTERPRISE SALES
    # -------------------------
    "b2b sales representative",
    "entry level b2b sales representative",
    "enterprise sales associate",
    "entry level enterprise sales associate",
    "corporate sales associate",
    "entry level corporate sales associate",
    "commercial sales associate",
    "entry level commercial sales associate",
    "solutions sales associate",
    "entry level solutions sales associate",

    # -------------------------
    # TECH SALES / SAAS
    # -------------------------
    "tech sales representative",
    "entry level tech sales representative",
    "saas sales representative",
    "entry level saas sales representative",
    "software sales representative",
    "entry level software sales representative",
    "technology sales associate",
    "entry level technology sales associate",
    "saas account executive",
    "entry level saas account executive",

    # -------------------------
    # SALES OPERATIONS
    # -------------------------
    "sales operations analyst",
    "entry level sales operations analyst",
    "junior sales operations analyst",
    "sales ops analyst",
    "entry level sales ops analyst",
    "revenue operations analyst",
    "entry level revenue operations analyst",
    "junior revenue operations analyst",
    "sales support analyst",
    "entry level sales support analyst",
    "sales enablement analyst",
    "entry level sales enablement analyst",

    # -------------------------
    # INSURANCE SALES
    # -------------------------
    "insurance sales representative",
    "entry level insurance sales representative",
    "insurance sales associate",
    "entry level insurance sales associate",
    "insurance agent",
    "entry level insurance agent",
    "insurance sales intern",
    "life insurance sales representative",
    "entry level life insurance sales representative",
    "insurance sales coordinator",
    "entry level insurance sales coordinator",

    # -------------------------
    # CHANNEL / PARTNERSHIPS
    # -------------------------
    "channel sales associate",
    "entry level channel sales associate",
    "partnerships associate",
    "entry level partnerships associate",
    "partner development representative",
    "entry level partner development representative",
]

LOCATIONS = [
    "North Carolina",
    "NC",
]

VALID_LOCATION_KEYWORDS = [
    "nc", "north carolina", "charlotte", "raleigh",
    "durham", "greensboro", "cary", "fayetteville",
    "wilmington", "asheville", "high point", "chapel hill",
]

# ─── Classification Constants ─────────────────────────────────────────────────

ROLE_KEYWORDS = [
    "sales associate", "sales coordinator", "sales analyst",
    "sales representative", "sales assistant", "sales intern",
    "sales development", "sales operations", "sales ops",
    "sales enablement", "sales support",
    "account executive", "account associate", "account coordinator",
    "account manager", "account development",
    "business development representative", "bdr",
    "inside sales", "outside sales", "direct sales",
    "retail sales", "consumer sales", "b2b sales",
    "enterprise sales", "corporate sales", "commercial sales",
    "tech sales", "saas sales", "software sales", "technology sales",
    "revenue operations", "channel sales",
    "partnerships associate", "partner development",
    "sdr", "solutions sales",
    "insurance sales", "insurance agent", "insurance representative",
]

# Titles that superficially match ROLE_KEYWORDS but are NOT sales roles.
NON_ROLE_TITLES = [
    "marketing coordinator",    # marketing
    "marketing analyst",        # marketing
    "financial analyst",        # finance
    "data analyst",             # data science
    "business analyst",         # business ops
    "hr analyst",               # human resources
    "operations analyst",       # general ops
    "account payable",          # accounting
    "account receivable",       # accounting
    "quality assurance",        # QA
    "customer service",         # support, not sales
    "customer support",         # support, not sales
    "technical support",        # support, not sales
    "sales engineer",           # engineering / presales
    "solutions engineer",       # engineering / presales
    "real estate agent",        # real estate — commission only
    "mortgage",                 # lending
    "loan officer",             # lending
    "financial advisor",        # wealth management
    "financial planner",        # wealth management
]

SENIOR_TITLE_KEYWORDS = [
    "senior", "sr", "sr ", "sr. ", " sr.", " sr ", "sr.", " sr,", "(sr)", "sr-",
    "principal", "director", "manager", "head of", "vp ", "vice president",
    "chief", "executive", "supervisor", "lead ", " iii", " iv", " v ", " ii",
    " 2", " 3", " 4", " 5", "midlevel", "mid-level", "avp", "suptrs",
    "staff", "advanced",
    # C-suite abbreviations
    "cfo", "ceo", "coo", "cto", "cpo", "cro",
    # Temporary / non-career roles
    "seasonal", "part-time", "part time", "parttime", "temporary",
    # Fractional roles are always senior
    "fractional",
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
    "silkroad.com", "cornerstone", "sap.com", "eightfold.ai",
    "isolvedhire.com", "csod.com",
]

# ─── Aggregators ──────────────────────────────────────────────────────────────

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
    # Niche job boards
    "jobs.chronicle.com", "tallo.com", "jobleads.com",
    "entertainmentcareers.net", "jobilize.com", "myjobhelper.com",
    "jobs.accaglobal.com", "higheredjobs.com",
    "joinhandshake.com", "app.joinhandshake.com",
    "showbizjobs.com", "earnbetter.com",
    "jobs.appcast.io", "jobs.intuit.com",
    "www.hospitalityonline.com", "hospitalityonline.com",
    # Staffing firms
    "jobot.com",
    "talentbridge.com", "accruepartners.com", "insightglobal.com",
    "element-staffing.com",
    "jobs.vaco.com", "roberthalf.com", "adecco.com", "manpower.com",
    "randstad.com", "kforce.com", "apexgroup.com", "staffmark.com",
    "aerotek.com", "heidrick.com", "michaelpage.com", "spencerstuart.com",
    "astoncarter.com", "addisongroup.com", "getcrg.com", "grahamjobs.com",
    "lhh.com", "talentally.com", "accentuatestaffing.com", "gdhinc.com",
    "inspyrsolutions.com", "mykelly.com", "pipercompanies.com", "matlensilver.com",
    "experis.com", "insidehighered.com", "mthreerecruitingportal",
]

# ─── Generic URL Endings ──────────────────────────────────────────────────────

GENERIC_URL_ENDINGS = [
    "/careers", "/jobs", "/internships", "/career-opportunities",
    "/work-with-us", "/join-us", "/job-search", "/openings",
    "/join-our-team", "/job-opportunities", "/internship-program",
    "/early-career", "/students", "/apply",
    "/about-royal/careers/internships",
    "/about-your-bank/work-with-us/careers/students.html",
    "/current-openings",
]

# ─── Job Identifier Patterns ──────────────────────────────────────────────────

JOB_ID_PATTERNS = [
    re.compile(r'\d{4,}'),
    re.compile(r'[A-Za-z0-9]{6,}[0-9][A-Za-z0-9]*'),
    re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
]

# ─── URL Title Validation Constants ──────────────────────────────────────────

GENERIC_TITLE_WORDS = {
    "analyst", "engineer", "developer", "manager", "associate", "specialist",
    "coordinator", "director", "assistant", "officer", "lead",
    "senior", "junior", "staff", "remote", "job", "jobs", "careers",
    "work", "home", "from", "team", "global", "north", "south",
    "east", "west", "united", "states", "americas", "apply", "view",
    "detail", "posting", "opening", "position", "role", "opportunity",
    "technician", "representative", "administrator", "intern", "entry",
    "level", "sales", "account", "business", "open",
}

SENIOR_URL_KEYWORDS = {
    "senior", "sr", "lead", "principal", "director", "vp", "head",
    "chief", "manager", "supervisor", "superintendent", "president",
}

# ─── Page Content Signal Lists ────────────────────────────────────────────────

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
    "the job you are trying to apply for has been filled",
    "job you are trying to apply for has been filled",
    "this job is no longer accepting applications",
]

APPLY_SIGNALS = [
    "apply now", "apply for this job",
    "apply for this position", "apply for this role",
    "apply today", "apply online", "submit your application",
    "apply here", "easy apply",
    "apply for this job online",
    "icims_applyonlinebutton",
    "apply to job",
    "apply-click",
    "top-apply",
    "applyonlinebutton",
    "apply-button",
    "applybutton",
    "apply-now",
    "data-apply",
    "applicationurl",
    "apply-link",
    "apply for this opportunity",
    "submit your resume",
    "apply",
    "apply to this position",
]

STAFFING_PAGE_SIGNALS = [
    "our client",
    "partnered with a",
    "partnering with a",
    "on behalf of our client",
    "on behalf of a client",
    "representing multiple",
    "search managed by",
    "working with a client",
    "working with our client",
    "client is looking",
    "client is seeking",
    "client company",
    "client organization",
    "our client is a",
    "our client has",
    "virtual recruiter",
    "jobot pro",
    "your recruiter",
    "your dedicated recruiter",
    "reach out to your recruiter",
    "consultant careers",
    "current consultants",
    "staffing firm",
    "staffing agency",
    "staffing company",
    "staffing solutions",
    "direct placement firm",
    "recruiting firm",
    "placement firm",
    "workforce solutions",
    "talent solutions",
    "serves thousands of clients",
    "thousands of organizations",
    "hundreds of organizations",
    "providing them with skilled talent",
    "connecting talent with",
    "placing professionals",
    "we place",
    "we staff",
    "we recruit",
    "we match",
    "employee type: contract",
    "this is a contract",
    "contract-to-hire",
    "contract to hire",
    "temp to hire",
    "temporary position",
    "w2 only",
    "w2 contract",
    "c2c",
    "corp to corp",
    "kelly services", "kelly science", "kelly technology",
    "mthree trains", "mthree programme",
    "piper companies", "inspyr solutions",
    "experis", "manpowergroup",
]

# ─── Company Name Normalization ───────────────────────────────────────────────

COMPANY_NAME_NOISE = {
    "inc", "llc", "ltd", "corp", "corporation", "company", "companies",
    "group", "usa", "us", "the", "and", "solutions", "services",
    "associates", "partners", "co", "international", "global",
    "holdings", "enterprises", "technologies", "technology",
    "consulting", "management", "resources", "staffing", "systems",
}


def normalize_company_tokens(company: str) -> list[str]:
    """
    Converts a company name into a list of short tokens that are likely
    to appear inside a domain name.

    The process:
      1. Strip punctuation and lowercase the name
      2. Split into words and remove legal/generic noise (Inc, LLC, Group, etc.)
      3. Drop tokens shorter than 3 characters
      4. Append a joined version of the first two tokens to catch
         domain styles like 'aosmith' from 'A. O. Smith'
    """
    cleaned = re.sub(r"[^\w\s]", "", company.lower())
    tokens = [t for t in cleaned.split() if t not in COMPANY_NAME_NOISE and len(t) > 2]
    if len(tokens) >= 2:
        tokens.append(tokens[0] + tokens[1])
    return tokens


# ─── Role Filters ─────────────────────────────────────────────────────────────

def is_target_role(title: str) -> bool:
    """
    Returns True if the job title is a genuine sales role.

    Two-step check:
      1. The title must contain at least one word from ROLE_KEYWORDS
         (e.g. "sales representative", "account executive", "bdr").
      2. The title must NOT contain any phrase from NON_ROLE_TITLES —
         these are titles that superficially match sales keywords but
         belong to a different field (e.g. "sales engineer" matches
         "sales" but is a presales/engineering role, not pure sales).

    Returns False if either condition fails.
    """
    title_lower = title.lower()
    if any(kw in title_lower for kw in ROLE_KEYWORDS):
        if not any(excl in title_lower for excl in NON_ROLE_TITLES):
            return True
    return False


def is_senior_found(title: str) -> bool:
    """
    Returns True if the title appears to be entry-level (i.e. NOT senior).
    Returns False if any seniority keyword is found in the title.

    Note: Returns False when a senior keyword IS found — meaning skip.
    """
    title_lower = title.lower()
    if any(kw in title_lower for kw in SENIOR_TITLE_KEYWORDS):
        return False
    return True


def is_nc_found(location: str) -> bool:
    """
    Returns True if the job location falls within North Carolina.
    Returns False for empty locations, "nan" strings, or out-of-area.
    """
    if not location or location.lower() == "nan":
        return False
    location_lower = location.lower()
    return any(kw in location_lower for kw in VALID_LOCATION_KEYWORDS)


# ─── URL Validation ───────────────────────────────────────────────────────────

def has_job_identifier(url: str) -> bool:
    parsed = urlparse(url)
    searchable = parsed.path + "?" + parsed.query
    return any(pattern.search(searchable) for pattern in JOB_ID_PATTERNS)


def is_generic_ending(url: str) -> bool:
    path = urlparse(url).path.rstrip("/").lower()
    for ending in GENERIC_URL_ENDINGS:
        if path.endswith(ending.rstrip("/")):
            return True
    return False


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
    if any(token in domain for token in tokens):
        return True
    return False


# ─── URL Title Validator ──────────────────────────────────────────────────────

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
        senior_hit = slug_words & SENIOR_URL_KEYWORDS
        print(f"  ⚠️  URL slug contains seniority keyword(s): {senior_hit}")
        return False
    title_words = set(re.split(r"[\s\-_,]", title.lower()))
    slug_specific  = slug_words  - GENERIC_TITLE_WORDS
    title_specific = title_words - GENERIC_TITLE_WORDS
    if not slug_specific:
        return True
    overlap = slug_specific & title_specific
    if not overlap:
        print(f"  ⚠️  Title/URL mismatch — slug: {slug_specific} | title: {title_specific}")
        return False
    return True


# ─── URL Quality Check ────────────────────────────────────────────────────────

def check_url_quality(url: str) -> dict:
    """
    Opens the URL and runs three sequential checks on the page content,
    all from a single GET request.

    Check 1 — Is the URL active?
      HEAD check for 4xx, then scans for dead signals.

    Check 2 — Does the page have an apply button?
      Scans APPLY_SIGNALS. A real listing always has at least one signal.

    Check 3 — Is this a staffing firm posting?
      Scans STAFFING_PAGE_SIGNALS. Requires 2+ hits before rejecting.

    Returns {"is_active": bool, "reason": str}.
    """
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

        if not any(signal in content for signal in APPLY_SIGNALS):
            return {"is_active": False, "reason": "No apply button found — likely generic or dead page"}

        staffing_hits = [s for s in STAFFING_PAGE_SIGNALS if s in content]
        if len(staffing_hits) >= 2:
            return {"is_active": False, "reason": f"Staffing firm detected: {staffing_hits[:3]}"}

        return {"is_active": True, "reason": "Active listing with apply button confirmed"}

    except httpx.HTTPError as e:
        return {"is_active": False, "reason": f"GET failed: {e}"}


# ─── Serper Fallback ──────────────────────────────────────────────────────────

def serper_find_apply_url(title: str, company: str, location: str) -> str | None:
    """
    Uses Serper (Google Search API) to find a direct ATS application URL
    when the job_url from JobSpy is an aggregator or fails is_valid_url.

    Builds a query: "<title> <company> apply <location>"
    Returns the first result that passes is_valid_url, or None.
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

        print(f"  🔍 Serper: {query}")
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
        print(f"  [Serper] Error: {e}")

    return None


# ─── Main Pipeline ────────────────────────────────────────────────────────────

def run():
    """
    Main entry point for the pipeline. Orchestrates the full scraping,
    filtering, and URL validation process across all queries and locations.

    Flow for each scraped job:
      1.  Sanity check  — skip rows with no title, URL, or company name
      2.  Source URL dedup — skip if this exact source URL was already seen
      3.  Role check — skip non-sales titles
      4.  Senior check — skip senior/management/temporary titles
      5.  Location check — skip jobs outside NC target area
      6.  Title + company dedup — skip same job from two different sources
      7.  URL validation — use job_url directly if valid, else fall back to Serper
      8.  Title/URL match check — reject if URL slug contradicts the title
      9.  URL quality check — open the URL, verify active + apply button + not staffing
      10. Resolved URL dedup — skip if this apply URL was already stored
      11. Store — append to all_jobs and add URL to seen_urls
    """
    seen_urls: set[str] = set()
    seen_jobs: set[tuple[str, str]] = set()
    all_jobs: list[dict] = []

    total_raw          = 0
    skipped_dup        = 0
    skipped_role       = 0
    skipped_senior     = 0
    skipped_location   = 0
    skipped_no_url     = 0
    skipped_url_title  = 0
    skipped_quality    = 0
    urls_found         = 0

    for location in LOCATIONS:
        for query in QUERIES:
            print(f"\n{'─' * 60}")
            print(f"  {query!r}  →  {location}")
            print(f"{'─' * 60}")

            try:
                df = scrape_jobs(
                    site_name=["indeed", "zip_recruiter", "linkedin", "google"],
                    search_term=query,
                    location=location,
                    results_wanted=50,
                    hours_old=168,
                    country_indeed="USA",
                )
            except Exception as e:
                print(f"  ERROR: {e}")
                continue

            if df is None or df.empty:
                print(f"  No results.")
                continue

            total_raw += len(df)

            for _, row in df.iterrows():
                title   = str(row.get("title",    "")).strip()
                company = str(row.get("company",  "")).strip()
                job_url = str(row.get("job_url",  "")).strip()
                job_loc = str(row.get("location", "")).strip()

                if not title or not job_url or job_url == "nan":
                    continue
                if not company or company.lower() == "nan":
                    skipped_role += 1
                    continue

                if job_url in seen_urls:
                    skipped_dup += 1
                    continue
                seen_urls.add(job_url)

                print(f"\n  {title!r} @ {company} ({job_loc})")

                if not is_target_role(title):
                    print(f"  ⏭️  Not a sales role")
                    skipped_role += 1
                    continue

                if not is_senior_found(title):
                    print(f"  ⏭️  Senior title")
                    skipped_senior += 1
                    continue

                if not is_nc_found(job_loc):
                    print(f"  ⏭️  Not NC: {job_loc!r}")
                    skipped_location += 1
                    continue

                job_key = (title.lower(), company.lower())
                if job_key in seen_jobs:
                    print(f"  ⏭️  Already stored")
                    skipped_dup += 1
                    continue
                seen_jobs.add(job_key)

                if is_valid_url(job_url, company):
                    apply_url = job_url
                else:
                    print(f"  🔍 Falling back to Serper...")
                    serper_url = serper_find_apply_url(title, company, job_loc)
                    if serper_url and is_valid_url(serper_url, company):
                        apply_url = serper_url
                    else:
                        print(f"  ❌ No valid URL found")
                        skipped_no_url += 1
                        continue

                if not title_matches_url(title, apply_url):
                    print(f"  ❌ Title/URL mismatch — discarding")
                    skipped_url_title += 1
                    continue

                quality = check_url_quality(apply_url)
                if not quality["is_active"]:
                    print(f"  ❌ Quality check failed — {quality['reason']}")
                    skipped_quality += 1
                    continue
                print(f"  ✅ Quality check passed — {quality['reason']}")

                if apply_url in seen_urls:
                    print(f"  ⏭️  Resolved URL already stored")
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
                print(f"  ✅ {apply_url}")

            time.sleep(random.uniform(1, 3))

    print(f"\n{'=' * 60}")
    print(f"  Raw jobs scraped:             {total_raw}")
    print(f"  Skipped (duplicate):          {skipped_dup}")
    print(f"  Skipped (role):               {skipped_role}")
    print(f"  Skipped (senior):             {skipped_senior}")
    print(f"  Skipped (location):           {skipped_location}")
    print(f"  Skipped (no valid URL):       {skipped_no_url}")
    print(f"  Skipped (title/URL mismatch): {skipped_url_title}")
    print(f"  Skipped (quality check):      {skipped_quality}")
    print(f"  {'─' * 35}")
    print(f"  Jobs stored (clean URLs):     {urls_found}")
    print(f"{'=' * 60}\n")

    print("FINAL RESULTS\n" + "=" * 60)
    for job in all_jobs:
        print(f"  {job['title']} @ {job['company']}")
        print(f"  {job['location']}")
        print(f"  {job['url']}")
        print(f"  {'-' * 40}")


if __name__ == "__main__":
    run()