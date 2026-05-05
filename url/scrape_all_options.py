import asyncio
import requests
import os
from playwright.async_api import async_playwright
from urllib.parse import urlparse, parse_qs, unquote, urlencode
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

AGGREGATORS = [
    "ziprecruiter.com",
    "simplyhired.com",
    "dice.com",
    "adzuna.com",
    "talentify.io",
    "jobright.ai",
    "tealhq.com",
    "spacetalent.org",
    "disabledperson.com",
    "fashionjobs.com",
    "joinrunway.io",
    "remotepositionshirings.com",
    "remotepulse",
    "hiringremotejobs.net",
    "entryleveljobs.me",
    "glassdoor.com",
    "indeed.com",
    "wellfound.com",
    "angel.co",
    "angellist.com",
    "jobzmall.com",
    "monster.com",
    "careerbuilder.com",
    "snagajob.com",
    "ladders.com",
    "salary.com",
    "builtin.com",
    "learn4good.com",
    "earnbetter.com",
    "thefreshdev.com",
    "jobgether.com",
    "jooble.org",
    "jobsora.com",
    "talent.com",
    "neuvoo.com",
    "jobrapido.com",
    "recruitnet.com",
    "career.com",
    "careerjet.com",
    "joblist.com",
    "jobsearch.com",
    "lensa.com",
    "whatjobs.com",
    "womenforhire.com",
    "sportstechjobs.com",
    "digitalhire.com",
    "jobg8.com",
    "moaijobs.com",
    "towardsai.net",
    "localjobnetwork.com",
    "diversityjobs.com",
    "weekday.works",
    "wayup.com",
    "bandana.com",
    "salaryguide.com",
    "bebee.com",
    "workopolis.com",
    "recruit.net",
    "jobs2careers.com",
    "stevenagefc.com",
    "ksnt.com",
    "kdvr.com",
    "jobabstracts.com",
    "workonward.com",
    "massmutualventures.com",
    "jobinabuja.com"
]

GOOD_PATTERNS = [
    "greenhouse.io",
    "lever.co",
    "myworkdayjobs.com",
    "avature.net",
    "icims.com",
    "taleo.net",
    "smartrecruiters.com",
    "jobvite.com",
    "ashbyhq.com",
    "breezy.hr",
    "paylocity.com",
    "recruitingbypaycor.com",
    "ultipro.com",
    "oraclecloud.com",
    "successfactors.com",
    "bamboohr.com",
    "workable.com",
    "recruitee.com",
    "pinpointhq.com",
    "careers.adobe.com",
    "careers.cisco.com",
    "careers.netapp.com",
    "careers.hpe.com",
    "careers.nutanix.com",
    "careers.garmin.com",
    "careers.l3harris.com",
    "careers.cushmanwakefield.com",
    "careers.marsh.com",
    "careers.steris.com",
    "careers.ryerson.com",
    "careers.apextoolgroup.com",
    "careers.arena.run",
    "careers.eisneramper.com",
    "careers.ace.aaa.com",
    "jobs.bostonscientific.com",
    "jobs.advanceautoparts.com",
    "jobs.deluxe.com",
    "jobs.saic.com",
    "jobs.ametek.com",
    "jobs.kwiktrip.com",
    "jobs.baesystems.com",
    "jobs.continental.com",
    "jobs.mercedes-benz.com",
    "jobs.myflorida.com",
    "jobs.ajg.com",
    "jobs.drivetime.com",
    "jobportal.reyesbeveragegroup.com",
    "jobportal.reyesholdings.com",
]


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
        "src", "source", "sourceType", "gh_src",
        "trk", "refId"
    ]
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    clean_params = {k: v for k, v in params.items() if k not in tracking_params}
    clean_query = urlencode({k: v[0] for k, v in clean_params.items()})
    return parsed._replace(query=clean_query).geturl()


async def extract_linkedin_url(page, linkedin_url: str) -> str | None:
    """Reusable — open a LinkedIn job page and extract the direct company apply URL."""
    try:
        await page.goto(linkedin_url, wait_until="networkidle", timeout=15000)
        links = await page.query_selector_all("a")
        for link in links:
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


