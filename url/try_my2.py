import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://www.linkedin.com/jobs/search?keywords=staff%20accountant&location=North%20Carolina&geoId=103255397&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"

async def scrape_linkedin_jobs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ]
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

        # Mask webdriver flag
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        print(f"Fetching: {URL}")
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)

        # Wait for job cards to appear
        await page.wait_for_selector("ul.jobs-search__results-list", timeout=15000)

        # Scroll to load more jobs
        for _ in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

        # Extract job cards
        jobs = await page.evaluate("""
            () => {
                const cards = document.querySelectorAll("ul.jobs-search__results-list li");
                return Array.from(cards).map(card => {
                    const titleEl = card.querySelector(".base-search-card__title");
                    const companyEl = card.querySelector(".base-search-card__subtitle");
                    const locationEl = card.querySelector(".job-search-card__location");
                    const linkEl = card.querySelector("a.base-card__full-link");
                    const dateEl = card.querySelector("time");

                    return {
                        title: titleEl?.innerText?.trim() || null,
                        company: companyEl?.innerText?.trim() || null,
                        location: locationEl?.innerText?.trim() || null,
                        linkedin_url: linkEl?.href || null,
                        posted_date: dateEl?.getAttribute("datetime") || null,
                    };
                });
            }
        """)

        await browser.close()

        # Filter out nulls
        jobs = [j for j in jobs if j["title"] and j["company"]]

        print(f"\nScraped {len(jobs)} jobs\n")
        for job in jobs:
            print(f"{job['title']} @ {job['company']}")
            print(f"  {job['location']} | {job['posted_date']}")
            print(f"  {job['linkedin_url']}")
            print()

        with open("linkedin_jobs.json", "w") as f:
            json.dump(jobs, f, indent=2)

        return jobs

if __name__ == "__main__":
    asyncio.run(scrape_linkedin_jobs())