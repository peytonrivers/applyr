"""
pipeline_linkedin.py
LinkedIn scraper pipeline: entry-level accounting jobs in North Carolina

Data source:
  Playwright headless Chromium replaces JobSpy. Scrapes LinkedIn public
  job search pages across all QUERIES x LOCATIONS combos and returns
  {title, company, location, linkedin_url, posted_date} per card.

Filter chain (identical to try_jobspy_accounting.py):
  1.  Dedup by LinkedIn job ID (cross-query dedup, no DB needed)
  2.  Recency — posted_date older than RECENCY_DAYS is skipped
  3.  is_accounting_role(title)
  4.  is_senior_found(title)
  5.  is_nc_found(location)
  6.  is_known_staffing_firm(company)  ← saves Serper credits
  7.  Title + company dedup (same job from two queries)
  8.  serper_find_apply_url -> is_valid_url
  9.  title_matches_url
  10. check_url_quality
  11. Resolved URL dedup
  12. save_to_db
"""

import asyncio
import os
import re
import sys
import time
import httpx
import random
import urllib.parse
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from langdetect import detect, LangDetectException, DetectorFactory

# ── DB imports ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import get_db, Jobs

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

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

INDUSTRY     = "business"
NICHE        = "accounting"
RECENCY_DAYS = 30

QUERIES = [
    "accountant", "entry level accountant",
    "accounting analyst", "staff accountant", "staff accountant I",
    "junior accountant", "accounting associate", "accounts payable",
    "accounts receivable", "bookkeeper", "payroll specialist",
    "tax associate", "accounting intern", "accounting coordinator",
    "cost accountant", "general ledger accountant", "accounting clerk",
    "billing specialist", "budget analyst", "accounting graduate",
]

VALID_LOCATION_KEYWORDS = [
    "nc", "north carolina", "charlotte", "raleigh",
    "durham", "greensboro", "cary", "fayetteville",
    "wilmington", "asheville", "high point", "chapel hill",
    "winston-salem", "winston salem",
    "concord", "huntersville",
]

# ─────────────────────────────────────────────
# CLASSIFICATION CONSTANTS
# ─────────────────────────────────────────────

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
    "cfo", "ceo", "coo", "cto", "cpo",
    "fractional", "controller",
    "seasonal", "part-time", "part time", "parttime", "temporary", "contract",
]

# ─────────────────────────────────────────────
# STAFFING FIRM COMPANY-NAME BLOCKLIST
# ─────────────────────────────────────────────

KNOWN_STAFFING_FIRMS = {
    "robert half", "lhh", "ledgent", "vaco", "vaco by highspring",
    "beacon hill", "jobot", "aerotek", "adecco", "manpower", "randstad",
    "kelly services", "kelly", "staffmark", "spherion",
    "accountingfly", "accountants one", "parker and lynch", "parker+lynch",
    "creative financial staffing", "cfs", "kforce", "insight global",
    "experis", "modis", "tatum", "protiviti",
    "ferretti search", "stevendouglas", "carolina prg", "jcw group",
    "sherpa", "sherpa recruiting", "sherpa | recruiting, staffing & consulting",
    "10x recruiting partners", "parcc associates", "the resource co",
    "mass markets", "mci", "cogent analytics", "target rwe",
    "catapult employers association", "dataannotation", "jobgether",
}

# ─────────────────────────────────────────────
# ATS DOMAIN WHITELIST
# ─────────────────────────────────────────────

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

# ─────────────────────────────────────────────
# AGGREGATORS
# ─────────────────────────────────────────────

AGGREGATORS = [
    "indeed.com", "linkedin.com", "ziprecruiter.com", "glassdoor.com",
    "simplyhired.com", "monster.com", "careerbuilder.com", "lensa.com",
    "talent.com", "joblist.com", "builtin.com", "wellfound.com",
    "dice.com", "adzuna.com", "talentify.io", "jobright.ai",
    "tealhq.com", "jooble.org", "snagajob.com", "salary.com",
    "careerjet.com", "whatjobs.com", "wayup.com", "bandana.com",
    "recruit.net", "jobs2careers.com", "learn4good.com",
    "neuvoo.com", "jobrapido.com",
    "jobs.chronicle.com", "tallo.com", "jobleads.com",
    "entertainmentcareers.net", "jobilize.com", "myjobhelper.com",
    "jobs.accaglobal.com", "higheredjobs.com",
    "joinhandshake.com", "app.joinhandshake.com",
    "showbizjobs.com", "earnbetter.com",
    "jobs.appcast.io", "jobs.intuit.com",
    "www.hospitalityonline.com", "hospitalityonline.com",
    "bebee.com", "nextgenenergyjobs.com",
    "jobot.com", "talentbridge.com", "accruepartners.com", "insightglobal.com",
    "element-staffing.com", "jobs.vaco.com", "roberthalf.com", "adecco.com",
    "manpower.com", "randstad.com", "kforce.com", "apexgroup.com",
    "staffmark.com", "aerotek.com", "heidrick.com", "michaelpage.com",
    "spencerstuart.com", "astoncarter.com", "addisongroup.com",
    "getcrg.com", "grahamjobs.com", "lhh.com", "talentally.com",
    "accentuatestaffing.com", "ledgent.com", "vaia.com",
]

