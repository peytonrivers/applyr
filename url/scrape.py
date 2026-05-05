import asyncio
import requests
import os
from playwright.async_api import async_playwright
from urllib.parse import urlparse, parse_qs, unquote, urlencode
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# ─── URL Classification ────────────────────────────────────────────────────────

AGGREGATORS = [
    "ziprecruiter.com", "simplyhired.com", "dice.com", "adzuna.com",
    "talentify.io", "jobright.ai", "tealhq.com", "spacetalent.org",
    "disabledperson.com", "fashionjobs.com", "joinrunway.io",
    "remotepositionshirings.com", "remotepulse", "hiringremotejobs.net",
    "entryleveljobs.me", "glassdoor.com", "indeed.com", "wellfound.com",
    "angel.co", "angellist.com", "jobzmall.com", "monster.com",
    "careerbuilder.com", "snagajob.com", "ladders.com", "salary.com",
    "builtin.com", "learn4good.com", "earnbetter.com", "thefreshdev.com",
    "jobgether.com", "jooble.org", "jobsora.com", "talent.com",
    "neuvoo.com", "jobrapido.com", "recruitnet.com", "career.com",
    "careerjet.com", "joblist.com", "jobsearch.com", "lensa.com",
    "whatjobs.com", "womenforhire.com", "sportstechjobs.com",
    "digitalhire.com", "jobg8.com", "moaijobs.com", "towardsai.net",
    "localjobnetwork.com", "diversityjobs.com", "weekday.works",
    "wayup.com", "bandana.com", "salaryguide.com", "bebee.com",
    "workopolis.com", "recruit.net", "jobs2careers.com", "stevenagefc.com",
    "ksnt.com", "kdvr.com", "jobabstracts.com", "workonward.com",
    "massmutualventures.com", "jobinabuja.com",
]

GOOD_PATTERNS = [
    "greenhouse.io", "lever.co", "myworkdayjobs.com", "avature.net",
    "icims.com", "taleo.net", "smartrecruiters.com", "jobvite.com",
    "ashbyhq.com", "breezy.hr", "paylocity.com", "recruitingbypaycor.com",
    "ultipro.com", "oraclecloud.com", "successfactors.com", "bamboohr.com",
    "workable.com", "recruitee.com", "pinpointhq.com",
    "careers.adobe.com", "careers.cisco.com", "careers.netapp.com",
    "careers.hpe.com", "careers.nutanix.com", "careers.garmin.com",
    "careers.l3harris.com", "careers.cushmanwakefield.com",
    "careers.marsh.com", "careers.steris.com", "careers.ryerson.com",
    "careers.apextoolgroup.com", "careers.arena.run",
    "careers.eisneramper.com", "careers.ace.aaa.com",
    "jobs.bostonscientific.com", "jobs.advanceautoparts.com",
    "jobs.deluxe.com", "jobs.saic.com", "jobs.ametek.com",
    "jobs.kwiktrip.com", "jobs.baesystems.com", "jobs.continental.com",
    "jobs.mercedes-benz.com", "jobs.myflorida.com", "jobs.ajg.com",
    "jobs.drivetime.com", "jobportal.reyesbeveragegroup.com",
    "jobportal.reyesholdings.com",
]

# ─── URL Quality Signals ───────────────────────────────────────────────────────

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

GENERIC_URL_ENDINGS = [
    "/careers", "/careers/", "/jobs", "/jobs/", "/internships",
    "/internships/", "/career-opportunities", "/career-opportunities/",
    "/work-with-us", "/work-with-us/", "/join-us", "/join-us/",
    "/job-search", "/openings", "/openings/", "/join-our-team",
    "/join-our-team/", "/about-royal/careers/internships",
    "/about-your-bank/work-with-us/careers/students.html",
]

GENERIC_PAGE_SIGNALS = [
    "search jobs", "filter jobs", "all open positions", "browse jobs",
    "view all jobs", "see all openings", "explore careers",
    "find your next role", "job search results",
]


# ─── Helpers ───────────────────────────────────────────────────────────────────

def is_aggregator(url: str) -> bool:
    return any(agg in url for agg in AGGREGATORS)


def is_good_url(url: str) -> bool:
    return any(pattern in url for pattern in GOOD_PATTERNS)


def clean_location(location: str) -> str:
    if not location:
        return ""
    cleaned = location.encode("ascii", "ignore").decode("ascii")
    parts = [part.strip() for part in cleaned.split(",") if part.strip()]
    return ", ".join(parts) if parts else ""


