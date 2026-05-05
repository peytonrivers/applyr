"""
try_jobspy_accounting.py
JobSpy pipeline: entry-level accounting jobs in North Carolina

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
    → The page content is written in English
    → An apply button is present
    → The page shows no staffing firm signals

  This means we never store a URL from an unknown domain that has
  no verifiable connection to the hiring company.
"""

import os
import sys
import re
import time
import random
import httpx
from jobspy import scrape_jobs
from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv
from langdetect import detect, LangDetectException
from langdetect import DetectorFactory
# ── DB: import session factory and Jobs model from database.py ────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import get_db, Jobs

# Pin langdetect's internal RNG so results are consistent across runs.
# Without this, the same text can return different language codes on each call.
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

QUERIES = [
    "accountant", "entry level accountant", 
    "accounting analyst", "staff accountant", "staff accountant I"
    "junior accountant", "accounting associate", "accounts payable",
    "accounts receivable", "bookkeeper", "payroll specialist",
    "tax associate",
    "accounting intern", "accounting coordinator", "cost accountant",
    "general ledger accountant", "accounting clerk", "billing specialist",
    "budget analyst", "accounting graduate",
]

LOCATIONS = [
    "North Carolina",
    "NC",
    "Charlotte, NC",
    "Raleigh, NC",
    "Durham, NC",
    "Greensboro, NC",
    "Winston-Salem, NC",
    "Cary, NC",
    "Fayetteville, NC",
    "Wilmington, NC",
    "High Point, NC",
    "Asheville, NC",
    "Concord, NC",
    "Huntersville, NC",
]

VALID_LOCATION_KEYWORDS = [
    "nc", "north carolina", "charlotte", "raleigh",
    "durham", "greensboro", "cary", "fayetville",
    "wilmington", "asheville", "high point", "chapel hill",
    "winston-salem", "winston salem", "fayetteville",  # cover both spellings
    "concord", "huntersville",                          # new city locations added
]

# ─── Classification Constants ─────────────────────────────────────────────────

ACCOUNTING_KEYWORDS = [
    "accountant", "accounting", "bookkeep", "payroll",
    "tax", "billing", "budget", "cpa", "cma",
    "accounts payable", "accounts receivable", "gl ", "general ledger",
    "cost analyst", "fiscal", "ledger", "invoic",
]

# Titles that superficially match ACCOUNTING_KEYWORDS but are NOT accounting roles.
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
    "account operations",       # ops/delivery, not accounting
    "it auditor",               # tech audit, not accounting
    "faculty",
    "adjunct",
    "key account",
]

SENIOR_TITLE_KEYWORDS = [
    "senior", "sr", "sr ", "sr. ", " sr.", " sr ", "sr.", " sr,", "(sr)", "sr-",
    "principal", "director", "manager", "head of", "vp ", "vice president",
    "chief", "executive", "supervisor", "lead ", " iii", " iv", " v ", " ii",
    " 2", " 3", " 4", " 5", "midlevel", "mid-level", "avp", "suptrs",
    # C-suite abbreviations
    "cfo", "ceo", "coo", "cto", "cpo",
    # Fractional roles are always senior hires
    "fractional",
    # Controller roles are senior
    "controller",
    # Temporary / non-career roles
    "seasonal", "part-time", "part time", "parttime", "temporary", "contract",
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
    "dayforcehcm.com",  # Ceridian's rebranded ATS platform
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
    "bebee.com", "nextgenenergyjobs.com",
    # Staffing firms
    "jobot.com",
    "talentbridge.com", "accruepartners.com", "insightglobal.com",
    "element-staffing.com",
    "jobs.vaco.com", "roberthalf.com", "adecco.com", "manpower.com",
    "randstad.com", "kforce.com", "apexgroup.com", "staffmark.com",
    "aerotek.com", "heidrick.com", "michaelpage.com", "spencerstuart.com",
    "astoncarter.com", "addisongroup.com", "getcrg.com", "grahamjobs.com",
    "lhh.com", "talentally.com", "accentuatestaffing.com", "ledgent.com",
    "vaia.com",
]

# ─── Generic URL Endings ──────────────────────────────────────────────────────

