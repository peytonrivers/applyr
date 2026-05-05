import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://www.glassdoor.com/Job/charlotte-entry-level-accounting-jobs-SRCH_IL.0,9_IC1138644_KO10,32.htm"

async def scrape_glassdoor_jobs():
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
        await asyncio.sleep(3)

        # Scroll to load more
        for _ in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

        jobs = await page.evaluate("""
            () => {
                const cards = document.querySelectorAll('[data-test="jobListing"]');
                return Array.from(cards).map(card => {
                    const titleEl = card.querySelector('[class*="JobCard_jobTitle"]')
                                 || card.querySelector('a[class*="jobTitle"]')
                                 || card.querySelector('[class*="job-title"]');

                    const companyEl = card.querySelector('[class*="EmployerProfile_employerName"]')
                                   || card.querySelector('[class*="jobEmpolyerName"]')
                                   || card.querySelector('[class*="employer-name"]')
                                   || card.querySelector('[class*="EmployerProfile"]');

                    const locationEl = card.querySelector('[class*="JobCard_location"]')
                                    || card.querySelector('[class*="job-location"]')
                                    || card.querySelector('[class*="location"]');

                    const salaryEl = card.querySelector('[class*="JobCard_salaryEstimate"]')
                                  || card.querySelector('[class*="salary"]');

                    const linkEl = card.querySelector('a[class*="JobCard_jobTitle"]')
                                || card.querySelector('a[href*="/job-listing/"]')
                                || card.querySelector('a[href*="glassdoor.com/job"]')
                                || card.querySelector('a[href*="GD_JOB"]');

                    const dateEl = card.querySelector('[class*="JobCard_listingAge"]')
                                || card.querySelector('[class*="listing-age"]')
                                || card.querySelector('[class*="age"]');

                    // FIX 1: use .href directly instead of prepending base URL
                    const rawHref = linkEl?.href || null;

                    // FIX 2: use only the first text node to avoid rating bleeding in
                    const companyName = companyEl
                        ? (companyEl.childNodes[0]?.textContent?.trim() || companyEl.innerText?.trim())
                        : null;

                    return {
                        title: titleEl?.innerText?.trim() || null,
                        company: companyName,
                        location: locationEl?.innerText?.trim() || null,
                        salary: salaryEl?.innerText?.trim() || null,
                        posted_date: dateEl?.innerText?.trim() || null,
                        glassdoor_url: rawHref,
                    };
                });
            }
        """)

        await browser.close()

        # Filter nulls
        jobs = [j for j in jobs if j["title"] and j["company"]]

        # Deduplicate by title + company
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
            print(f"  {job['location']} | {job['posted_date']} | {job['salary']}")
            print(f"  {job['glassdoor_url']}")
            print()

        with open("glassdoor_jobs.json", "w") as f:
            json.dump(unique_jobs, f, indent=2)

        return unique_jobs

if __name__ == "__main__":
    asyncio.run(scrape_glassdoor_jobs())