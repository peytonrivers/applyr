import asyncio
import requests
from datetime import datetime
from jobspy import scrape_jobs
from playwright.async_api import async_playwright
from urllib.parse import urlparse, parse_qs, unquote, urlencode

# ─── Config ────────────────────────────────────────────────────────────────────

STATE        = "North Carolina"
STATE_ABBR   = "NC"
QUERIES      = ["software engineer", "accountant"]
RESULTS_EACH = 10

# ─── Senior Signals (title must NOT contain any of these) ─────────────────────

SENIOR_SIGNALS = [
    # Seniority / Experience Level
    "Senior", "Sr.", "Sr ", "Lead", "Principal", "Staff", "Distinguished",
    "Fellow", "Director", "Manager", "Head of", "VP", "Vice President",
    "Chief", "C-Suite", "CTO", "CFO", "CEO", "COO", "CIO", "SVP", "EVP",
    "AVP", "Partner", "Associate Director", "Managing Director", "Executive",

    # Mid-Level Indicators
    "Mid-Level", "Mid Level", "Experienced", "Seasoned", "Specialist",
    "Architect", "Expert",

    # Year/Experience Requirements
    "3+ years", "4+ years", "5+ years", "6+ years", "7+ years", "8+ years",
    "9+ years", "10+ years", "3-5 years", "4-6 years", "5-7 years",
    "5-10 years", "minimum 3", "minimum 4", "minimum 5", "at least 3",
    "at least 4", "at least 5", "3 years of experience",
    "4 years of experience", "5 years of experience",

    # Role Prefixes/Suffixes That Signal Seniority
    " II", " III", " IV", "Level 2", "Level 3", "L3", "L4", "L5", "L6",
    "Tier 2", "Tier 3", "Grade 2", "Grade 3",

    # Internship / Student
    "Intern", "Internship", "Co-op", "Coop", "Co op", "Student",
    "Apprentice", "Trainee", "Temporary", "Temp ", "Contract",
    "Freelance", "Part-time", "Part time",
]

# ─── Aggregators + Tracking URLs to Filter Out ────────────────────────────────

AGGREGATORS = [
    # Major Job Boards
    "ziprecruiter.com", "indeed.com", "glassdoor.com",
    "monster.com", "careerbuilder.com", "simplyhired.com", "dice.com",
    "wellfound.com", "salary.com", "lensa.com", "talent.com",
    "jooble.org", "careerjet.com", "wayup.com", "snagajob.com",
    "nexxt.com", "theladders.com", "hired.com", "joblist.com",
    "jobsearch.com", "jobs.com", "jobrapido.com", "jobsonline.com",
    "adzuna.com", "neuvoo.com", "trovit.com", "mitula.com",
    "bebee.com", "jobcase.com", "jobleads.com", "jobscore.com",

    # Niche / Specialized Boards
    "internships.com", "internmatch.com", "chegg.com", "looksharp.com",
    "college-recruiter.com", "aftercollege.com", "campusreel.org",
    "idealist.org", "philanthropy.com", "devex.com", "clearancejobs.com",
    "usajobs.gov", "governmentjobs.com", "publicjobs.com",
    "healthcarejobsite.com", "healthjobsnationwide.com", "nursejobs.com",
    "lawjobs.com", "legalstaff.com", "mediabistro.com",
    "journalismjobs.com", "authenticjobs.com", "dribbble.com",
    "coroflot.com", "behance.net", "remoteok.com", "weworkremotely.com",
    "remote.co", "flexjobs.com", "remotive.io", "justremote.co",
    "nodesk.co", "pangian.com",

    # ATS / Recruiting Platforms (tracking/apply URLs)
    "jometer.com", "talemetry.com", "joveo.com", "apploi.com",
    "contacthr.com", "jobsync.io", "appone.com", "trakstar.com",
    "recruitics.com", "jobvite.com", "icims.com", "taleo.net",
    "successfactors.com", "successfactors.eu", "brassring.com",
    "kenexa.com", "silkroad.com", "ultipro.com", "kronos.com",
    "adp.com", "paychex.com", "bamboohr.com", "smartrecruiters.com",
    "recruiterbox.com", "freshteam.com", "pinpointhq.com",
    "workable.com", "teamtailor.com", "occupop.com", "recruitee.com",
    "dover.com", "ashbyhq.com", "rippling.com", "jazz.co",
    "jazzhr.com", "hiringthing.com", "crelate.com", "bullhorn.com",
    "pcrecruiter.net", "zohorecruit.com", "manatalhr.com",
    "loxo.co", "vincere.io", "avionteq.com", "jobadder.com",
    "catsone.com", "jobdiva.com", "erecruit.com", "jobscience.com",

    # Aggregator Networks / Programmatic
    "appcast.io", "broadbean.com", "multiposting.fr", "talentfunnel.com",
    "jobg8.com", "jobisjob.com", "jobbird.com", "jobsora.com",
    "jobbled.com", "jobsatlas.com", "workcircle.com", "ework.com",
    "jobsinnetwork.com", "jobsintheuk.com", "jobsite.co.uk",
    "totaljobs.com", "reed.co.uk", "cwjobs.co.uk", "jobs.ie",

    # Staffing / Temp Agencies
    "roberthalf.com", "manpower.com", "adecco.com", "kellyservices.com",
    "spherion.com", "randstad.com", "staffmark.com", "aerotek.com",
    "insight-global.com", "insightglobal.com", "teksystems.com",
    "kforce.com", "cybercoders.com", "hays.com", "michaelpage.com",
    "pagegroup.com", "executivesearch.com",
]