def clean_url(url: str) -> str:
    tracking_params = [
        "utm_source", "utm_medium", "utm_campaign",
        "src", "source", "sourceType", "gh_src", "trk", "refId",
    ]
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    clean_params = {k: v for k, v in params.items() if k not in tracking_params}
    clean_query = urlencode({k: v[0] for k, v in clean_params.items()})
    return parsed._replace(query=clean_query).geturl()


def is_generic_url(url: str) -> bool:
    """Returns True if URL looks like a careers homepage rather than a specific job listing."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/").lower()
    for ending in GENERIC_URL_ENDINGS:
        if path.endswith(ending.rstrip("/")):
            return True
    # Specific jobs almost always have IDs, slugs, or longer paths
    if len(path.split("/")) <= 2 and not parsed.query:
        return True
    return False


# ─── URL Quality Check ─────────────────────────────────────────────────────────

async def check_url_quality(page, url: str) -> dict:
    """
    Returns { is_active: bool, reason: str }.
    Runs a fast HTTP check first, then a Playwright content scan.
    """
    if is_generic_url(url):
        return {"is_active": False, "reason": "Generic career page — not a specific job listing"}

    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code in [400, 403, 404, 410]:
            return {"is_active": False, "reason": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"is_active": False, "reason": f"HTTP request failed: {str(e)}"}

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2000)
        content = (await page.content()).lower()

        for signal in DEAD_SIGNALS:
            if signal in content:
                return {"is_active": False, "reason": f"Dead signal: '{signal}'"}

        generic_count = sum(1 for s in GENERIC_PAGE_SIGNALS if s in content)
        if generic_count >= 2:
            return {"is_active": False, "reason": f"Generic listing page ({generic_count} signals)"}

        if any(s in content for s in LIVE_SIGNALS):
            return {"is_active": True, "reason": "Live signal confirmed"}

        return {"is_active": True, "reason": "No dead signals (unconfirmed — review recommended)"}

    except Exception as e:
        msg = str(e)
        if "download" in msg.lower():
            return {"is_active": False, "reason": "Non-HTML content (PDF or download)"}
        return {"is_active": False, "reason": f"Playwright error: {msg[:100]}"}


# ─── Platform Extractors ───────────────────────────────────────────────────────

async def extract_linkedin_url(page, linkedin_url: str) -> str | None:
    """Navigate to a LinkedIn job page and extract the direct company apply URL."""
    try:
        await page.goto(linkedin_url, wait_until="networkidle", timeout=15000)
        for link in await page.query_selector_all("a"):
            try:
                href = await link.get_attribute("href")
                if href and "externalApply" in href:
                    parsed = urlparse(href)
                    params = parse_qs(parsed.query)
                    if "url" in params:
                        return clean_url(unquote(params["url"][0]))
            except Exception:
                continue
    except Exception:
        pass
    return None


async def extract_indeed_url(page, indeed_url: str) -> str | None:
    """
    Navigate to an Indeed job page and extract the direct company apply URL.
    Indeed wraps external apply links — we look for non-aggregator hrefs
    that appear near the apply button area.
    """
    try:
        await page.goto(indeed_url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2000)

        # Indeed often has an "Apply on company site" button with an external href
        for link in await page.query_selector_all("a"):
            try:
                href = await link.get_attribute("href")
                text = (await link.inner_text()).lower().strip()
                if not href:
                    continue
                # Skip anything pointing back to Indeed or an aggregator
                if "indeed.com" in href or is_aggregator(href):
                    continue
                # Must look like an external apply action
                if any(kw in text for kw in ["apply on", "apply at", "company site", "apply now", "apply"]):
                    return clean_url(href)
            except Exception:
                continue

        # Fallback: scan all links for known good ATS patterns
        for link in await page.query_selector_all("a"):
            try:
                href = await link.get_attribute("href")
                if href and is_good_url(href) and not is_aggregator(href):
                    return clean_url(href)
            except Exception:
                continue

    except Exception:
        pass
    return None


# ─── Core Resolver ─────────────────────────────────────────────────────────────

async def get_apply_url(page, job: dict, state: dict) -> str | None:
    """
    Try each method in order. After resolving a candidate URL, validate it
    with check_url_quality before returning — skip dead URLs and keep trying.

    state: shared dict across all jobs. Tracks:
        - method4_used (bool): limits the paid Google Search call to one use per run.
    """
    apply_options = job.get("apply_options", [])
    title = job.get("title", "")
    company = job.get("company_name", "")

    async def validate(url: str, label: str) -> str | None:
        """Run quality check on a candidate URL. Return it if alive, None if dead."""
        result = await check_url_quality(page, url)
        if result["is_active"]:
            print(f"     ✅ {label}: {url}")
            return url
        else:
            print(f"     ⚠️  {label} rejected — {result['reason']}")
            return None

    # ── Method 1: Known good ATS URL directly in apply_options ────────────────
    for option in apply_options:
        link = option.get("link", "")
        if link and is_good_url(link) and not is_aggregator(link):
            result = await validate(clean_url(link), "Method 1 (direct ATS)")
            if result:
                return result

    # ── Method 2: LinkedIn externalApply extraction ────────────────────────────
    linkedin_url = next(
        (o["link"] for o in apply_options if "linkedin.com" in o.get("link", "")),
        None,
    )
    if linkedin_url:
        url = await extract_linkedin_url(page, linkedin_url)
        if url:
            result = await validate(url, "Method 2 (LinkedIn extraction)")
            if result:
                return result

    # ── Method 3: Indeed external apply extraction ─────────────────────────────
    indeed_url = next(
        (o["link"] for o in apply_options if "indeed.com" in o.get("link", "")),
        None,
    )
    if indeed_url:
        url = await extract_indeed_url(page, indeed_url)
        if url:
            result = await validate(url, "Method 3 (Indeed extraction)")
            if result:
                return result

    # ── Method 4: Google Search fallback ──────────────────────────────────────
    # Limited to one use per run — each call costs a SerpAPI credit.
    if state.get("method4_used"):
        print("     ⏭️  Method 4 skipped — already used once this run")
        return None

    if title and company:
        params = {
            "engine": "google",
            "q": f"{company} {title} careers apply",
            "api_key": SERPAPI_KEY,
            "num": 5,
        }
        try:
            state["method4_used"] = True
            data = requests.get("https://serpapi.com/search", params=params).json()
            for result in data.get("organic_results", []):
                link = result.get("link", "")
                if not link or is_aggregator(link):
                    continue

                if "linkedin" in link:
                    url = await extract_linkedin_url(page, link)
                    if url:
                        validated = await validate(url, "Method 4 (Google → LinkedIn)")
                        if validated:
                            return validated
                    continue

                if "indeed" in link:
                    url = await extract_indeed_url(page, link)
                    if url:
                        validated = await validate(url, "Method 4 (Google → Indeed)")
                        if validated:
                            return validated
                    continue

                validated = await validate(clean_url(link), "Method 4 (Google Search)")
                if validated:
                    return validated

        except Exception:
            pass

    return None


# ─── SerpAPI Fetcher ───────────────────────────────────────────────────────────

def fetch_google_jobs(query: str, pages: int = 3) -> list:
    """Fetch jobs with pagination via next_page_token. Default 3 pages = up to 30 results."""
    all_jobs = []
    next_page_token = None

    for page in range(pages):
        params = {
            "engine": "google_jobs",
            "q": query,
            "location": "United States",
            "hl": "en",
            "api_key": SERPAPI_KEY,
        }
        if next_page_token:
            params["next_page_token"] = next_page_token

        data = requests.get("https://serpapi.com/search", params=params).json()

        if "error" in data:
            print(f"  Page {page + 1} error: {data['error']}")
            break

        jobs = data.get("jobs_results", [])
        if not jobs:
            print(f"  Page {page + 1} returned no results, stopping.")
            break

        print(f"  Page {page + 1}: {len(jobs)} jobs")
        all_jobs.extend(jobs)

        next_page_token = data.get("serpapi_pagination", {}).get("next_page_token")
        if not next_page_token:
            print("  No more pages.")
            break

    return all_jobs


# ─── Main Processor ────────────────────────────────────────────────────────────

async def process_jobs(jobs: list) -> list:
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

        print(f"\nProcessing {len(jobs)} jobs...\n" + "=" * 70)
        results = []

        for i, job in enumerate(jobs):
            title = job.get("title")
            company = job.get("company_name")
            location = clean_location(job.get("location", ""))
            print(f"\n[{i+1}] {title} @ {company} ({location})")

            state = {"method4_used": False}  # reset per job — Method 4 allowed once per URL
            apply_url = await get_apply_url(page, job, state)

            if apply_url:
                results.append({**job, "company_apply_url": apply_url})
            else:
                print("     ❌ Skipping — no usable apply URL found")

        await browser.close()

        print("\n" + "=" * 70)
        print(f"Results: {len(results)}/{len(jobs)} jobs have usable apply URLs")
        return results


# ─── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Fetching entry level marketing jobs in North Carolina (3 pages = up to 30 results)...\n")
    jobs = fetch_google_jobs("linkedin marketing north carolina")
    print(f"\nTotal fetched: {len(jobs)} jobs")
    asyncio.run(process_jobs(jobs))