GENERIC_URL_ENDINGS = [
    "/careers", "/jobs", "/internships", "/career-opportunities",
    "/work-with-us", "/join-us", "/job-search", "/openings",
    "/join-our-team", "/job-opportunities", "/internship-program",
    "/early-career", "/students",
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
    "the page you are looking for doesn't exist",
]

APPLY_SIGNALS = [
    # Standard phrases
    "apply now", "apply for this job",
    "apply for this position", "apply for this role",
    "apply today",
    "apply online", "submit your application", "apply here",
    "easy apply",
    # iCIMS specific
    "apply for this job online",
    "icims_applyonlinebutton",
    # Packaging Corp / Dayforce style
    "apply to job",
    "apply-click",
    "top-apply",
    # Other common raw HTML patterns
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
    # Client language — strongest signal
    "our client",
    "partnered with a",
    "partnering with a",
    "on behalf of our client",
    "representing multiple",
    "search managed by",
    # Recruiter attribution
    "virtual recruiter",
    "jobot pro",
    # Navigation / structural signals
    "consultant careers",
    "current consultants",
    # Self-identification in page content
    "staffing firm",
    "staffing agency",
    "direct placement firm",
    "recruiting firm",
    "placement firm",
    "serves thousands of clients",
    # Contract / temp signals
    "employee type: contract",
    "this is a contract",
    "contract-to-hire",
    "contract to hire",
    "temp to hire",
    "temporary position",
    "staffing",
]

# ─── Company Name Normalization ───────────────────────────────────────────────

COMPANY_NAME_NOISE = {
    "inc", "llc", "ltd", "corp", "corporation", "company", "companies",
    "group", "usa", "us", "the", "and", "solutions", "services",
    "associates", "partners", "co", "international", "global",
    "holdings", "enterprises", "technologies", "technology",
    "consulting", "management", "resources", "staffing", "systems",
}