# ─────────────────────────────────────────────
# GENERIC URL ENDINGS
# ─────────────────────────────────────────────

GENERIC_URL_ENDINGS = [
    "/careers", "/jobs", "/internships", "/career-opportunities",
    "/work-with-us", "/join-us", "/job-search", "/openings",
    "/join-our-team", "/job-opportunities", "/internship-program",
    "/early-career", "/students",
    "/about-royal/careers/internships",
    "/about-your-bank/work-with-us/careers/students.html",
    "/current-openings",
]

JOB_ID_PATTERNS = [
    re.compile(r'\d{4,}'),
    re.compile(r'[A-Za-z0-9]{6,}[0-9][A-Za-z0-9]*'),
    re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
]

# ─────────────────────────────────────────────
# URL TITLE VALIDATION CONSTANTS
# ─────────────────────────────────────────────

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

# ─────────────────────────────────────────────
# PAGE CONTENT SIGNAL LISTS
# ─────────────────────────────────────────────

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
    "apply now", "apply for this job",
    "apply for this position", "apply for this role",
    "apply today", "apply online", "submit your application", "apply here",
    "easy apply", "apply for this job online", "icims_applyonlinebutton",
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

TRUSTED_ATS_BYPASS = [
    "workforcenow.adp.com",
    "adp.com",
]

# ─────────────────────────────────────────────
# LINKEDIN HELPERS
# ─────────────────────────────────────────────

def extract_job_id(linkedin_url: str) -> str | None:
    """Extract numeric job ID from LinkedIn URL for cross-query dedup."""
    match = re.search(r"-(\d{10,})(?:\?|$)", linkedin_url)
    return match.group(1) if match else None


def is_recent(date_str: str | None) -> bool:
    """Return True if posted within RECENCY_DAYS, or if date is missing."""
    if not date_str:
        return True
    try:
        posted = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
        return posted >= datetime.now(timezone.utc) - timedelta(days=RECENCY_DAYS)
    except ValueError:
        return True


def build_linkedin_url(query: str) -> str:
    q = urllib.parse.quote(query, safe="")
    return (
        f"https://www.linkedin.com/jobs/search"
        f"?keywords={q}"
        f"&location=North%20Carolina"
        f"&geoId=103255397"
        f"&trk=public_jobs_jobs-search-bar_search-submit"
        f"&position=1&pageNum=0"
    )

# ─────────────────────────────────────────────
# FILTER FUNCTIONS  (identical to try_jobspy_accounting.py)
# ─────────────────────────────────────────────

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
    if any(kw in title_lower for kw in SENIOR_TITLE_KEYWORDS):
        return False
    return True


def is_nc_found(location: str) -> bool:
    if not location or location.lower() == "nan":
        return False
    return any(kw in location.lower() for kw in VALID_LOCATION_KEYWORDS)


def is_known_staffing_firm(company: str) -> bool:
    return company.lower().strip() in KNOWN_STAFFING_FIRMS


def has_job_identifier(url: str) -> bool:
    parsed     = urlparse(url)
    searchable = parsed.path + "?" + parsed.query
    return any(pattern.search(searchable) for pattern in JOB_ID_PATTERNS)


def is_generic_ending(url: str) -> bool:
    path = urlparse(url).path.rstrip("/").lower()
    for ending in GENERIC_URL_ENDINGS:
        if path.endswith(ending.rstrip("/")):
            return True
    return False


def is_specific_listing(url: str) -> bool:
    parsed   = urlparse(url)
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