# ─── Greenhouse Companies ──────────────────────────────────────────────────────

GREENHOUSE_COMPANIES = [
    "stripe", "airbnb", "doordash", "reddit", "notion",
    "figma", "brex", "rippling", "gusto", "mercury",
    "plaid", "robinhood", "chime", "coinbase", "databricks",
    "capitalone", "ally", "truist", "lendingclub", "sofi",
    "atriumhealth", "wakemed", "labcorp", "novant",
    "cisco", "ibm", "sas", "redhat", "lenovo",
    "bancorpsouth", "firstcitizensbank", "bbandt",
]

# ─── Lever Companies ──────────────────────────────────────────────────────────

LEVER_COMPANIES = [
    "netflix", "shopify", "lyft", "canva", "atlassian",
    "zendesk", "intercom", "segment", "amplitude", "linear",
    "vercel", "loom", "lattice", "clubhouse", "figma",
    "betterment", "wealthfront", "acorns", "stash",
    "twilio", "sendgrid", "cloudflare", "fastly",
    "spreedly", "pendo", "bandwidth",
]

# ─── Helpers ───────────────────────────────────────────────────────────────────

def is_aggregator(url: str) -> bool:
    return any(agg in url.lower() for agg in AGGREGATORS)

def clean_url(url: str) -> str:
    tracking_params = [
        "utm_source", "utm_medium", "utm_campaign",
        "src", "source", "sourceType", "gh_src", "trk",
        "refId", "cmpid", "publisher", "rb", "postedDate",
    ]
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    clean_params = {k: v for k, v in params.items() if k not in tracking_params}
    clean_query = urlencode({k: v[0] for k, v in clean_params.items()})
    return parsed._replace(query=clean_query).geturl()

def is_not_senior(title: str) -> bool:
    """Returns True if the job title does NOT contain senior signals."""
    title_lower = title.lower()
    return not any(signal in title_lower for signal in SENIOR_SIGNALS)

def is_in_state(location: str) -> bool:
    if not location:
        return False
    loc = location.lower()
    return (
        STATE.lower() in loc or
        f", {STATE_ABBR.lower()}" in loc or
        f" {STATE_ABBR.lower()}," in loc or
        f" {STATE_ABBR.lower()} " in loc or
        loc.endswith(f" {STATE_ABBR.lower()}")
    )

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ─── Source 1: JobSpy ──────────────────────────────────────────────────────────