# ─── Trusted ATS domains that skip the apply button check ────────────────────
# These platforms are confirmed to have apply buttons but render them via
# JavaScript, so httpx can't detect them in raw HTML.
TRUSTED_ATS_BYPASS = [
    "workforcenow.adp.com",
    "adp.com",
]


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

    Examples:
      "A. O. Smith Corporation"  → ["smith", "ao", "aosmith"]
      "Lowe's Companies, Inc."   → ["lowes"]
      "Compass Group USA"        → ["compass"]
      "UNC Charlotte"            → ["unc", "charlotte", "unccharlotte"]
    """
    cleaned = re.sub(r"[^\w\s]", "", company.lower())
    tokens = [t for t in cleaned.split() if t not in COMPANY_NAME_NOISE and len(t) > 2]
    if len(tokens) >= 2:
        tokens.append(tokens[0] + tokens[1])
    return tokens


# ─── Role Filters ─────────────────────────────────────────────────────────────

def is_accounting_role(title: str) -> bool:
    """
    Returns True if the job title is a genuine accounting role.

    Two-step check:
      1. The title must contain at least one word from ACCOUNTING_KEYWORDS
         (e.g. "accountant", "payroll", "ledger", "audit").
      2. The title must NOT contain any phrase from NON_ACCOUNTING_TITLES —
         these are titles that superficially match accounting keywords but
         belong to a different field (e.g. "account executive" matches
         "account" but is a sales role, not accounting).

    Returns False if either condition fails.
    """
    title_lower = title.lower()
    if any(kw in title_lower for kw in ACCOUNTING_KEYWORDS):
        if not any(excl in title_lower for excl in NON_ACCOUNTING_TITLES):
            return True
    return False


def is_senior_found(title: str) -> bool:
    """
    Returns True if the title appears to be entry-level (i.e. NOT senior).
    Returns False if any seniority keyword is found in the title.

    Checks against SENIOR_TITLE_KEYWORDS which covers:
      - Explicit seniority words: "senior", "sr", "principal", "lead"
      - Management titles: "manager", "director", "supervisor", "head of"
      - C-suite: "cfo", "ceo", "coo", "cto", "chief"
      - Roman numerals / number suffixes: "ii", "iii", "iv", " 2", " 3"
      - Temporary / non-career roles: "seasonal", "part-time"
      - Fractional roles which are always senior consulting positions

    Note: The function name reads as "is senior found" — it returns False
    when a senior keyword IS found, meaning the job should be skipped.
    """
    title_lower = title.lower()
    if any(kw in title_lower for kw in SENIOR_TITLE_KEYWORDS):
        return False
    return True


def is_nc_found(location: str) -> bool:
    """
    Returns True if the job location falls within the target area
    (North Carolina and its surrounding metro cities).

    Checks the location string against VALID_LOCATION_KEYWORDS which
    includes state abbreviations ("nc", "north carolina") and specific
    city names in the Charlotte metro and broader NC region.

    Returns False for empty locations, "nan" strings, or any location
    that doesn't match a known NC keyword — this filters out jobs that
    JobSpy returned for an NC query but tagged with a non-NC location.
    """
    if not location or location.lower() == "nan":
        return False
    location_lower = location.lower()
    return any(kw in location_lower for kw in VALID_LOCATION_KEYWORDS)


# ─── URL Validation ───────────────────────────────────────────────────────────

def has_job_identifier(url: str) -> bool:
    """
    Returns True if the URL contains a numeric or alphanumeric job ID
    somewhere in the path or query string.

    Uses three patterns from JOB_ID_PATTERNS:
      1. Any sequence of 4+ digits (e.g. /jobs/16277, ?jobId=526729)
      2. Any 6+ char alphanumeric token containing at least one digit
         (e.g. REQ-12152, JR-02431832, 4567383006)
      3. A full UUID (e.g. Workable job codes, ADP cid params)

    Real job listings always have some form of ID in the URL.
    Generic career homepages typically do not.
    """
    parsed = urlparse(url)
    searchable = parsed.path + "?" + parsed.query
    return any(pattern.search(searchable) for pattern in JOB_ID_PATTERNS)


def is_generic_ending(url: str) -> bool:
    """
    Returns True if the URL path ends with a known generic careers
    page suffix — meaning it's a company's career homepage or job
    listing index rather than a specific job posting.

    Checks against GENERIC_URL_ENDINGS which includes common endings
    like /careers, /jobs, /openings, /current-openings, /internships,
    /job-opportunities, /apply, and a few bank-specific legacy paths
    caught in earlier runs.
    """
    path = urlparse(url).path.rstrip("/").lower()
    for ending in GENERIC_URL_ENDINGS:
        if path.endswith(ending.rstrip("/")):
            return True
    return False


def is_specific_listing(url: str) -> bool:
    """
    Returns True if the URL appears to point to a specific job listing
    rather than a general career page.

    Three conditions must all be met:
      1. The URL path has at least 2 segments — a bare domain or single
         segment path (e.g. company.com/careers) is always generic.
      2. The URL contains a job identifier — a numeric or alphanumeric
         ID somewhere in the path or query string.
      3. The path does not end with a known generic careers suffix.

    Validated against every clean URL across all pipeline runs — every
    real listing satisfied all three conditions.
    """
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
    """
    Primary URL acceptance gate — returns True only if the URL is both
    a specific listing AND comes from a trusted domain.

    Rejection order:
      1. Aggregator / staffing firm domain → reject immediately before
         anything else, even if company name would otherwise match.
      2. Not a specific listing (generic page, no job ID, too few
         path segments) → reject.

    Acceptance order (either condition is sufficient):
      3. URL domain is in ATS_DOMAINS (known ATS platform) → accept.
      4. A normalized company name token appears in the URL domain
         (e.g. "lowes" in "talent.lowes.com") → accept.

    If neither acceptance condition is met the URL is rejected — we
    never store a URL from an unknown domain with no link to the company.
    """
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
    """
    Extracts meaningful words from the job title slug embedded in a URL path.

    Walks the path segments from the end, looking for the first segment
    that contains at least 2 alpha words of 3+ characters separated by
    dashes or underscores — this is the pattern used by ATS platforms
    for human-readable slugs (e.g. "staff-accountant", "payroll-specialist").

    Returns an empty set when no readable slug is found, which happens for:
      - Pure numeric IDs (/jobs/16277)
      - UUIDs (/j/7E649AFECA)
      - Workday/Taleo opaque paths

    An empty set result gives the URL a free pass since there is nothing
    meaningful to compare against the scraped title.
    """
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
    """
    Returns True if the URL slug is consistent with the scraped job title.

    This catches two problems that slip past all other filters:

      1. Seniority hidden in the URL slug — Serper occasionally returns a
         URL for a senior role even when the scraped title looks entry-level.
         If the slug contains words like "senior", "sr", "lead", "director",
         or "controller" the job is rejected regardless of what the title says.

      2. Completely wrong job association — Serper sometimes links a job
         title to the wrong posting entirely. If the URL slug has readable
         title words but none of them overlap with the scraped title (after
         removing generic words like "analyst", "staff", "remote"), the URL
         is rejected as a mismatch.

    URLs with opaque slugs (pure IDs, UUIDs, Taleo paths) always return
    True because there is nothing to compare — _extract_slug_words returns
    an empty set in those cases.

    Examples:
      title="Staff Accountant", url=".../staff-accountant/job/ABC123" → True
      title="Staff Accountant", url=".../senior-financial-analyst/..."  → False (seniority)
      title="Payroll Specialist", url=".../billing-coordinator/..."     → False (mismatch)
      title="Staff Accountant", url=".../jobs/16277"                    → True (opaque ID)
    """
    slug_words = _extract_slug_words(url)

    if not slug_words:
        return True

    # Check 1: seniority keyword in URL slug
    if slug_words & SENIOR_URL_KEYWORDS:
        senior_hit = slug_words & SENIOR_URL_KEYWORDS
        print(f"  ⚠️  URL slug contains seniority keyword(s): {senior_hit}")
        return False

    # Check 2: specific-word overlap between slug and title
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


# ─── Language Detection ───────────────────────────────────────────────────────

def is_english_content(text: str, min_length: int = 50) -> bool:
    """
    Returns True if the page content is detected as English.

    Uses langdetect, which is seeded at import time (DetectorFactory.seed = 0)
    to ensure deterministic results across runs.

    Two edge cases are given a free pass rather than a rejection:
      - Text shorter than min_length characters — too little content for
        reliable detection. ATS pages sometimes serve a thin initial HTML
        shell before JS hydration, so short content shouldn't auto-fail.
      - LangDetectException — raised when the detector cannot identify any
        language at all (e.g. a page of pure HTML tags or encoded garbage).
        In this case we let the listing through and rely on the apply button
        and staffing checks to catch it if something is wrong.

    Non-English results (Spanish, Chinese, etc.) are a strong scam signal
    for US-targeted job listings and are rejected outright.
    """
    if not text or len(text.strip()) < min_length:
        return True
    try:
        return detect(text) == "en"
    except LangDetectException:
        return True


# ─── URL Quality Check ────────────────────────────────────────────────────────

def check_url_quality(url: str) -> dict:
    """
    Opens the URL and runs four sequential checks on the page content,
    all from a single GET request — no redundant HTTP calls.

    Check 1 — Is the URL active?
      Runs a HEAD check first to catch 4xx responses cheaply before
      fetching the full page. Then scans the page body for dead signals
      like "job not found", "no longer available", "position has been
      filled", etc. Returns is_active: False if any dead signal is found.

    Check 2 — Is the page written in English?
      Uses langdetect to identify the primary language of the visible
      page text. Non-English pages are rejected as a scam signal — all
      legitimate US job listings targeting NC applicants are in English.
      Pages that are too short to detect or trigger a LangDetectException
      are given a free pass; the remaining checks will catch bad pages.

    Check 3 — Does the page have an apply button?
      Scans for apply signals across a broad set of patterns confirmed
      to appear in raw HTML across different ATS platforms:
        - Standard phrases: "apply now", "submit application", "easy apply"
        - iCIMS (server-rendered): "apply for this job online",
          "icims_applyonlinebutton"
        - Dayforce/Packaging Corp: "apply to job", "apply-click"
        - Raw HTML class names: "applyonlinebutton", "apply-button",
          "apply-now", "data-apply"
      A real job listing will always have at least one of these present
      in the raw HTML. A search results page, career center homepage,
      or dead listing will not. Returns is_active: False if none found.

    Check 4 — Is this a staffing firm posting?
      Scans for staffing firm signals across two categories:
        - Client language: "our client", "partnered with a",
          "on behalf of our client", "search managed by"
        - Structural signals: "consultant careers", "staffing agency",
          "employee type: contract", "virtual recruiter"
      Requires 2+ signals before rejecting — a single word like
      "staffing" could appear on a legitimate employer page, but
      2+ signals together is near-certain confirmation.

    Returns {"is_active": bool, "reason": str}.
    """
    # ── Step 1a: HEAD check ───────────────────────────────────────────────────
    try:
        head = httpx.head(url, follow_redirects=True, timeout=10, headers=HEADERS)
        if head.status_code in (400, 403, 404, 410):
            return {"is_active": False, "reason": f"HTTP {head.status_code}"}
    except httpx.HTTPError as e:
        return {"is_active": False, "reason": f"HEAD failed: {e}"}

    # ── Steps 1b-4: GET + content scan ───────────────────────────────────────
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=15, headers=HEADERS)
        content = resp.text.lower()

        # Check 1 — Active listing
        for signal in DEAD_SIGNALS:
            if signal in content:
                return {"is_active": False, "reason": f"Dead signal: '{signal}'"}

        # Check 2 — English content
        if not is_english_content(resp.text):
            detected = detect(resp.text) if resp.text.strip() else "unknown"
            return {"is_active": False, "reason": f"Non-English content detected: '{detected}'"}

        # Check 3 — Apply button present
        # Skip this check for trusted ATS platforms that render buttons via JS
        is_trusted_ats = any(domain in url.lower() for domain in TRUSTED_ATS_BYPASS)
        if not is_trusted_ats and not any(signal in content for signal in APPLY_SIGNALS):
            return {"is_active": False, "reason": "No apply button found — likely generic or dead page"}

        # Check 4 — Not a staffing firm
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

    Builds a query in the format:
      "<title> <company> apply <location>"

    The "apply" keyword biases Google results toward actual ATS application
    pages rather than news articles, PDFs, or government archives.

    Iterates through the top 5 organic results and returns the first one
    that passes is_valid_url — meaning it must be a known ATS or company
    domain AND a specific listing, not a generic career page.

    Returns None if no valid result is found or if the API call fails.
    """
    query = f"{title} {company} apply {location}"

    try:
        resp = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": 8},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("organic", [])

        print(f"  🔍 Serper: {query}")
        for i, r in enumerate(results[:8], 1):
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