def _extract_slug_words(url: str) -> set[str]:
    path     = urlparse(url).path.lower()
    segments = [s for s in path.split("/") if s]
    if not segments:
        return set()
    for segment in reversed(segments):
        segment     = re.sub(r"\.\w{2,4}$", "", segment)
        words       = re.split(r"[-_]", segment)
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
    title_words    = set(re.split(r"[\s\-_,]", title.lower()))
    slug_specific  = slug_words  - GENERIC_TITLE_WORDS
    title_specific = title_words - GENERIC_TITLE_WORDS
    if not slug_specific:
        return True
    if not (slug_specific & title_specific):
        print(f"  ⚠️  Title/URL mismatch — slug: {slug_specific} | title: {title_specific}")
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
        resp    = httpx.get(url, follow_redirects=True, timeout=15, headers=HEADERS)
        content = resp.text.lower()

        for signal in DEAD_SIGNALS:
            if signal in content:
                return {"is_active": False, "reason": f"Dead signal: '{signal}'"}

        if not is_english_content(resp.text):
            detected = detect(resp.text) if resp.text.strip() else "unknown"
            return {"is_active": False, "reason": f"Non-English content: '{detected}'"}

        is_trusted_ats = any(domain in url.lower() for domain in TRUSTED_ATS_BYPASS)
        if not is_trusted_ats and not any(sig in content for sig in APPLY_SIGNALS):
            return {"is_active": False, "reason": "No apply button found"}

        staffing_hits = [s for s in STAFFING_PAGE_SIGNALS if s in content]
        if len(staffing_hits) >= 2:
            return {"is_active": False, "reason": f"Staffing firm detected: {staffing_hits[:3]}"}

        return {"is_active": True, "reason": "Active listing with apply button confirmed"}

    except httpx.HTTPError as e:
        return {"is_active": False, "reason": f"GET failed: {e}"}


def serper_find_apply_url(title: str, company: str, location: str) -> str | None:
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


def save_to_db(jobs: list[dict]):
    db      = next(get_db())
    saved   = 0
    skipped = 0
    try:
        for job in jobs:
            record = Jobs(
                job_name     = job["title"],
                company      = job["company"],
                job_location = job["location"],
                job_url      = job["url"],
                industry     = job["industry"],
                niche        = job["niche"],
                is_active    = True,
                source       = job["source"],
            )
            db.add(record)
            try:
                db.flush()
                saved += 1
            except Exception:
                db.rollback()
                skipped += 1
                print(f"  ⚠️  Skipped duplicate: {job['url']}")
        db.commit()
        print(f"\n  ✅ Committed {saved} jobs to database. ({skipped} duplicates skipped)")
    except Exception as e:
        db.rollback()
        print(f"\n  ❌ DB commit failed: {e}")
    finally:
        db.close()

# ─────────────────────────────────────────────
# LINKEDIN SCRAPER
# ─────────────────────────────────────────────

async def scrape_linkedin_query(page, query: str) -> list[dict]:
    """Scrape one query from LinkedIn public job search."""
    url = build_linkedin_url(query)
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("ul.jobs-search__results-list", timeout=15000)
    except Exception:
        return []

    # Scroll to trigger lazy-loaded cards
    for _ in range(5):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

    jobs = await page.evaluate("""
        () => {
            const cards = document.querySelectorAll("ul.jobs-search__results-list li");
            return Array.from(cards).map(card => {
                const titleEl    = card.querySelector(".base-search-card__title");
                const companyEl  = card.querySelector(".base-search-card__subtitle");
                const locationEl = card.querySelector(".job-search-card__location");
                const linkEl     = card.querySelector("a.base-card__full-link");
                const dateEl     = card.querySelector("time");
                return {
                    title:        titleEl?.innerText?.trim()        || null,
                    company:      companyEl?.innerText?.trim()      || null,
                    location:     locationEl?.innerText?.trim()     || null,
                    linkedin_url: linkEl?.href                      || null,
                    posted_date:  dateEl?.getAttribute("datetime") || null,
                };
            });
        }
    """)

    return [j for j in jobs if j["title"] and j["company"] and j["linkedin_url"]]

# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────