def fetch_jobspy(query: str) -> list[dict]:
    log(f"  JobSpy → '{query}' in {STATE}")
    results = []

    try:
        jobs = scrape_jobs(
            site_name=["indeed", "zip_recruiter", "google"],
            search_term=query,
            location=STATE,
            results_wanted=RESULTS_EACH,
            hours_old=72,
            country_indeed="USA",
        )

        for _, job in jobs.iterrows():
            title     = str(job.get("title", ""))
            company   = str(job.get("company", ""))
            location  = str(job.get("location", ""))
            apply_url = str(job.get("job_url_direct") or job.get("job_url") or "")

            if not apply_url or apply_url == "nan":
                continue
            if is_aggregator(apply_url):
                continue
            if not is_in_state(location):
                continue
            if not is_not_senior(title):
                continue

            results.append({
                "source":    f"jobspy/{job.get('site', '')}",
                "title":     title,
                "company":   company,
                "location":  location,
                "apply_url": clean_url(apply_url),
                "salary":    f"${job.get('min_amount')} - ${job.get('max_amount')}"
                             if job.get("min_amount") else "",
            })

    except Exception as e:
        log(f"  ❌ JobSpy error: {e}")

    log(f"  JobSpy → {len(results)} jobs passed filters")
    return results

# ─── Source 2: LinkedIn ────────────────────────────────────────────────────────