# ─── Database Save ────────────────────────────────────────────────────────────

def save_to_db(jobs: list[dict]):
    """
    Commits all collected jobs to the database in a single transaction.

    Called once at the end of run() after all filtering is complete.
    Uses flush() per record so a duplicate job_url (unique constraint)
    skips that one row without rolling back the entire batch — the
    rest of the jobs still commit cleanly.
    """
    db = next(get_db())
    saved = 0
    skipped = 0
    try:
        for job in jobs:
            # Map each dict entry to the Jobs model columns
            record = Jobs(
                job_name     = job["title"],
                job_location = job["location"],
                job_url      = job["url"],
                industry     = job["industry"],
                niche        = job["niche"],
                is_active    = True,
            )
            db.add(record)
            try:
                # flush() writes to DB without committing — lets us catch
                # per-row constraint violations without aborting the batch
                db.flush()
                saved += 1
            except Exception:
                db.rollback()
                skipped += 1
                print(f"  ⚠️  Skipped duplicate: {job['url']}")

        # Single commit for all successfully flushed records
        db.commit()
        print(f"\n  ✅ Committed {saved} jobs to database. ({skipped} duplicates skipped)")
    except Exception as e:
        db.rollback()
        print(f"\n  ❌ DB commit failed: {e}")
    finally:
        db.close()


