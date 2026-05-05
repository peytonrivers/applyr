import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://www.ziprecruiter.com/Jobs/Entry-Level-Accountant/--in-North-Carolina?lk=dYjNNTKDg1QXaejobhowZA"

async def scrape_ziprecruiter_jobs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
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

        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(8)

        # Scroll to load more
        for _ in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

        jobs = await page.evaluate("""
            () => {
                const cards = document.querySelectorAll('.job_result_two_pane_v2');

                return Array.from(cards).map(card => {
                    // Company: confirmed data-testid
                    const companyEl = card.querySelector('[data-testid="job-card-company"]');

                    // Title: find all anchors and pick the one that's not company
                    const titleEl = card.querySelector('[data-testid="job-card-title"]')
                                 || card.querySelector('h2 a')
                                 || card.querySelector('a[href*="/k/"]')
                                 || Array.from(card.querySelectorAll('a')).find(a => 
                                     a !== companyEl && a.innerText.length > 3
                                 );

                    // Location: look for common patterns
                    const locationEl = card.querySelector('[data-testid="job-card-location"]')
                                    || card.querySelector('[class*="location"]')
                                    || card.querySelector('address');

                    // Salary
                    const salaryEl = card.querySelector('[data-testid="job-card-salary"]')
                                  || card.querySelector('[class*="salary"]')
                                  || card.querySelector('[class*="compensation"]');

                    // Link: job apply URL
                    const linkEl = card.querySelector('a[href*="/k/"]')
                                || card.querySelector('a[href*="ziprecruiter.com/c/"]')
                                || titleEl;

                    return {
                        title: titleEl?.innerText?.trim() || null,
                        company: companyEl?.innerText?.trim() || null,
                        location: locationEl?.innerText?.trim() || null,
                        salary: salaryEl?.innerText?.trim() || null,
                        ziprecruiter_url: linkEl?.href || null,
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
            print(f"  {job['ziprecruiter_url']}")
            print()

        with open("ziprecruiter_jobs.json", "w") as f:
            json.dump(unique_jobs, f, indent=2)

        return unique_jobs

if __name__ == "__main__":
    asyncio.run(scrape_ziprecruiter_jobs())