async def fetch_linkedin(page, query: str) -> list[dict]:
    log(f"  LinkedIn → '{query}' in {STATE}")
    results = []

    search_url = (
        f"https://www.linkedin.com/jobs/search"
        f"?keywords={query.replace(' ', '+')}"
        f"&location={STATE.replace(' ', '%20')}"
        f"&f_E=1,2"        # experience: internship + entry level
        f"&f_TPR=r259200"  # last 3 days
    )

    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(3)

        for _ in range(2):
            await page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(1)

        job_urls = []
        links = await page.query_selector_all("a")
        for link in links:
            try:
                href = await link.get_attribute("href")
                if href and "/jobs/view/" in href:
                    clean = (
                        "https://www.linkedin.com" + href.split("?")[0]
                        if href.startswith("/")
                        else href.split("?")[0]
                    )
                    if clean not in job_urls:
                        job_urls.append(clean)
                        if len(job_urls) >= RESULTS_EACH:
                            break
            except Exception:
                continue

        for job_url in job_urls:
            try:
                await page.goto(job_url, wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(2)

                title = company = location = ""

                try:
                    el = await page.query_selector("h1")
                    title = (await el.inner_text()).strip() if el else ""
                except Exception:
                    pass

                try:
                    el = await page.query_selector(".topcard__org-name-link")
                    company = (await el.inner_text()).strip() if el else ""
                except Exception:
                    pass

                try:
                    el = await page.query_selector(".topcard__flavor--bullet")
                    location = (await el.inner_text()).strip() if el else ""
                except Exception:
                    pass

                if not is_not_senior(title):
                    continue

                apply_url = None
                for link in await page.query_selector_all("a"):
                    try:
                        href = await link.get_attribute("href")
                        if href and "externalApply" in href:
                            parsed = urlparse(href)
                            params = parse_qs(parsed.query)
                            if "url" in params:
                                candidate = clean_url(unquote(params["url"][0]))
                                if not is_aggregator(candidate):
                                    apply_url = candidate
                                    break
                    except Exception:
                        continue

                if not apply_url:
                    continue

                results.append({
                    "source":    "linkedin",
                    "title":     title,
                    "company":   company,
                    "location":  location,
                    "apply_url": apply_url,
                    "salary":    "",
                })

            except Exception:
                continue

    except Exception as e:
        log(f"  ❌ LinkedIn error: {e}")

    log(f"  LinkedIn → {len(results)} jobs passed filters")
    return results

# ─── Source 3: Greenhouse ──────────────────────────────────────────────────────

def fetch_greenhouse(query: str) -> list[dict]:
    log(f"  Greenhouse → '{query}'")
    results = []

    for company in GREENHOUSE_COMPANIES:
        try:
            url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
            response = requests.get(url, timeout=8)
            if response.status_code != 200:
                continue

            for job in response.json().get("jobs", []):
                title     = job.get("title", "")
                location  = job.get("location", {}).get("name", "")
                apply_url = job.get("absolute_url", "")

                if not apply_url:
                    continue
                if not is_not_senior(title):
                    continue
                if not is_in_state(location):
                    continue
                if query.lower() not in title.lower():
                    continue

                results.append({
                    "source":    "greenhouse",
                    "title":     title,
                    "company":   company.capitalize(),
                    "location":  location,
                    "apply_url": clean_url(apply_url),
                    "salary":    "",
                })

        except Exception:
            continue

    log(f"  Greenhouse → {len(results)} jobs passed filters")
    return results

# ─── Source 4: Lever ──────────────────────────────────────────────────────────

def fetch_lever(query: str) -> list[dict]:
    log(f"  Lever → '{query}'")
    results = []

    for company in LEVER_COMPANIES:
        try:
            url = f"https://api.lever.co/v0/postings/{company}?mode=json"
            response = requests.get(url, timeout=8)
            if response.status_code != 200:
                continue

            for job in response.json():
                title     = job.get("text", "")
                location  = job.get("categories", {}).get("location", "")
                apply_url = job.get("hostedUrl", "")

                if not apply_url:
                    continue
                if not is_not_senior(title):
                    continue
                if not is_in_state(location):
                    continue
                if query.lower() not in title.lower():
                    continue

                results.append({
                    "source":    "lever",
                    "title":     title,
                    "company":   company.capitalize(),
                    "location":  location,
                    "apply_url": clean_url(apply_url),
                    "salary":    "",
                })

        except Exception:
            continue

    log(f"  Lever → {len(results)} jobs passed filters")
    return results

# ─── Deduplication ─────────────────────────────────────────────────────────────

def deduplicate(jobs: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for job in jobs:
        url = job["apply_url"]
        if url not in seen:
            seen.add(url)
            unique.append(job)
    return unique

# ─── Main ──────────────────────────────────────────────────────────────────────

async def main():
    all_results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        for query in QUERIES:
            print(f"\n{'=' * 60}")
            print(f"  Query: {query} | {STATE}")
            print(f"{'=' * 60}")

            jobspy_results     = fetch_jobspy(query)
            linkedin_results   = await fetch_linkedin(page, query)
            greenhouse_results = fetch_greenhouse(query)
            lever_results      = fetch_lever(query)

            combined = (
                jobspy_results +
                linkedin_results +
                greenhouse_results +
                lever_results
            )

            unique = deduplicate(combined)
            all_results.extend(unique)

            print(f"\n  Results for '{query}':")
            print(f"  JobSpy:     {len(jobspy_results)}")
            print(f"  LinkedIn:   {len(linkedin_results)}")
            print(f"  Greenhouse: {len(greenhouse_results)}")
            print(f"  Lever:      {len(lever_results)}")
            print(f"  Unique:     {len(unique)}")

        await browser.close()

    print(f"\n{'=' * 60}")
    print(f"  TOTAL: {len(all_results)} jobs in {STATE}")
    print(f"{'=' * 60}\n")

    for job in all_results:
        print(f"  [{job['source']}] {job['title']} @ {job['company']}")
        print(f"  Location  : {job['location']}")
        if job["salary"]:
            print(f"  Salary    : {job['salary']}")
        print(f"  Apply URL : {job['apply_url']}")
        print()

if __name__ == "__main__":
    asyncio.run(main())