# ─── Main Pipeline ────────────────────────────────────────────────────────────

def run():
    """
    Main entry point for the pipeline. Orchestrates the full scraping,
    filtering, and URL validation process across all queries and locations.

    Flow for each scraped job:
      1.  Sanity check  — skip rows with no title, URL, or company name
      2.  Source URL dedup — skip if this exact source URL was already seen
      3.  Accounting role check — skip non-accounting titles
      4.  Senior check — skip senior/management/temporary titles
      5.  Location check — skip jobs outside NC target area
      6.  Title + company dedup — skip same job from two different sources
      7.  URL validation — use job_url directly if valid, else fall back to Serper
      8.  Title/URL match check — reject if URL slug contradicts the title
      9.  URL quality check — open the URL, verify it is active, written in
          English, has an apply button, and shows no staffing firm signals
      10. Resolved URL dedup — skip if this apply URL was already stored
      11. Store — append to all_jobs and add URL to seen_urls

    Prints a summary at the end with counts for each skip reason,
    then prints the full list of stored jobs with their URLs.
    """
    # ── Pre-seed seen_urls from DB to prevent cross-run duplicates ───────────
    # Loads every job_url already committed so they're caught at step 1 and
    # step 9 (source URL dedup + resolved URL dedup) before save_to_db is
    # ever reached — no reliance on unique constraint alone.
    db = next(get_db())
    existing_urls = {row.job_url for row in db.query(Jobs.job_url).all()}
    db.close()
    print(f"  📦 Loaded {len(existing_urls)} existing URLs from database.")

    seen_urls: set[str] = existing_urls  # pre-seeded — not an empty set
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
                # ── DB: capture which JobSpy source produced this listing ─────
                source  = str(row.get("site",     "")).strip()

                # ── 0. Sanity check ───────────────────────────────────────────
                if not title or not job_url or job_url == "nan":
                    continue
                if not company or company.lower() == "nan":
                    skipped_role += 1
                    continue

                # ── 1. Source URL dedup ───────────────────────────────────────
                if job_url in seen_urls:
                    skipped_dup += 1
                    continue
                seen_urls.add(job_url)

                print(f"\n  {title!r} @ {company} ({job_loc})")

                # ── 2. Accounting role check ──────────────────────────────────
                if not is_accounting_role(title):
                    print(f"  ⏭️  Not an accounting role")
                    skipped_role += 1
                    continue

                # ── 3. Senior check ───────────────────────────────────────────
                if not is_senior_found(title):
                    print(f"  ⏭️  Senior title")
                    skipped_senior += 1
                    continue

                # ── 4. Location check ─────────────────────────────────────────
                if not is_nc_found(job_loc):
                    print(f"  ⏭️  Not NC: {job_loc!r}")
                    skipped_location += 1
                    continue

                # ── 5. Title + company dedup ──────────────────────────────────
                job_key = (title.lower(), company.lower())
                if job_key in seen_jobs:
                    print(f"  ⏭️  Already stored")
                    skipped_dup += 1
                    continue
                seen_jobs.add(job_key)

                # ── 6. URL validation ─────────────────────────────────────────
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

                # ── 7. Title/URL match check ──────────────────────────────────
                if not title_matches_url(title, apply_url):
                    print(f"  ❌ Title/URL mismatch — discarding")
                    skipped_url_title += 1
                    continue

                # ── 8. URL quality check ──────────────────────────────────────
                quality = check_url_quality(apply_url)
                if not quality["is_active"]:
                    print(f"  ❌ Quality check failed — {quality['reason']}")
                    skipped_quality += 1
                    continue
                print(f"  ✅ Quality check passed — {quality['reason']}")

                # ── 9. Resolved URL dedup ─────────────────────────────────────
                if apply_url in seen_urls:
                    print(f"  ⏭️  Resolved URL already stored")
                    skipped_dup += 1
                    continue

                seen_urls.add(apply_url)
                urls_found += 1
                # ── DB: include industry, niche, and source in the stored dict ─
                all_jobs.append({
                    "title":    title,
                    "company":  company,
                    "location": job_loc,
                    "url":      apply_url,
                    "industry": "business",   # hardcoded for this pipeline
                    "niche":    "accounting",          # the search term that found it
                    "source":   source,         # jobspy site (indeed, linkedin, etc.)
                })
                print(f"  ✅ {apply_url}")

            time.sleep(random.uniform(1, 3))

    # ── Summary ───────────────────────────────────────────────────────────────
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

    # ── Final output ──────────────────────────────────────────────────────────
    print("FINAL RESULTS\n" + "=" * 60)
    for job in all_jobs:
        print(f"  {job['title']} @ {job['company']}")
        print(f"  {job['location']}")
        print(f"  {job['url']}")
        print(f"  {'-' * 40}")

    # ── DB: commit all passing jobs to the database in one batch ──────────────
    if all_jobs:
        save_to_db(all_jobs)
    else:
        print("  No jobs to commit.")


if __name__ == "__main__":
    run()