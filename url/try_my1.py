"""
pipeline_js.py
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
    "budget analyst", "CPA", "accounting graduate",
]

LOCATIONS = [
    "North Carolina",
    "Raleigh, NC",
    "Charlotte, NC",
    "Durham, NC",
    "Greensboro, NC",
    "Winston-Salem, NC",
    "Cary, NC",
    "Fayetteville, NC",
    "Wilmington, NC",
    "Asheville, NC", 
    "High Point, NC",
    "Chapel Hill, NC",
]

VALID_LOCATION_KEYWORDS = [
    "nc", "north carolina",
    "charlotte", "mooresville", "concord", "gastonia",
    "huntersville", "matthews", "fort mill", "rock hill",
    "kannapolis", "salisbury", "monroe", "albemarle",
    "hickory", "statesville", "davidson", "cornelius",
]

# ─── Classification Constants ─────────────────────────────────────────────────

ACCOUNTING_KEYWORDS = [
    "account", "accountant", "accounting", "bookkeep", "payroll",
    "audit", "tax", "billing", "budget", "cpa", "cma",
    "accounts payable", "accounts receivable", "gl ", "general ledger",
    "cost analyst", "revenue", "treasury", "fiscal", "ledger", "invoic",
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
    "key account"
]

SENIOR_TITLE_KEYWORDS = [
    "senior", "sr","sr ", "sr. ", " sr." " sr ", "sr.", " sr,", "(sr)", "sr-", "principal", "director",
    "manager", "head of", "vp ", "vice president", "chief", "executive",
    "supervisor", "lead ", " iii", " iv", " v ", " ii", " 2", " 3", " 4", " 5",
    "midlevel", "mid-level"
    # C-suite abbreviations
    "cfo", "ceo", "coo", "cto", "cpo",
    # Fractional roles are always senior hires
    "fractional",
    # Controller roles are senior
    "controller",
    # Seasonal roles are temporary gigs, not entry-level career jobs
    "seasonal", "part-time", "part time", "parttime",
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
# Checked FIRST — before company name matching — so token collisions
# can never sneak a staffing firm or job board through.

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
    "lhh.com", "talentally.com", "jobot.com", "accentuatestaffing.com", 
    "astoncarter.com",
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
# Words so common in finance/accounting titles that they can't count as
# meaningful overlap between a scraped title and a URL slug.

GENERIC_TITLE_WORDS = {
    "analyst", "accountant", "manager", "associate", "specialist",
    "coordinator", "director", "assistant", "officer", "lead",
    "senior", "junior", "staff", "remote", "job", "jobs", "careers",
    "work", "home", "from", "team", "global", "north", "south",
    "east", "west", "united", "states", "americas", "apply", "view",
    "detail", "posting", "opening", "position", "role", "opportunity",
    "clerk", "technician", "representative", "administrator",
}

# Seniority tokens that, if found in the URL slug, trigger rejection
# regardless of what the scraped title says.
SENIOR_URL_KEYWORDS = {
    "senior", "sr", "lead", "principal", "director", "vp", "head",
    "chief", "manager", "supervisor", "superintendent", "president",
    "controller",
}

# ─── Company Name Normalization ───────────────────────────────────────────────

COMPANY_NAME_NOISE = {
    "inc", "llc", "ltd", "corp", "corporation", "company", "companies",
    "group", "usa", "us", "the", "and", "solutions", "services",
    "associates", "partners", "co", "international", "global",
    "holdings", "enterprises", "technologies", "technology",
    "consulting", "management", "resources", "staffing", "systems",
}


def normalize_company_tokens(company: str) -> list[str]:
    cleaned = re.sub(r"[^\w\s]", "", company.lower())
    tokens = [t for t in cleaned.split() if t not in COMPANY_NAME_NOISE and len(t) > 2]
    if len(tokens) >= 2:
        tokens.append(tokens[0] + tokens[1])
    return tokens


# ─── Role Filters ─────────────────────────────────────────────────────────────

def is_accounting_role(title: str) -> bool:
    title_lower = title.lower()
    if any(job in title_lower for job in ACCOUNTING_KEYWORDS):
        if not any(excl in title_lower for excl in NON_ACCOUNTING_TITLES):
            return True
    return False


def is_senior_found(title: str) -> bool:
    title_lower = title.lower()
    if any(job in title_lower for job in SENIOR_TITLE_KEYWORDS):
        return False
    return True


def is_nc_found(location: str) -> bool:
    location_lower = location.lower()
    if any(kw in location_lower for kw in VALID_LOCATION_KEYWORDS):
        return True
    return False


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
    """
    Pull the last readable path segment from a URL and split into words.
    Returns an empty set when the slug is a pure opaque ID (Taleo, Workday
    numeric IDs, UUIDs, etc.) — those get a free pass since there's nothing
    to compare against.
    """
    path = urlparse(url).path.lower()
    segments = [s for s in path.split("/") if s]
    if not segments:
        return set()

    # Walk from the end to find the first segment that looks like a title slug
    # (contains at least one alpha run of 3+ characters separated by dashes)
    for segment in reversed(segments):
        # Strip file extensions
        segment = re.sub(r"\.\w{2,4}$", "", segment)
        words = re.split(r"[-_]", segment)
        alpha_words = [w for w in words if re.search(r"[a-z]{3,}", w)]
        if len(alpha_words) >= 2:
            return set(alpha_words)

    return set()


def title_matches_url(title: str, url: str) -> bool:
    """
    Returns True if the URL slug is consistent with the scraped job title.
    Returns False (reject) when:
      1. The URL slug contains a seniority keyword (e.g. "senior", "sr", "lead")
         regardless of what the title says — catches cases where the title was
         scraped incorrectly but the URL reveals the true level.
      2. The URL slug has readable title words but none of the non-generic words
         overlap with the scraped title — catches completely wrong job associations
         like "General Ledger Analyst" linked to a "Senior-Financial-Analyst" URL.

    URLs with opaque slugs (pure IDs, Taleo, etc.) always return True since
    there is nothing to compare.
    """
    slug_words = _extract_slug_words(url)

    # No readable slug — give benefit of the doubt
    if not slug_words:
        return True

    # ── Check 1: seniority in URL slug ───────────────────────────────────────
    if slug_words & SENIOR_URL_KEYWORDS:
        senior_hit = slug_words & SENIOR_URL_KEYWORDS
        print(f"  ⚠️  URL slug contains seniority keyword(s): {senior_hit}")
        return False

    # ── Check 2: specific-word overlap ───────────────────────────────────────
    title_words = set(re.split(r"[\s\-_,]", title.lower()))

    slug_specific  = slug_words  - GENERIC_TITLE_WORDS
    title_specific = title_words - GENERIC_TITLE_WORDS

    # If the slug is entirely generic words we can't determine anything useful
    if not slug_specific:
        return True

    overlap = slug_specific & title_specific
    if not overlap:
        print(f"  ⚠️  Title/URL mismatch — slug: {slug_specific} | title: {title_specific}")
        return False

    return True


# ─── Serper Fallback ──────────────────────────────────────────────────────────

def serper_find_apply_url(title: str, company: str, location: str) -> str | None:
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

                # ── Sanity check ──────────────────────────────────────────────
                if not title or not job_url or job_url == "nan":
                    continue
                if not company or company.lower() == "nan":
                    skipped_role += 1
                    continue

                # ── Source URL dedup ──────────────────────────────────────────
                if job_url in seen_urls:
                    skipped_dup += 1
                    continue
                seen_urls.add(job_url)

                print(f"\n  {title!r} @ {company} ({job_loc})")

                # ── 1. Accounting role check ──────────────────────────────────
                if not is_accounting_role(title):
                    print(f"  ⏭️  Not an accounting role")
                    skipped_role += 1
                    continue

                # ── 2. Senior check ───────────────────────────────────────────
                if not is_senior_found(title):
                    print(f"  ⏭️  Senior title")
                    skipped_senior += 1
                    continue

                # ── 3. Location check ─────────────────────────────────────────
                if not is_nc_found(job_loc):
                    print(f"  ⏭️  Not NC: {job_loc!r}")
                    skipped_location += 1
                    continue

                # ── 4. Title + company dedup ──────────────────────────────────
                job_key = (title.lower(), company.lower())
                if job_key in seen_jobs:
                    print(f"  ⏭️  Already stored")
                    skipped_dup += 1
                    continue
                seen_jobs.add(job_key)

                # ── 5. URL validation ─────────────────────────────────────────
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

                # ── 6. URL title validation ───────────────────────────────────
                if not title_matches_url(title, apply_url):
                    print(f"  ❌ Title/URL mismatch — discarding")
                    skipped_url_title += 1
                    continue

                # ── 7. Resolved URL dedup ─────────────────────────────────────
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
    print(f"  Raw jobs scraped:            {total_raw}")
    print(f"  Skipped (duplicate):         {skipped_dup}")
    print(f"  Skipped (role):              {skipped_role}")
    print(f"  Skipped (senior):            {skipped_senior}")
    print(f"  Skipped (location):          {skipped_location}")
    print(f"  Skipped (no valid URL):      {skipped_no_url}")
    print(f"  Skipped (title/URL mismatch):{skipped_url_title}")
    print(f"  {'─' * 35}")
    print(f"  Jobs stored (clean URLs):    {urls_found}")
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