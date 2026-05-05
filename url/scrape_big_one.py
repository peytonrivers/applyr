import asyncio
import requests
import os
from playwright.async_api import async_playwright
from urllib.parse import urlparse, parse_qs, unquote
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Aggregators we never want to use
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
]

# Known good ATS / careers URL patterns
GOOD_PATTERNS = [
    "greenhouse.io",
    "lever.co",
    "workday.com",
    "myworkdayjobs.com",
    "avature.net",
    "icims.com",
    "taleo.net",
    "smartrecruiters.com",
    "jobvite.com",
    "careers.",
    "jobs.",
]


def is_aggregator(url: str) -> bool:
    return any(agg in url for agg in AGGREGATORS)


def is_good_url(url: str) -> bool:
    return any(pattern in url for pattern in GOOD_PATTERNS)


def clean_location(location: str) -> str:
    """Remove non-ASCII characters and clean up location string."""
    if not location:
        return ""
    # Keep only ASCII characters
    cleaned = location.encode("ascii", "ignore").decode("ascii")
    # Remove empty parts but preserve meaningful ones
    parts = [part.strip() for part in cleaned.split(",") if part.strip()]
    return ", ".join(parts) if parts else ""


def clean_url(url: str) -> str:
    """Strip UTM and tracking params from URL."""
    tracking_params = [
        "utm_source", "utm_medium", "utm_campaign",
        "src", "source", "sourceType", "gh_src",
        "trk", "refId"
    ]
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    clean_params = {k: v for k, v in params.items() if k not in tracking_params}
    from urllib.parse import urlencode
    clean_query = urlencode({k: v[0] for k, v in clean_params.items()})
    return parsed._replace(query=clean_query).geturl()


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
                            url = clean_url(unquote(params["url"][0]))
                            print(f"     Method 2 (LinkedIn extraction): {url}")
                            return url
                except Exception:
                    continue
        except Exception:
            pass

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

    # Method 4 — try ALL remaining aggregator links and follow redirects
    for option in apply_options:
        link = option.get("link", "")
        if not link or "linkedin.com" in link or "ziprecruiter.com" in link:
            continue
        if not is_aggregator(link):
            continue
        try:
            await page.goto(link, wait_until="networkidle", timeout=15000)
            final_url = page.url

            # If we redirected to a non-aggregator page that's not the same domain
            if not is_aggregator(final_url) and urlparse(final_url).netloc != urlparse(link).netloc:
                print(f"     Method 4 (aggregator redirect): {clean_url(final_url)}")
                return clean_url(final_url)

            # Also check if there's an "Apply on company site" button on the page
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

    # Method 5 — Google Search fallback for jobs with no apply_options
    if not apply_options and title and company:
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
                if (link
                    and not is_aggregator(link)
                    and "linkedin.com" not in link
                    and "indeed.com" not in link
                    and "glassdoor.com" not in link):
                    print(f"     Method 5 (Google Search): {clean_url(link)}")
                    return clean_url(link)
        except Exception:
            pass

    return None


def fetch_google_jobs(query: str):
    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    if "error" in data:
        print(f"API Error: {data['error']}")
        return []

    return data.get("jobs_results", [])


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
            apply_options = job.get("apply_options", [])

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
    print("Fetching software engineer internships in North Carolina...\n")
    jobs = fetch_google_jobs("software engineer internship North Carolina")
    print(f"Found {len(jobs)} jobs from SerpAPI")

    asyncio.run(process_jobs(jobs))