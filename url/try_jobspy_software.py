"""
pipeline_software.py
JobSpy pipeline: entry-level software engineering jobs in North Carolina

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
    # SOFTWARE ENGINEERING CORE
    # -------------------------
    "software engineer",
    "software developer",
    "entry level software engineer",
    "entry level software developer",
    "junior software engineer",
    "junior software developer",
    "associate software engineer",
    "associate software developer",
    "new grad software engineer",
    "new grad software developer",
    "graduate software engineer",
    "graduate software developer",
    "application engineer",
    "application developer",
    "entry level application engineer",
    "entry level application developer",

    # -------------------------
    # BACKEND
    # -------------------------
    "backend engineer",
    "backend developer",
    "entry level backend engineer",
    "entry level backend developer",
    "backend software engineer",
    "backend software developer",
    "entry level backend software engineer",
    "entry level backend software developer",
    "api engineer",
    "api developer",
    "entry level api engineer",
    "entry level api developer",
    "server side engineer",
    "server side developer",
    "entry level server side engineer",
    "entry level server side developer",

    # Backend language-specific
    "python engineer",
    "python developer",
    "entry level python engineer",
    "entry level python developer",
    "java engineer",
    "java developer",
    "entry level java engineer",
    "entry level java developer",
    "c# engineer",
    "c# developer",
    "entry level c# engineer",
    "entry level c# developer",
    "golang engineer",
    "golang developer",
    "entry level golang engineer",
    "entry level golang developer",
    "go engineer",
    "go developer",
    "entry level go engineer",
    "entry level go developer",
    "node.js engineer",
    "node.js developer",
    "entry level node.js engineer",
    "entry level node.js developer",
    "node engineer",
    "node developer",
    "entry level node engineer",
    "entry level node developer",

    # -------------------------
    # FULL STACK
    # -------------------------
    "full stack engineer",
    "full stack developer",
    "entry level full stack engineer",
    "entry level full stack developer",
    "fullstack engineer",
    "fullstack developer",
    "entry level fullstack engineer",
    "entry level fullstack developer",
    "full stack software engineer",
    "full stack software developer",
    "entry level full stack software engineer",
    "entry level full stack software developer",

    # Full stack language-specific
    "javascript engineer",
    "javascript developer",
    "entry level javascript engineer",
    "entry level javascript developer",
    "typescript engineer",
    "typescript developer",
    "entry level typescript engineer",
    "entry level typescript developer",
    "react engineer",
    "react developer",
    "entry level react engineer",
    "entry level react developer",
    "web engineer",
    "web developer",
    "entry level web engineer",
    "entry level web developer",

    # -------------------------
    # MOBILE
    # -------------------------
    "mobile engineer",
    "mobile developer",
    "entry level mobile engineer",
    "entry level mobile developer",
    "mobile software engineer",
    "mobile software developer",
    "entry level mobile software engineer",
    "entry level mobile software developer",
    "ios engineer",
    "ios developer",
    "entry level ios engineer",
    "entry level ios developer",
    "android engineer",
    "android developer",
    "entry level android engineer",
    "entry level android developer",
    "swift engineer",
    "swift developer",
    "entry level swift engineer",
    "entry level swift developer",
    "kotlin engineer",
    "kotlin developer",
    "entry level kotlin engineer",
    "entry level kotlin developer",
    "react native engineer",
    "react native developer",
    "entry level react native engineer",
    "entry level react native developer",
    "flutter engineer",
    "flutter developer",
    "entry level flutter engineer",
    "entry level flutter developer",

    # -------------------------
    # QA / TESTING
    # -------------------------
    "qa engineer",
    "qa developer",
    "entry level qa engineer",
    "entry level qa developer",
    "test engineer",
    "test developer",
    "entry level test engineer",
    "entry level test developer",
    "software test engineer",
    "software test developer",
    "entry level software test engineer",
    "entry level software test developer",
    "qa automation engineer",
    "qa automation developer",
    "entry level qa automation engineer",
    "entry level qa automation developer",
    "automation engineer",
    "automation developer",
    "entry level automation engineer",
    "entry level automation developer",
    "sdet",
    "entry level sdet",
    "junior sdet",

    # QA language/tool-specific
    "selenium engineer",
    "selenium developer",
    "entry level selenium engineer",
    "entry level selenium developer",
    "playwright engineer",
    "playwright developer",
    "entry level playwright engineer",
    "entry level playwright developer",

    # -------------------------
    # AI (NOT ML)
    # -------------------------
    "ai engineer",
    "ai developer",
    "entry level ai engineer",
    "entry level ai developer",
    "artificial intelligence engineer",
    "artificial intelligence developer",
    "entry level artificial intelligence engineer",
    "entry level artificial intelligence developer",
    "ai software engineer",
    "ai software developer",
    "entry level ai software engineer",
    "entry level ai software developer",
    "generative ai engineer",
    "generative ai developer",
    "entry level generative ai engineer",
    "entry level generative ai developer",
    "llm engineer",
    "llm developer",
    "entry level llm engineer",
    "entry level llm developer",
    "prompt engineer",
    "prompt developer",
    "entry level prompt engineer",
    "entry level prompt developer",
    "ai application engineer",
    "ai application developer",
    "entry level ai application engineer",
    "entry level ai application developer",

    # -------------------------
    # GENERAL LANGUAGE/TITLE VARIANTS
    # -------------------------
    "python software engineer",
    "python software developer",
    "entry level python software engineer",
    "entry level python software developer",
    "java software engineer",
    "java software developer",
    "entry level java software engineer",
    "entry level java software developer",
    "javascript software engineer",
    "javascript software developer",
    "entry level javascript software engineer",
    "entry level javascript software developer",
    "typescript software engineer",
    "typescript software developer",
    "entry level typescript software engineer",
    "entry level typescript software developer",
    "react software engineer",
    "react software developer",
    "entry level react software engineer",
    "entry level react software developer"
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
    "software engineer", "software developer", "frontend", "back end",
    "backend", "full stack", "fullstack", "web developer", "web engineer",
    "mobile developer", "mobile engineer", "ai engineer", "ml engineer",
    "machine learning", "devops", "cloud engineer", "java developer",
    "python developer", "react developer", "node developer",
    "ios developer", "android developer", "api developer",
    "site reliability", "sre", "software intern", "developer intern",
    "engineer intern", "software development", "python", "java", "nodejs",
]

# Titles that superficially match ROLE_KEYWORDS but are NOT software roles.
NON_ROLE_TITLES = [
    "sales engineer",           # sales / presales
    "solutions engineer",       # sales / presales
    "customer engineer",        # support
    "field engineer",           # hardware / field ops
    "network engineer",         # infrastructure
    "hardware engineer",        # not software
    "mechanical engineer",      # not software
    "civil engineer",           # not software
    "electrical engineer",      # not software
    "industrial engineer",      # not software
    "quality assurance",        # QA testing
    "qa engineer",              # QA testing
    "support engineer",         # technical support
    "test engineer",            # QA testing
    "manufacturing engineer",   # not software
    "process engineer",         # not software
    "systems engineer",         # often hardware/defense
    "firmware engineer",        # embedded, not pure software
    "hvac",
]

SENIOR_TITLE_KEYWORDS = [
    "senior", "sr", "sr ", "sr. ", " sr.", " sr ", "sr.", " sr,", "(sr)", "sr-",
    "principal", "director", "manager", "head of", "vp ", "vice president",
    "chief", "executive", "supervisor", "lead ", " iii", " iv", " v ", " ii",
    " 2", " 3", " 4", " 5", "midlevel", "mid-level", "avp", "suptrs",
     "staff", "advanced",
    # C-suite abbreviations
    "cfo", "ceo", "coo", "cto", "cpo",
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
    "experis.com", "insidehighered.com", "mthreerecruitingportal"
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
    "level", "software", "open",
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
    "This job is no longer accepting applications",
]

APPLY_SIGNALS = [
    # Standard phrases
    "apply now", "apply for this job",
    "apply for this position", "apply for this role",
    "apply today", "apply online", "submit your application",
    "apply here", "easy apply",
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
    # Client language — strongest signal, direct employers never say this
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

    # Recruiter attribution
    "virtual recruiter",
    "jobot pro",
    "your recruiter",
    "your dedicated recruiter",
    "reach out to your recruiter",

    # Navigation / structural signals
    "consultant careers",
    "current consultants",

    # Self-identification in page content
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

    # Contract / temp signals
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

    # Kelly Services specific
    "kelly services",
    "kelly science",
    "kelly technology",

    # mthree specific
    "mthree trains",
    "mthree programme",

    # Piper Companies specific
    "piper companies",

    # INSPYR specific
    "inspyr solutions",

    # Experis / ManpowerGroup specific
    "experis",
    "manpowergroup",
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

def is_target_role(title: str) -> bool:
    """
    Returns True if the job title is a genuine software engineering role.

    Two-step check:
      1. The title must contain at least one word from ROLE_KEYWORDS
         (e.g. "software engineer", "frontend", "full stack").
      2. The title must NOT contain any phrase from NON_ROLE_TITLES —
         these are titles that superficially match role keywords but
         belong to a different field (e.g. "sales engineer" matches
         "engineer" but is a sales role, not software).

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

    Checks against SENIOR_TITLE_KEYWORDS which covers:
      - Explicit seniority words: "senior", "sr", "principal", "lead"
      - Management titles: "manager", "director", "supervisor", "head of"
      - C-suite abbreviations: "cfo", "ceo", "coo", "cto"
      - Roman numerals / number suffixes: "ii", "iii", "iv", " 2", " 3"
      - Temporary / non-career roles: "seasonal", "part-time", "temporary"

    Note: Returns False when a senior keyword IS found — meaning skip.
    """
    title_lower = title.lower()
    if any(kw in title_lower for kw in SENIOR_TITLE_KEYWORDS):
        return False
    return True


def is_nc_found(location: str) -> bool:
    """
    Returns True if the job location falls within North Carolina.

    Checks the location string against VALID_LOCATION_KEYWORDS which
    includes state abbreviations and major NC city names.

    Returns False for empty locations, "nan" strings, or any location
    outside the target area.
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
      1. The URL path has at least 2 segments.
      2. The URL contains a job identifier.
      3. The path does not end with a known generic careers suffix.
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
      1. Aggregator / staffing firm domain → reject immediately.
      2. Not a specific listing → reject.

    Acceptance order (either condition is sufficient):
      3. URL domain is in ATS_DOMAINS → accept.
      4. A normalized company name token appears in the URL domain → accept.
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

    Walks path segments from the end, looking for the first segment
    with at least 2 alpha words of 3+ characters separated by dashes
    or underscores. Returns an empty set for pure numeric IDs or UUIDs,
    which gives those URLs a free pass.
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

    Catches two problems:
      1. Seniority in the URL slug — rejects regardless of title.
      2. Completely wrong job association — rejects if no specific-word
         overlap exists between the slug and the scraped title.

    URLs with opaque slugs (pure IDs, UUIDs) always return True.
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