async def get_apply_url(page, job: dict) -> str | None:
    apply_options = job.get("apply_options", [])
    title = job.get("title", "")
    company = job.get("company_name", "")

    # Method 1 — known good ATS URL directly in apply_options
    for option in apply_options:
        link = option.get("link", "")
        if link and is_good_url(link) and not is_aggregator(link):
            print(f"     Method 1 (direct ATS): {clean_url(link)}")
            return clean_url(link)

    # Method 2 — LinkedIn externalApply extraction via Playwright
    linkedin_url = next(
        (o["link"] for o in apply_options if "linkedin.com" in o.get("link", "")),
        None
    )
    if linkedin_url:
        url = await extract_linkedin_url(page, linkedin_url)
        if url:
            print(f"     Method 2 (LinkedIn extraction): {url}")
            return url

    # Method 3 — ZipRecruiter redirect
    zip_url = next(
        (o["link"] for o in apply_options if "ziprecruiter.com" in o.get("link", "")),
        None
    )
    if zip_url:
        try:
            await page.goto(zip_url, wait_until="networkidle", timeout=15000)
            final_url = page.url
            if not is_aggregator(final_url):
                print(f"     Method 3 (ZipRecruiter redirect): {clean_url(final_url)}")
                return clean_url(final_url)
        except Exception:
            pass

    # Method 4 — follow any aggregator link and see where it redirects
    for option in apply_options:
        link = option.get("link", "")
        if not link or "linkedin.com" in link or "ziprecruiter.com" in link:
            continue
        if not is_aggregator(link):
            continue
        try:
            await page.goto(link, wait_until="networkidle", timeout=15000)
            final_url = page.url
            if not is_aggregator(final_url) and urlparse(final_url).netloc != urlparse(link).netloc:
                print(f"     Method 4 (aggregator redirect): {clean_url(final_url)}")
                return clean_url(final_url)
            links_on_page = await page.query_selector_all("a")
            for a in links_on_page:
                try:
                    href = await a.get_attribute("href")
                    text = await a.inner_text()
                    if href and not is_aggregator(href) and any(
                        x in text.lower() for x in ["apply on", "apply at", "apply now", "company site"]
                    ):
                        print(f"     Method 4 (aggregator apply button): {clean_url(href)}")
                        return clean_url(href)
                except Exception:
                    continue
        except Exception:
            continue

    # Method 5 — Google Search last resort (fires even if apply_options existed)
    if title and company:
        search_query = f"{company} {title} careers apply"
        params = {
            "engine": "google",
            "q": search_query,
            "api_key": SERPAPI_KEY,
            "num": 5
        }
        try:
            response = requests.get("https://serpapi.com/search", params=params)
            data = response.json()
            organic = data.get("organic_results", [])
            for result in organic:
                link = result.get("link", "")
                if not link or is_aggregator(link):
                    continue
                if "linkedin.com" in link:
                    url = await extract_linkedin_url(page, link)
                    if url:
                        print(f"     Method 5 (Google → LinkedIn extraction): {url}")
                        return url
                    continue
                print(f"     Method 5 (Google Search): {clean_url(link)}")
                return clean_url(link)
        except Exception:
            pass

    return None


def fetch_google_jobs(query: str, pages: int = 3):
    """Fetch jobs with pagination using next_page_token. Default 3 pages = up to 30 results."""
    all_jobs = []
    next_page_token = None

    for page in range(pages):
        params = {
            "engine": "google_jobs",
            "q": query,
            "location": "United States",
            "hl": "en",
            "api_key": SERPAPI_KEY
        }
        if next_page_token:
            params["next_page_token"] = next_page_token

        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()

        if "error" in data:
            print(f"  Page {page + 1} error: {data['error']}")
            break

        jobs = data.get("jobs_results", [])
        if not jobs:
            print(f"  Page {page + 1} returned no results, stopping.")
            break

        print(f"  Page {page + 1}: {len(jobs)} jobs returned")
        all_jobs.extend(jobs)

        # Get token for next page
        next_page_token = data.get("serpapi_pagination", {}).get("next_page_token")
        if not next_page_token:
            print(f"  No more pages available.")
            break

    return all_jobs


async def process_jobs(jobs: list):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"\nProcessing {len(jobs)} jobs...\n")
        print("=" * 70)

        results = []

        for i, job in enumerate(jobs):
            title = job.get("title")
            company = job.get("company_name")
            location = clean_location(job.get("location", ""))

            print(f"[{i+1}] {title} @ {company} ({location})")

            company_url = await get_apply_url(page, job)

            if company_url:
                results.append({**job, "company_apply_url": company_url})
            else:
                print(f"     ❌ Skipping — no usable apply URL found")
            print()

        await browser.close()

        print("=" * 70)
        print(f"\nResults: {len(results)}/{len(jobs)} jobs have usable apply URLs")
        return results


if __name__ == "__main__":
    print("Fetching marketing internships (6 pages = up to 60 jobs)...\n")
    jobs = fetch_google_jobs("entry level marketing north carolina")
    print(f"\nTotal fetched: {len(jobs)} jobs")
    asyncio.run(process_jobs(jobs))