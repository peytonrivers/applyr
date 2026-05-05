import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse, parse_qs, unquote

TEST_URL = "https://www.linkedin.com/jobs/entry-level-business-analyst-jobs-north-carolina?position=1&pageNum=0"

async def run():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context()
        page    = await context.new_page()

        print(f"Navigating to: {TEST_URL}")
        await page.goto(TEST_URL, wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(3)

        # scroll to load listings
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

        print(f"Found {len(job_urls)} job listings")

        for job_url in job_urls:
            print(f"\n→ {job_url}")
            await page.goto(job_url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)

            # grab title + company while we're here
            title   = ""
            company = ""
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

            # find and click the Apply button — intercept the new tab it opens
            try:
                apply_url = None

                # listen for a new page (Apply opens in new tab)
                async with context.expect_page(timeout=5000) as new_page_info:
                    apply_btn = await page.query_selector("button.jobs-apply-button, a.jobs-apply-button")
                    if apply_btn:
                        await apply_btn.click()
                    else:
                        print(f"  ⚠️  No Apply button found")
                        continue

                new_page   = await new_page_info.value
                await new_page.wait_for_load_state("domcontentloaded", timeout=10000)
                apply_url  = new_page.url
                await new_page.close()

                print(f"  title:     {title}")
                print(f"  company:   {company}")
                print(f"  apply_url: {apply_url}")

            except Exception as e:
                print(f"  ❌ Could not get apply URL: {e}")
                continue

        await browser.close()

asyncio.run(run())