# ─── URL Quality Check ────────────────────────────────────────────────────────

def check_url_quality(url: str) -> dict:
    """
    Opens the URL and runs three sequential checks on the page content,
    all from a single GET request.

    Check 1 — Is the URL active?
      HEAD check for 4xx, then scans for dead signals like
      "job not found", "no longer available", "position has been filled".

    Check 2 — Does the page have an apply button?
      Scans APPLY_SIGNALS across standard phrases, ATS-specific raw HTML
      patterns (iCIMS, Dayforce, Greenhouse), and common class names.
      A real listing always has at least one signal in raw HTML.

    Check 3 — Is this a staffing firm posting?
      Scans STAFFING_PAGE_SIGNALS. Requires 2+ hits before rejecting
      to avoid false positives from legitimate employer pages.

    Returns {"is_active": bool, "reason": str}.
    """
    # ── Step 1a: HEAD check ───────────────────────────────────────────────────
    try:
        head = httpx.head(url, follow_redirects=True, timeout=10, headers=HEADERS)
        if head.status_code in (400, 403, 404, 410):
            return {"is_active": False, "reason": f"HTTP {head.status_code}"}
    except httpx.HTTPError as e:
        return {"is_active": False, "reason": f"HEAD failed: {e}"}

    # ── Step 1b-3: GET + content scan ────────────────────────────────────────
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=15, headers=HEADERS)
        content = resp.text.lower()

        # Check 1 — Active listing
        for signal in DEAD_SIGNALS:
            if signal in content:
                return {"is_active": False, "reason": f"Dead signal: '{signal}'"}

        # Check 2 — Apply button present
        if not any(signal in content for signal in APPLY_SIGNALS):
            return {"is_active": False, "reason": "No apply button found — likely generic or dead page"}

        # Check 3 — Not a staffing firm
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
      3.  Role check — skip non-software titles
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

                # ── 2. Role check ─────────────────────────────────────────────
                if not is_target_role(title):
                    print(f"  ⏭️  Not a software role")
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
                all_jobs.append({
                    "title":    title,
                    "company":  company,
                    "location": job_loc,
                    "url":      apply_url,
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


if __name__ == "__main__":
    run()