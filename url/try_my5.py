import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://www.simplyhired.com/search?q=entry+level+accountant&l=north+carolina"

async def scrape_simplyhired_jobs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
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
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        print(f"Fetching: {URL}")
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)

        # Scroll to load more
        for _ in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

        jobs = await page.evaluate("""
            () => {
                const cards = document.querySelectorAll('div[data-jobkey]');

                return Array.from(cards).map(card => {
                    const titleEl   = card.querySelector('[data-testid="searchSerpJobTitle"]');
                    const companyEl = card.querySelector('[data-testid="companyName"]');
                    const locationEl = card.querySelector('[data-testid="searchSerpJobLocation"]');
                    const salaryEl  = card.querySelector('[data-testid="salaryChip-0"]');
                    const linkEl    = card.querySelector('a[data-testid="serpJobCompanyLink"]')
                                   || card.querySelector('a');

                    // Get the job link not the company link
                    const jobLinkEl = card.querySelector('h2 a')
                                   || card.querySelector('a[href*="/job/"]');

                    return {
                        title: titleEl?.innerText?.trim() || null,
                        company: companyEl?.innerText?.trim() || null,
                        location: locationEl?.innerText?.trim() || null,
                        salary: salaryEl?.innerText?.trim() || null,
                        simplyhired_url: jobLinkEl?.href || linkEl?.href || null,
                    };
                });
            }
        """)

        await browser.close()

        jobs = [j for j in jobs if j["title"] and j["company"]]

        seen = set()
        unique_jobs = []
        for job in jobs:
            key = (job["title"].lower(), job["company"].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        print(f"\nScraped {len(unique_jobs)} unique jobs\n")
        for job in unique_jobs:
            print(f"{job['title']} @ {job['company']}")
            print(f"  {job['location']} | {job['salary']}")
            print(f"  {job['simplyhired_url']}")
            print()

        with open("simplyhired_jobs.json", "w") as f:
            json.dump(unique_jobs, f, indent=2)

        return unique_jobs

if __name__ == "__main__":
    asyncio.run(scrape_simplyhired_jobs())