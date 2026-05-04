# LangGraph Agent to start the Application
"""
    1. Open the URL
    2. 404 error or Timeout
        - break & set the url to inactive
    3. Track Domain inside of url
    4. Find Apply Button
        - HTML Scraping
        - Looking for buttons as well
    5. Click Apply with playwright apply tool
        - If 404 Error or Timeout
            - break & set the url to inactive
        - If Not the same Domain
            - break & est the url to inactive
    6. Send to Recognition Tool
"""

"""
    1. Grab url and open it
"""

import asyncio 
from playwright.sync_api import sync_playwright, Playwright
from playwright.async_api import async_playwright

async def grab_and_open_url():
    # 1. Retrieve url
    url = "https://www.allstate.jobs/job/23127059/product-engineer-java-spring-boot-w-full-stack-option-remote-il/?source=LinkedInJB&utm_source=LILimitedListings&source=linkedinjobpostings"
    # 2. Open the url with playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
   