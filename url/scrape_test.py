import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse, parse_qs, unquote, urlencode

# ─── Config ────────────────────────────────────────────────────────────────────

SEARCH_QUERIES = [
    ("entry level accountant", "North Carolina"),
    ("data analyst", "North Carolina"),
]

# ─── Helpers ───────────────────────────────────────────────────────────────────

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

# ─── Step 1: Scrape LinkedIn job listing URLs ──────────────────────────────────

async def get_linkedin_job_urls(page, keyword: str, location: str) -> list[str]:
    urls = []
    search_url = (
        f"https://www.linkedin.com/jobs/search"
        f"?keywords={keyword.replace(' ', '%20')}"
        f"&location={location.replace(' ', '%20')}"
        f"&f_TPR=r86400"
    )

    print(f"\n  🔍 Searching: {keyword} in {location}")

    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(3000)

        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 800)")
            await page.wait_for_timeout(1000)

        links = await page.query_selector_all("a")
        for link in links:
            try:
                href = await link.get_attribute("href")
                if href and "/jobs/view/" in href:
                    clean = "https://www.linkedin.com" + href.split("?")[0] if href.startswith("/") else href.split("?")[0]
                    if clean not in urls:
                        urls.append(clean)
            except Exception:
                continue

        print(f"     Found {len(urls)} job listing URLs")

    except Exception as e:
        print(f"     ❌ Search failed: {e}")

    return urls

# ─── Step 2: Extract direct apply URL from each LinkedIn job page ──────────────

async def extract_apply_url(page, linkedin_url: str) -> str | None:
    try:
        await page.goto(linkedin_url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2000)

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

    except Exception as e:
        print(f"     ❌ Extraction failed: {e}")

    return None

# ─── Main ──────────────────────────────────────────────────────────────────────

async def main():
    print("=" * 60)
    print("  ApplyR — LinkedIn Apply URL Scraper")
    print("=" * 60)

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

        for keyword, location in SEARCH_QUERIES:

            job_urls = await get_linkedin_job_urls(page, keyword, location)

            for job_url in job_urls:
                print(f"\n  📄 {job_url}")
                apply_url = await extract_apply_url(page, job_url)

                if apply_url:
                    print(f"  ✅ Apply URL: {apply_url}")
                    all_results.append({
                        "linkedin_url": job_url,
                        "apply_url": apply_url,
                    })
                else:
                    print(f"  ⚠️  No external apply URL found (LinkedIn Easy Apply only)")

        await browser.close()

    print("\n" + "=" * 60)
    print(f"  Done. Found {len(all_results)} direct apply URLs\n")
    for r in all_results:
        print(f"  {r['apply_url']}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())