async def run():
    # Pre-seed seen_urls from DB to prevent cross-run duplicates
    db = next(get_db())
    existing_urls = {row.job_url for row in db.query(Jobs.job_url).all()}
    db.close()
    print(f"  📦 Loaded {len(existing_urls)} existing URLs from database.")

    seen_urls:    set[str]   = existing_urls
    seen_job_ids: set[str]   = set()   # LinkedIn job ID dedup
    seen_jobs:    set[tuple] = set()   # (title, company) dedup
    all_jobs:     list[dict] = []

    total_raw         = 0
    skipped_dup       = 0
    skipped_stale     = 0
    skipped_role      = 0
    skipped_senior    = 0
    skipped_location  = 0
    skipped_staffing  = 0
    skipped_no_url    = 0
    skipped_url_title = 0
    skipped_quality   = 0
    urls_found        = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        page = await context.new_page()
        await page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )

        for query in QUERIES:
            print(f"\n{'─' * 60}")
            print(f"  {query!r}")
            print(f"{'─' * 60}")

            jobs = await scrape_linkedin_query(page, query)

            if not jobs:
                print(f"  No results.")
                await asyncio.sleep(1)
                continue

            total_raw += len(jobs)

            for job in jobs:
                title   = job["title"]
                company = job["company"]
                loc     = job["location"] or ""

                # ── 1. Dedup by LinkedIn job ID ───────────────────────────
                job_id = extract_job_id(job["linkedin_url"])
                if not job_id or job_id in seen_job_ids:
                    skipped_dup += 1
                    continue
                seen_job_ids.add(job_id)

                print(f"\n  {title!r} @ {company} ({loc})")

                # ── 2. Recency check ──────────────────────────────────────
                if not is_recent(job["posted_date"]):
                    print(f"  ⏭️  Stale posting: {job['posted_date']}")
                    skipped_stale += 1
                    continue

                # ── 3. Accounting role check ──────────────────────────────
                if not is_accounting_role(title):
                    print(f"  ⏭️  Not an accounting role")
                    skipped_role += 1
                    continue

                # ── 4. Senior check ───────────────────────────────────────
                if not is_senior_found(title):
                    print(f"  ⏭️  Senior title")
                    skipped_senior += 1
                    continue

                # ── 5. Location check ─────────────────────────────────────
                if not is_nc_found(loc):
                    print(f"  ⏭️  Not NC: {loc!r}")
                    skipped_location += 1
                    continue

                # ── 6. Staffing firm company-name check ───────────────────
                if is_known_staffing_firm(company):
                    print(f"  ⏭️  Known staffing firm: {company!r}")
                    skipped_staffing += 1
                    continue

                # ── 7. Title + company dedup ──────────────────────────────
                job_key = (title.lower(), company.lower())
                if job_key in seen_jobs:
                    print(f"  ⏭️  Already seen this title + company")
                    skipped_dup += 1
                    continue
                seen_jobs.add(job_key)

                # ── 8. Serper ATS URL resolution ──────────────────────────
                serper_url = serper_find_apply_url(title, company, loc)
                if serper_url and is_valid_url(serper_url, company):
                    apply_url = serper_url
                else:
                    print(f"  ❌ No valid URL found")
                    skipped_no_url += 1
                    continue

                # ── 9. Title/URL match check ──────────────────────────────
                if not title_matches_url(title, apply_url):
                    print(f"  ❌ Title/URL mismatch — discarding")
                    skipped_url_title += 1
                    continue

                # ── 10. URL quality check ─────────────────────────────────
                quality = check_url_quality(apply_url)
                if not quality["is_active"]:
                    print(f"  ❌ Quality check failed — {quality['reason']}")
                    skipped_quality += 1
                    continue
                print(f"  ✅ Quality check passed — {quality['reason']}")

                # ── 11. Resolved URL dedup ────────────────────────────────
                if apply_url in seen_urls:
                    print(f"  ⏭️  Resolved URL already stored")
                    skipped_dup += 1
                    continue

                seen_urls.add(apply_url)
                urls_found += 1
                all_jobs.append({
                    "title":    title,
                    "company":  company,
                    "location": loc,
                    "url":      apply_url,
                    "industry": INDUSTRY,
                    "niche":    NICHE,
                    "source":   "linkedin_scrape",
                })
                print(f"  ✅ {apply_url}")

            await asyncio.sleep(random.uniform(1, 3))

        await browser.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"  Raw jobs scraped:             {total_raw}")
    print(f"  Skipped (duplicate):          {skipped_dup}")
    print(f"  Skipped (stale >30d):         {skipped_stale}")
    print(f"  Skipped (role):               {skipped_role}")
    print(f"  Skipped (senior):             {skipped_senior}")
    print(f"  Skipped (location):           {skipped_location}")
    print(f"  Skipped (staffing firm):      {skipped_staffing}")
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

    if all_jobs:
        save_to_db(all_jobs)
    else:
        print("  No jobs to commit.")


if __name__ == "__main__":
    asyncio.run(run())