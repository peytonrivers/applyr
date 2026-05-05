import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse, parse_qs, unquote

TEST_URL = "https://www.linkedin.com/jobs/entry-level-business-analyst-jobs-north-carolina?position=1&pageNum=0"

async def run():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        print(f"Navigating to: {TEST_URL}")
        await page.goto(TEST_URL, wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(3)

        for _ in range(2):
            await page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(1)

        # collect /jobs/view/ links
        job_urls = []
        for link in await page.query_selector_all("a"):
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
            except Exception:
                continue

        print(f"Found {len(job_urls)} job listings\n")

        for job_url in job_urls:
            print(f"→ {job_url}")
            await page.goto(job_url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)

            # grab title + company
            title   = ""
            company = ""
            try:
                el = await page.query_selector("h1")
                title = (await el.inner_text()).strip() if el else ""
            except Exception:
                pass
            try:
                el = await page.query_selector(".topcard__org-name-link, .sub-nav-cta__optional-url")
                company = (await el.inner_text()).strip() if el else ""
            except Exception:
                pass

            # extract apply URL from page HTML — it's always embedded even logged out
            apply_url = None

            # method 1: externalApply link in href
            for link in await page.query_selector_all("a[href*='externalApply']"):
                try:
                    href = await link.get_attribute("href")
                    params = parse_qs(urlparse(href).query)
                    if "url" in params:
                        apply_url = unquote(params["url"][0])
                        break
                except Exception:
                    continue

            # method 2: scan raw page source for the apply URL as fallback
            if not apply_url:
                try:
                    content = await page.content()
                    marker  = '"applyMethod":{"com.linkedin.voyager.jobs.OffsiteApply":{"url":"'
                    idx     = content.find(marker)
                    if idx != -1:
                        start     = idx + len(marker)
                        end       = content.find('"', start)
                        apply_url = content[start:end].replace("\\u0026", "&")
                except Exception:
                    pass

            print(f"  title:     {title}")
            print(f"  company:   {company}")
            print(f"  apply_url: {apply_url if apply_url else 'NOT FOUND'}\n")

        await browser.close()

asyncio.run(run())